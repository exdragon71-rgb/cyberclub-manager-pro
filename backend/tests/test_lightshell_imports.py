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