from decimal import Decimal

from fastapi.testclient import TestClient


def test_inventory_reports_active_debt_quantity(
    client: TestClient,
) -> None:
    employee_response = client.post(
        "/employees",
        json={
            "name": "Роман",
        },
    )

    assert employee_response.status_code == 201
    employee = employee_response.json()

    product_response = client.post(
        "/products",
        json={
            "name": "HQD 0,45 в ассортименте",
            "price": 180,
            "unit": "шт.",
            "minimum_stock": 3,
            "lightshell_id": None,
        },
    )

    assert product_response.status_code == 201
    product = product_response.json()

    balance_response = client.patch(
        f"/inventory-balances/{product['id']}",
        json={
            "program_quantity": 9,
            "actual_quantity": 8,
        },
    )

    assert balance_response.status_code == 200

    debt_response = client.post(
        "/debts",
        json={
            "employee_id": employee["id"],
            "product_id": product["id"],
            "quantity": 1,
            "note": None,
        },
    )

    assert debt_response.status_code == 201
    debt = debt_response.json()

    active_balance_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert active_balance_response.status_code == 200

    active_balance = active_balance_response.json()

    assert Decimal(
        active_balance["active_debt_quantity"]
    ) == Decimal("1")

    pay_response = client.post(
        f"/debts/{debt['id']}/pay"
    )

    assert pay_response.status_code == 200

    paid_balance_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert paid_balance_response.status_code == 200

    paid_balance = paid_balance_response.json()

    assert Decimal(
        paid_balance["active_debt_quantity"]
    ) == Decimal("0")

    assert Decimal(
        paid_balance["program_quantity"]
    ) == Decimal("8")