from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient


def create_employee(
    client: TestClient,
    *,
    name: str = "Роман",
) -> dict:
    response = client.post(
        "/employees",
        json={
            "name": name,
        },
    )

    assert response.status_code == 201

    return response.json()


def create_product(
    client: TestClient,
    *,
    name: str = "Lipton Лимон 0,5",
    price: int = 130,
) -> dict:
    response = client.post(
        "/products",
        json={
            "name": name,
            "price": price,
            "unit": "шт.",
            "minimum_stock": 3,
            "lightshell_id": None,
        },
    )

    assert response.status_code == 201

    return response.json()


def create_debt(
    client: TestClient,
    *,
    employee_id: str,
    product_id: str,
    quantity: int = 1,
    note: str | None = None,
) -> dict:
    response = client.post(
        "/debts",
        json={
            "employee_id": employee_id,
            "product_id": product_id,
            "quantity": quantity,
            "note": note,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_debt(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=2,
        note="До зарплаты",
    )

    assert debt["employee_id"] == employee["id"]
    assert debt["product_id"] == product["id"]

    assert Decimal(
        debt["quantity"]
    ) == Decimal("2")

    assert Decimal(
        debt["unit_price"]
    ) == Decimal("130")

    assert Decimal(
        debt["total_amount"]
    ) == Decimal("260")

    assert debt["status"] == "active"
    assert debt["note"] == "До зарплаты"
    assert debt["paid_at"] is None

    assert debt["employee"]["name"] == "Роман"

    assert debt["product"]["name"] == (
        "Lipton Лимон 0,5"
    )


def test_create_debt_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=2,
        note="До зарплаты",
    )

    response = client.get(
        "/action-logs",
        params={
            "event_type": "debt_created",
            "entity_type": "debt",
        },
    )

    assert response.status_code == 200

    action_logs = response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == debt["id"]

    assert action_log["message"] == (
        "Добавлен долг сотрудника «Роман» "
        "за товар «Lipton Лимон 0,5»."
    )

    assert action_log["details"]["employee_name"] == (
        "Роман"
    )

    assert action_log["details"]["product_name"] == (
        "Lipton Лимон 0,5"
    )

    assert Decimal(
        action_log["details"]["quantity"]
    ) == Decimal("2")

    assert Decimal(
        action_log["details"]["total_amount"]
    ) == Decimal("260")

    assert action_log["details"]["status"] == "active"

    assert action_log["details"]["note"] == (
        "До зарплаты"
    )


def test_debt_creation_does_not_change_inventory(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    update_response = client.patch(
        f"/inventory-balances/{product['id']}",
        json={
            "program_quantity": 18,
            "actual_quantity": 17,
        },
    )

    assert update_response.status_code == 200

    create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
    )

    balance_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert balance_response.status_code == 200

    balance = balance_response.json()

    assert Decimal(
        balance["program_quantity"]
    ) == Decimal("18")

    assert Decimal(
        balance["actual_quantity"]
    ) == Decimal("17")


def test_debt_keeps_original_product_price(
    client: TestClient,
) -> None:
    employee = create_employee(client)

    product = create_product(
        client,
        price=130,
    )

    debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
    )

    product_update_response = client.patch(
        f"/products/{product['id']}",
        json={
            "price": 180,
        },
    )

    assert product_update_response.status_code == 200

    debt_response = client.get(
        f"/debts/{debt['id']}"
    )

    assert debt_response.status_code == 200

    loaded_debt = debt_response.json()

    assert Decimal(
        loaded_debt["unit_price"]
    ) == Decimal("130")


def test_update_active_debt(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
    )

    response = client.patch(
        f"/debts/{debt['id']}",
        json={
            "quantity": 3,
            "note": "Три бутылки",
        },
    )

    assert response.status_code == 200

    updated_debt = response.json()

    assert Decimal(
        updated_debt["quantity"]
    ) == Decimal("3")

    assert updated_debt["note"] == "Три бутылки"


def test_update_debt_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
        note="Одна бутылка",
    )

    response = client.patch(
        f"/debts/{debt['id']}",
        json={
            "quantity": 3,
            "note": "Три бутылки",
        },
    )

    assert response.status_code == 200

    logs_response = client.get(
        "/action-logs",
        params={
            "event_type": "debt_updated",
            "entity_type": "debt",
        },
    )

    assert logs_response.status_code == 200

    action_logs = logs_response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == debt["id"]

    assert action_log["message"] == (
        "Изменён долг сотрудника «Роман» "
        "за товар «Lipton Лимон 0,5»."
    )

    assert Decimal(
        action_log["details"]["before"]["quantity"]
    ) == Decimal("1")

    assert (
        action_log["details"]["before"]["note"]
        == "Одна бутылка"
    )

    assert Decimal(
        action_log["details"]["after"]["quantity"]
    ) == Decimal("3")

    assert (
        action_log["details"]["after"]["note"]
        == "Три бутылки"
    )


def test_pay_debt_reduces_program_quantity(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    balance_response = client.patch(
        f"/inventory-balances/{product['id']}",
        json={
            "program_quantity": 18,
            "actual_quantity": 17,
        },
    )

    assert balance_response.status_code == 200

    debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
    )

    pay_response = client.post(
        f"/debts/{debt['id']}/pay"
    )

    assert pay_response.status_code == 200

    paid_debt = pay_response.json()

    assert paid_debt["status"] == "paid"
    assert paid_debt["paid_at"] is not None

    updated_balance_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert updated_balance_response.status_code == 200

    updated_balance = updated_balance_response.json()

    assert Decimal(
        updated_balance["program_quantity"]
    ) == Decimal("17")

    assert Decimal(
        updated_balance["actual_quantity"]
    ) == Decimal("17")


def test_pay_debt_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    balance_response = client.patch(
        f"/inventory-balances/{product['id']}",
        json={
            "program_quantity": 18,
            "actual_quantity": 17,
        },
    )

    assert balance_response.status_code == 200

    debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
        note="До зарплаты",
    )

    pay_response = client.post(
        f"/debts/{debt['id']}/pay"
    )

    assert pay_response.status_code == 200

    logs_response = client.get(
        "/action-logs",
        params={
            "event_type": "debt_paid",
            "entity_type": "debt",
        },
    )

    assert logs_response.status_code == 200

    action_logs = logs_response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == debt["id"]

    assert action_log["message"] == (
        "Погашен долг сотрудника «Роман» "
        "за товар «Lipton Лимон 0,5»."
    )

    assert action_log["details"]["status"] == "paid"

    assert Decimal(
        action_log["details"][
            "program_quantity_before"
        ]
    ) == Decimal("18")

    assert Decimal(
        action_log["details"][
            "program_quantity_after"
        ]
    ) == Decimal("17")

    assert action_log["details"]["paid_at"] is not None


def test_paying_debt_twice_does_not_reduce_stock_twice(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    balance_response = client.patch(
        f"/inventory-balances/{product['id']}",
        json={
            "program_quantity": 10,
            "actual_quantity": 9,
        },
    )

    assert balance_response.status_code == 200

    debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
    )

    first_pay_response = client.post(
        f"/debts/{debt['id']}/pay"
    )

    assert first_pay_response.status_code == 200

    second_pay_response = client.post(
        f"/debts/{debt['id']}/pay"
    )

    assert second_pay_response.status_code == 200

    balance_after_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert balance_after_response.status_code == 200

    balance_after = balance_after_response.json()

    assert Decimal(
        balance_after["program_quantity"]
    ) == Decimal("9")


def test_paid_debt_cannot_be_updated(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
    )

    pay_response = client.post(
        f"/debts/{debt['id']}/pay"
    )

    assert pay_response.status_code == 200

    update_response = client.patch(
        f"/debts/{debt['id']}",
        json={
            "quantity": 2,
        },
    )

    assert update_response.status_code == 422

    assert update_response.json()["detail"] == (
        "Погашенный долг нельзя изменить."
    )


def test_filter_debts_by_status(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    active_debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
    )

    paid_debt = create_debt(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
    )

    pay_response = client.post(
        f"/debts/{paid_debt['id']}/pay"
    )

    assert pay_response.status_code == 200

    active_response = client.get(
        "/debts",
        params={
            "status": "active",
        },
    )

    assert active_response.status_code == 200
    assert len(active_response.json()) == 1

    assert active_response.json()[0]["id"] == (
        active_debt["id"]
    )

    paid_response = client.get(
        "/debts",
        params={
            "status": "paid",
        },
    )

    assert paid_response.status_code == 200
    assert len(paid_response.json()) == 1

    assert paid_response.json()[0]["id"] == (
        paid_debt["id"]
    )


def test_unknown_debt_returns_404(
    client: TestClient,
) -> None:
    unknown_debt_id = uuid4()

    response = client.get(
        f"/debts/{unknown_debt_id}"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Долг не найден."
    )