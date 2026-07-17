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


def create_prize(
    client: TestClient,
    *,
    employee_id: str,
    product_id: str,
    quantity: int = 1,
    note: str | None = None,
) -> dict:
    response = client.post(
        "/prizes",
        json={
            "employee_id": employee_id,
            "product_id": product_id,
            "quantity": quantity,
            "note": note,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_prize(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
        note="Один выигранный напиток",
    )

    assert prize["employee_id"] == employee["id"]
    assert prize["product_id"] == product["id"]

    assert Decimal(
        prize["quantity"]
    ) == Decimal("1")

    assert Decimal(
        prize["ticket_price"]
    ) == Decimal("85.00")

    assert prize["status"] == "active"

    assert prize["note"] == (
        "Один выигранный напиток"
    )

    assert prize["written_off_at"] is None

    assert prize["employee"]["name"] == "Роман"

    assert prize["product"]["name"] == (
        "Lipton Лимон 0,5"
    )


def test_create_prize_uses_current_ticket_price(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    settings_response = client.patch(
        "/club-settings",
        json={
            "lottery_ticket_price": 100,
        },
    )

    assert settings_response.status_code == 200

    prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
    )

    assert Decimal(
        prize["ticket_price"]
    ) == Decimal("100.00")

    second_settings_response = client.patch(
        "/club-settings",
        json={
            "lottery_ticket_price": 120,
        },
    )

    assert second_settings_response.status_code == 200

    prize_response = client.get(
        f"/prizes/{prize['id']}"
    )

    assert prize_response.status_code == 200

    stored_prize = prize_response.json()

    assert Decimal(
        stored_prize["ticket_price"]
    ) == Decimal("100.00")


def test_create_prize_rejects_quantity_not_one(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    response = client.post(
        "/prizes",
        json={
            "employee_id": employee["id"],
            "product_id": product["id"],
            "quantity": 2,
            "note": None,
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "Одна запись должна "
        "соответствовать одной "
        "лотерейке и одному призу. "
        "Количество должно быть равно 1."
    )


def test_create_prize_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
        note="Один выигранный напиток",
    )

    response = client.get(
        "/action-logs",
        params={
            "event_type": "prize_created",
            "entity_type": "prize",
        },
    )

    assert response.status_code == 200

    action_logs = response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == prize["id"]

    assert action_log["message"] == (
        "Выдан лотерейный приз "
        "«Lipton Лимон 0,5». "
        "Сотрудник: «Роман»."
    )

    assert action_log["details"]["employee_name"] == (
        "Роман"
    )

    assert action_log["details"]["product_name"] == (
        "Lipton Лимон 0,5"
    )

    assert Decimal(
        action_log["details"]["quantity"]
    ) == Decimal("1")

    assert Decimal(
        action_log["details"]["ticket_price"]
    ) == Decimal("85.00")

    assert action_log["details"]["status"] == "active"

    assert action_log["details"]["note"] == (
        "Один выигранный напиток"
    )


def test_get_prizes(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    first_prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
    )

    second_prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
    )

    response = client.get(
        "/prizes",
        params={
            "status": "active",
        },
    )

    assert response.status_code == 200

    prizes = response.json()

    assert len(prizes) == 2

    prize_ids = {
        prize["id"]
        for prize in prizes
    }

    assert first_prize["id"] in prize_ids
    assert second_prize["id"] in prize_ids

    for prize in prizes:
        assert Decimal(
            prize["ticket_price"]
        ) == Decimal("85.00")


def test_prize_does_not_change_inventory(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    update_response = client.patch(
        f"/inventory-balances/{product['id']}",
        json={
            "program_quantity": 13,
            "actual_quantity": 12,
        },
    )

    assert update_response.status_code == 200

    create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
    )

    balance_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert balance_response.status_code == 200

    balance = balance_response.json()

    assert Decimal(
        balance["program_quantity"]
    ) == Decimal("13")

    assert Decimal(
        balance["actual_quantity"]
    ) == Decimal("12")

    assert Decimal(
        balance["active_prize_quantity"]
    ) == Decimal("1")


def test_update_prize_changes_note(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
    )

    response = client.patch(
        f"/prizes/{prize['id']}",
        json={
            "note": "Исправленное примечание",
        },
    )

    assert response.status_code == 200

    updated_prize = response.json()

    assert Decimal(
        updated_prize["quantity"]
    ) == Decimal("1")

    assert updated_prize["note"] == (
        "Исправленное примечание"
    )

    balance_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert balance_response.status_code == 200

    balance = balance_response.json()

    assert Decimal(
        balance["active_prize_quantity"]
    ) == Decimal("1")


def test_update_prize_rejects_quantity_not_one(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
    )

    response = client.patch(
        f"/prizes/{prize['id']}",
        json={
            "quantity": 3,
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "Количество приза "
        "должно быть равно 1."
    )


def test_update_prize_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
        note="Приз выдан",
    )

    response = client.patch(
        f"/prizes/{prize['id']}",
        json={
            "note": "Примечание исправлено",
        },
    )

    assert response.status_code == 200

    logs_response = client.get(
        "/action-logs",
        params={
            "event_type": "prize_updated",
            "entity_type": "prize",
        },
    )

    assert logs_response.status_code == 200

    action_logs = logs_response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == prize["id"]

    assert action_log["message"] == (
        "Изменена запись лотерейного приза "
        "«Lipton Лимон 0,5». "
        "Сотрудник: «Роман»."
    )

    assert Decimal(
        action_log["details"]["before"]["quantity"]
    ) == Decimal("1")

    assert Decimal(
        action_log["details"]["before"]["ticket_price"]
    ) == Decimal("85.00")

    assert (
        action_log["details"]["before"]["note"]
        == "Приз выдан"
    )

    assert Decimal(
        action_log["details"]["after"]["quantity"]
    ) == Decimal("1")

    assert Decimal(
        action_log["details"]["after"]["ticket_price"]
    ) == Decimal("85.00")

    assert (
        action_log["details"]["after"]["note"]
        == "Примечание исправлено"
    )


def test_confirm_prize_reflected(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    update_response = client.patch(
        f"/inventory-balances/{product['id']}",
        json={
            "program_quantity": 12,
            "actual_quantity": 12,
        },
    )

    assert update_response.status_code == 200

    prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
    )

    response = client.post(
        f"/prizes/{prize['id']}/confirm-reflected"
    )

    assert response.status_code == 200

    confirmed_prize = response.json()

    assert confirmed_prize["status"] == "written_off"

    assert confirmed_prize["written_off_at"] is not None

    balance_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert balance_response.status_code == 200

    balance = balance_response.json()

    assert Decimal(
        balance["program_quantity"]
    ) == Decimal("12")

    assert Decimal(
        balance["actual_quantity"]
    ) == Decimal("12")

    assert Decimal(
        balance["active_prize_quantity"]
    ) == Decimal("0")


def test_confirm_prize_reflected_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
        note="Приз выдан",
    )

    response = client.post(
        f"/prizes/{prize['id']}/confirm-reflected"
    )

    assert response.status_code == 200

    logs_response = client.get(
        "/action-logs",
        params={
            "event_type": "prize_reflected",
            "entity_type": "prize",
        },
    )

    assert logs_response.status_code == 200

    action_logs = logs_response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == prize["id"]

    assert action_log["message"] == (
        "Подтверждён учёт лотерейного приза "
        "«Lipton Лимон 0,5» в LightShell."
    )

    assert action_log["details"]["status"] == (
        "written_off"
    )

    assert Decimal(
        action_log["details"]["ticket_price"]
    ) == Decimal("85.00")

    assert action_log["details"]["written_off_at"] is not None

    assert action_log["details"]["employee_name"] == (
        "Роман"
    )

    assert action_log["details"]["product_name"] == (
        "Lipton Лимон 0,5"
    )


def test_confirm_prize_reflected_twice_returns_422(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    prize = create_prize(
        client,
        employee_id=employee["id"],
        product_id=product["id"],
        quantity=1,
    )

    first_response = client.post(
        f"/prizes/{prize['id']}/confirm-reflected"
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/prizes/{prize['id']}/confirm-reflected"
    )

    assert second_response.status_code == 422

    assert second_response.json()["detail"] == (
        "Приз уже учтён в LightShell."
    )


def test_archived_employee_cannot_receive_prize(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    archive_response = client.post(
        f"/employees/{employee['id']}/archive"
    )

    assert archive_response.status_code == 200

    response = client.post(
        "/prizes",
        json={
            "employee_id": employee["id"],
            "product_id": product["id"],
            "quantity": 1,
            "note": None,
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "Нельзя оформить приз "
        "на сотрудника из архива."
    )


def test_archived_product_cannot_be_prize(
    client: TestClient,
) -> None:
    employee = create_employee(client)
    product = create_product(client)

    archive_response = client.post(
        f"/products/{product['id']}/archive"
    )

    assert archive_response.status_code == 200

    response = client.post(
        "/prizes",
        json={
            "employee_id": employee["id"],
            "product_id": product["id"],
            "quantity": 1,
            "note": None,
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "Нельзя оформить приз "
        "на товар из архива."
    )


def test_unknown_prize_returns_404(
    client: TestClient,
) -> None:
    unknown_prize_id = uuid4()

    response = client.get(
        f"/prizes/{unknown_prize_id}"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Приз не найден."
    )