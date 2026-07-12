from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from app.integrations.lightshell.pdf_parser import (
    LightShellPdfParseError,
    parse_lightshell_inventory_pdf,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "lightshell_inventory.pdf"
)


def test_parse_lightshell_inventory_pdf() -> None:
    file_content = FIXTURE_PATH.read_bytes()

    document = parse_lightshell_inventory_pdf(
        file_content
    )

    assert document.branch == "#1"

    assert document.generated_at == datetime(
        2026,
        7,
        12,
        9,
        54,
        59,
    )

    assert len(document.items) == 81


def test_parse_first_inventory_item() -> None:
    document = parse_lightshell_inventory_pdf(
        FIXTURE_PATH.read_bytes()
    )

    first_item = document.items[0]

    assert first_item.source_number == 1
    assert first_item.name == (
        "Горячая кружка Магги со стаканчиком"
    )
    assert first_item.category == (
        "Горячая штучка"
    )
    assert first_item.program_quantity == Decimal(
        "4"
    )


def test_parse_three_digit_quantity() -> None:
    document = parse_lightshell_inventory_pdf(
        FIXTURE_PATH.read_bytes()
    )

    lottery_service = document.items[47]

    assert lottery_service.source_number == 48
    assert lottery_service.name == (
        "Услуга по участию в розыгрыше призов"
    )
    assert lottery_service.category == (
        "Услуга по участию в розыгрыше призов"
    )
    assert lottery_service.program_quantity == Decimal(
        "318"
    )


def test_parse_last_inventory_item() -> None:
    document = parse_lightshell_inventory_pdf(
        FIXTURE_PATH.read_bytes()
    )

    last_item = document.items[-1]

    assert last_item.source_number == 81
    assert last_item.name == (
        "HQD 0,45 в ассортименте"
    )
    assert last_item.category == "Энергетики"
    assert last_item.program_quantity == Decimal(
        "8"
    )


def test_empty_pdf_is_rejected() -> None:
    with pytest.raises(
        LightShellPdfParseError,
        match="Загруженный PDF пуст",
    ):
        parse_lightshell_inventory_pdf(b"")