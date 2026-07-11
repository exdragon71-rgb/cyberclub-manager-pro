from fastapi.testclient import TestClient


def create_test_product(
    client: TestClient,
    *,
    name: str = "Lipton Лимон 0,5",
    price: float = 130,
    minimum_stock: float = 5,
    lightshell_id: str | None = None,
) -> dict:
    response = client.post(
        "/products",
        json={
            "name": name,
            "price": price,
            "unit": "шт.",
            "minimum_stock": minimum_stock,
            "lightshell_id": lightshell_id,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_product(
    client: TestClient,
) -> None:
    product = create_test_product(
        client,
        name="Lipton Лимон 0,5",
        price=130,
        minimum_stock=5,
        lightshell_id="lightshell-lipton-lemon",
    )

    assert product["name"] == "Lipton Лимон 0,5"
    assert product["price"] == "130.00"
    assert product["unit"] == "шт."
    assert product["minimum_stock"] == "5.000"
    assert product["lightshell_id"] == "lightshell-lipton-lemon"
    assert product["is_active"] is True
    assert product["id"]


def test_get_products(
    client: TestClient,
) -> None:
    create_test_product(
        client,
        name="Lipton Лимон 0,5",
    )

    create_test_product(
        client,
        name="VIPS Лимонад 0,5",
        price=110,
    )

    response = client.get(
        "/products"
    )

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 2

    product_names = [
        product["name"]
        for product in products
    ]

    assert "Lipton Лимон 0,5" in product_names
    assert "VIPS Лимонад 0,5" in product_names


def test_get_product_by_id(
    client: TestClient,
) -> None:
    created_product = create_test_product(
        client
    )

    product_id = created_product["id"]

    response = client.get(
        f"/products/{product_id}"
    )

    assert response.status_code == 200

    product = response.json()

    assert product["id"] == product_id
    assert product["name"] == "Lipton Лимон 0,5"


def test_update_product(
    client: TestClient,
) -> None:
    created_product = create_test_product(
        client
    )

    product_id = created_product["id"]

    response = client.patch(
        f"/products/{product_id}",
        json={
            "name": "Lipton Лимон 0,5 обновлённый",
            "price": 150,
            "minimum_stock": 10,
        },
    )

    assert response.status_code == 200

    updated_product = response.json()

    assert (
        updated_product["name"]
        == "Lipton Лимон 0,5 обновлённый"
    )
    assert updated_product["price"] == "150.00"
    assert updated_product["minimum_stock"] == "10.000"


def test_archive_product(
    client: TestClient,
) -> None:
    created_product = create_test_product(
        client
    )

    product_id = created_product["id"]

    archive_response = client.post(
        f"/products/{product_id}/archive"
    )

    assert archive_response.status_code == 200
    assert archive_response.json()["is_active"] is False

    active_products_response = client.get(
        "/products",
        params={
            "include_inactive": False,
        },
    )

    assert active_products_response.status_code == 200
    assert active_products_response.json() == []

    all_products_response = client.get(
        "/products",
        params={
            "include_inactive": True,
        },
    )

    assert all_products_response.status_code == 200
    assert len(all_products_response.json()) == 1
    assert (
        all_products_response.json()[0]["is_active"]
        is False
    )


def test_restore_product(
    client: TestClient,
) -> None:
    created_product = create_test_product(
        client
    )

    product_id = created_product["id"]

    client.post(
        f"/products/{product_id}/archive"
    )

    restore_response = client.post(
        f"/products/{product_id}/restore"
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["is_active"] is True

    active_products_response = client.get(
        "/products"
    )

    assert active_products_response.status_code == 200
    assert len(active_products_response.json()) == 1


def test_duplicate_product_name_returns_conflict(
    client: TestClient,
) -> None:
    create_test_product(
        client,
        name="Lipton Лимон 0,5",
    )

    duplicate_response = client.post(
        "/products",
        json={
            "name": "Lipton Лимон 0,5",
            "price": 130,
            "unit": "шт.",
            "minimum_stock": 5,
            "lightshell_id": None,
        },
    )

    assert duplicate_response.status_code == 409


def test_duplicate_lightshell_id_returns_conflict(
    client: TestClient,
) -> None:
    create_test_product(
        client,
        name="Первый товар",
        lightshell_id="same-lightshell-id",
    )

    duplicate_response = client.post(
        "/products",
        json={
            "name": "Второй товар",
            "price": 200,
            "unit": "шт.",
            "minimum_stock": 0,
            "lightshell_id": "same-lightshell-id",
        },
    )

    assert duplicate_response.status_code == 409


def test_unknown_product_returns_404(
    client: TestClient,
) -> None:
    response = client.get(
        "/products/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404