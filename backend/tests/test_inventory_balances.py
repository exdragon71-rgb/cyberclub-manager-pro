from uuid import uuid4

from fastapi.testclient import TestClient


def create_product(
    client: TestClient,
    *,
    name: str = "Тестовый товар",
) -> dict:
    response = client.post(
        "/products",
        json={
            "name": name,
            "price": 150,
            "unit": "шт.",
            "minimum_stock": 3,
            "lightshell_id": None,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_product_creation_creates_inventory_balance(
    client: TestClient,
) -> None:
    product = create_product(client)

    response = client.get(
        "/inventory-balances"
    )

    assert response.status_code == 200

    balances = response.json()

    assert len(balances) == 1
    assert balances[0]["product_id"] == product["id"]
    assert balances[0]["program_quantity"] == "0.000"
    assert balances[0]["actual_quantity"] == "0.000"
    assert balances[0]["product"]["name"] == (
        "Тестовый товар"
    )


def test_get_inventory_balance_by_product_id(
    client: TestClient,
) -> None:
    product = create_product(client)

    response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert response.status_code == 200

    balance = response.json()

    assert balance["product_id"] == product["id"]
    assert balance["product"]["id"] == product["id"]


def test_update_inventory_balance(
    client: TestClient,
) -> None:
    product = create_product(client)

    response = client.patch(
        f"/inventory-balances/{product['id']}",
        json={
            "program_quantity": 12,
            "actual_quantity": 10,
        },
    )

    assert response.status_code == 200

    balance = response.json()

    assert balance["program_quantity"] == "12.000"
    assert balance["actual_quantity"] == "10.000"


def test_inactive_products_can_be_included(
    client: TestClient,
) -> None:
    product = create_product(client)

    archive_response = client.post(
        f"/products/{product['id']}/archive"
    )

    assert archive_response.status_code == 200

    active_response = client.get(
        "/inventory-balances"
    )

    assert active_response.status_code == 200
    assert active_response.json() == []

    all_response = client.get(
        "/inventory-balances",
        params={
            "include_inactive": True,
        },
    )

    assert all_response.status_code == 200
    assert len(all_response.json()) == 1


def test_unknown_inventory_balance_returns_404(
    client: TestClient,
) -> None:
    unknown_product_id = uuid4()

    response = client.get(
        f"/inventory-balances/{unknown_product_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Остатки для товара не найдены."
    )