import json
from pathlib import Path

from fastapi.testclient import TestClient


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "lightshell_inventory.pdf"
)


def create_test_product(
    client: TestClient,
    *,
    name: str,
) -> dict:
    response = client.post(
        "/products",
        json={
            "name": name,
            "price": 100,
            "unit": "шт.",
            "minimum_stock": 0,
            "lightshell_id": None,
        },
    )

    assert response.status_code == 201

    return response.json()


def build_resolutions(
    *,
    first_action: str,
    first_product_id: str | None = None,
) -> list[dict]:
    resolutions = [
        {
            "source_number": 1,
            "action": first_action,
            "product_id": first_product_id,
        }
    ]

    resolutions.extend(
        {
            "source_number": source_number,
            "action": "skip",
            "product_id": None,
        }
        for source_number in range(2, 82)
    )

    return resolutions


def test_preview_lightshell_import(
    client: TestClient,
) -> None:
    product = create_test_product(
        client,
        name=(
            "Горячая кружка Магги "
            "со стаканчиком"
        ),
    )

    with FIXTURE_PATH.open("rb") as pdf_file:
        response = client.post(
            "/lightshell-imports/preview",
            files={
                "file": (
                    "lightshell_inventory.pdf",
                    pdf_file,
                    "application/pdf",
                ),
            },
        )

    assert response.status_code == 200

    preview = response.json()

    assert preview["branch"] == "#1"
    assert preview["source_filename"] == (
        "lightshell_inventory.pdf"
    )
    assert preview["total_items"] == 81
    assert preview["matched_items"] == 1
    assert preview["unmatched_items"] == 80
    assert preview["ambiguous_items"] == 0

    first_item = preview["items"][0]

    assert first_item["source_number"] == 1
    assert first_item["status"] == "exact"
    assert first_item["product_id"] == product["id"]
    assert first_item["product_name"] == product["name"]


def test_preview_rejects_non_pdf_file(
    client: TestClient,
) -> None:
    response = client.post(
        "/lightshell-imports/preview",
        files={
            "file": (
                "inventory.txt",
                b"not a pdf",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Можно загрузить только PDF-файл."
    )


def test_preview_rejects_empty_pdf(
    client: TestClient,
) -> None:
    response = client.post(
        "/lightshell-imports/preview",
        files={
            "file": (
                "inventory.pdf",
                b"",
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Загруженный PDF пуст."
    )


def test_apply_updates_only_program_quantity(
    client: TestClient,
) -> None:
    product = create_test_product(
        client,
        name=(
            "Горячая кружка Магги "
            "со стаканчиком"
        ),
    )

    balance_response = client.patch(
        f"/inventory-balances/{product['id']}",
        json={
            "program_quantity": 99,
            "actual_quantity": 7,
        },
    )

    assert balance_response.status_code == 200

    resolutions = build_resolutions(
        first_action="use_existing",
        first_product_id=product["id"],
    )

    with FIXTURE_PATH.open("rb") as pdf_file:
        response = client.post(
            "/lightshell-imports/apply",
            files={
                "file": (
                    "lightshell_inventory.pdf",
                    pdf_file,
                    "application/pdf",
                ),
            },
            data={
                "resolutions_json": json.dumps(
                    resolutions
                ),
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert result["total_items"] == 81
    assert result["updated_items"] == 1
    assert result["created_products"] == 0
    assert result["skipped_items"] == 80
    assert result["created_mappings"] == 1

    updated_balance_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert updated_balance_response.status_code == 200

    updated_balance = updated_balance_response.json()

    assert updated_balance["program_quantity"] == "4.000"
    assert updated_balance["actual_quantity"] == "7.000"

    with FIXTURE_PATH.open("rb") as pdf_file:
        preview_response = client.post(
            "/lightshell-imports/preview",
            files={
                "file": (
                    "lightshell_inventory.pdf",
                    pdf_file,
                    "application/pdf",
                ),
            },
        )

    assert preview_response.status_code == 200
    assert (
        preview_response.json()["items"][0]["status"]
        == "mapped"
    )


def test_apply_creates_new_product(
    client: TestClient,
) -> None:
    resolutions = build_resolutions(
        first_action="create_new",
    )

    with FIXTURE_PATH.open("rb") as pdf_file:
        response = client.post(
            "/lightshell-imports/apply",
            files={
                "file": (
                    "lightshell_inventory.pdf",
                    pdf_file,
                    "application/pdf",
                ),
            },
            data={
                "resolutions_json": json.dumps(
                    resolutions
                ),
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert result["updated_items"] == 1
    assert result["created_products"] == 1
    assert result["skipped_items"] == 80
    assert result["created_mappings"] == 1

    products_response = client.get(
        "/products"
    )

    assert products_response.status_code == 200

    products = products_response.json()

    assert len(products) == 1

    product = products[0]

    assert product["name"] == (
        "Горячая кружка Магги со стаканчиком"
    )
    assert product["price"] == "0.00"

    balance_response = client.get(
        f"/inventory-balances/{product['id']}"
    )

    assert balance_response.status_code == 200

    balance = balance_response.json()

    assert balance["program_quantity"] == "4.000"
    assert balance["actual_quantity"] == "0.000"


def test_apply_rejects_missing_resolutions(
    client: TestClient,
) -> None:
    incomplete_resolutions = [
        {
            "source_number": 1,
            "action": "skip",
            "product_id": None,
        }
    ]

    with FIXTURE_PATH.open("rb") as pdf_file:
        response = client.post(
            "/lightshell-imports/apply",
            files={
                "file": (
                    "lightshell_inventory.pdf",
                    pdf_file,
                    "application/pdf",
                ),
            },
            data={
                "resolutions_json": json.dumps(
                    incomplete_resolutions
                ),
            },
        )

    assert response.status_code == 422
    assert response.json()["detail"].startswith(
        "Не указано решение для позиций:"
    )