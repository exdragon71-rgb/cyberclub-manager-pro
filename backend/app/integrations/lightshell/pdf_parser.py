import re
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from pydantic import ValidationError
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.integrations.lightshell.schemas import (
    LightShellInventoryDocument,
    LightShellInventoryItem,
)


class LightShellPdfParseError(Exception):
    pass


def _clean_cell(value: str) -> str:
    value = (
        value
        .replace("\u00ad", "")
        .replace("\u200b", "")
        .replace("\ufffe", "")
    )

    # В layout-режиме pypdf иногда вставляет несколько
    # пробелов прямо внутрь одного слова.
    value = re.sub(
        r"[ \t]{2,}",
        "",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    ).strip()

    # Соединяем слова, перенесённые после дефиса.
    value = value.replace(
        "- ",
        "-",
    )

    return value


def _parse_document_metadata(
    reader: PdfReader,
) -> tuple[str, datetime]:
    first_page_text = (
        reader.pages[0].extract_text()
        or ""
    )

    metadata_match = re.search(
        (
            r"Филиал:\s*(?P<branch>.+?)\s+"
            r"Сформировано:\s*"
            r"(?P<generated_at>"
            r"\d{2}\.\d{2}\.\d{4},\s*"
            r"\d{2}:\d{2}:\d{2}"
            r")"
        ),
        first_page_text,
    )

    if metadata_match is None:
        raise LightShellPdfParseError(
            "Не удалось определить филиал "
            "и дату формирования PDF."
        )

    branch = _clean_cell(
        metadata_match.group("branch")
    )

    try:
        generated_at = datetime.strptime(
            metadata_match.group("generated_at"),
            "%d.%m.%Y, %H:%M:%S",
        )
    except ValueError as error:
        raise LightShellPdfParseError(
            "В PDF указана некорректная "
            "дата формирования."
        ) from error

    return branch, generated_at


def _find_column_positions(
    lines: list[str],
) -> tuple[int, int, int, int, int]:
    for line_index, line in enumerate(lines):
        if (
            "Название товара" in line
            and "Категория" in line
            and "Факт" in line
        ):
            name_start = line.index(
                "Название товара"
            )

            category_start = line.index(
                "Категория"
            )

            program_start = line.index(
                "По",
                category_start
                + len("Категория"),
            )

            fact_start = line.index(
                "Факт",
                program_start + len("По"),
            )

            return (
                line_index,
                name_start,
                category_start,
                program_start,
                fact_start,
            )

    raise LightShellPdfParseError(
        "На странице PDF не найдена "
        "таблица ревизии."
    )


def _parse_page_items(
    reader: PdfReader,
    page_index: int,
) -> list[LightShellInventoryItem]:
    page_text = reader.pages[
        page_index
    ].extract_text(
        extraction_mode="layout"
    )

    if not page_text:
        raise LightShellPdfParseError(
            f"Страница {page_index + 1} "
            "не содержит доступного текста."
        )

    lines = page_text.splitlines()

    (
        header_index,
        name_start,
        category_start,
        program_start,
        fact_start,
    ) = _find_column_positions(lines)

    parsed_rows: list[dict] = []
    current_row: dict | None = None

    for line in lines[header_index + 1:]:
        padded_line = line.ljust(
            fact_start
        )

        number_text = padded_line[
            :name_start
        ].strip()

        is_new_row = bool(
            re.fullmatch(
                r"\d+",
                number_text,
            )
        )

        quantity_start: int | None = None

        if is_new_row:
            if current_row is not None:
                parsed_rows.append(
                    current_row
                )

            current_row = {
                "source_number": int(
                    number_text
                ),
                "name_parts": [],
                "category_parts": [],
                "program_quantity": None,
            }

            quantity_match = re.search(
                r"(\d+(?:[.,]\d+)?)\s*$",
                line,
            )

            if quantity_match is None:
                raise LightShellPdfParseError(
                    "Не удалось определить "
                    "остаток товара №"
                    f"{number_text}."
                )

            quantity_text = (
                quantity_match
                .group(1)
                .replace(",", ".")
            )

            current_row[
                "program_quantity"
            ] = Decimal(quantity_text)

            quantity_start = (
                quantity_match.start(1)
            )

        if current_row is None:
            continue

        name_part = _clean_cell(
            padded_line[
                name_start:category_start
            ]
        )

        category_end = program_start

        # У трёхзначных остатков первая цифра
        # иногда заезжает в колонку категории.
        if (
            is_new_row
            and quantity_start is not None
        ):
            category_end = min(
                category_end,
                quantity_start,
            )

        category_part = _clean_cell(
            padded_line[
                category_start:category_end
            ]
        )

        if name_part:
            current_row[
                "name_parts"
            ].append(name_part)

        if category_part:
            current_row[
                "category_parts"
            ].append(category_part)

    if current_row is not None:
        parsed_rows.append(current_row)

    items: list[LightShellInventoryItem] = []

    for row in parsed_rows:
        name = _clean_cell(
            " ".join(
                row["name_parts"]
            )
        )

        category = _clean_cell(
            " ".join(
                row["category_parts"]
            )
        )

        program_quantity = row[
            "program_quantity"
        ]

        if not name:
            raise LightShellPdfParseError(
                "Не удалось прочитать название "
                f"товара №{row['source_number']}."
            )

        if not category:
            raise LightShellPdfParseError(
                "Не удалось прочитать категорию "
                f"товара №{row['source_number']}."
            )

        if program_quantity is None:
            raise LightShellPdfParseError(
                "Не удалось прочитать остаток "
                f"товара №{row['source_number']}."
            )

        try:
            item = LightShellInventoryItem(
                source_number=row[
                    "source_number"
                ],
                name=name,
                category=category,
                program_quantity=(
                    program_quantity
                ),
            )
        except ValidationError as error:
            raise LightShellPdfParseError(
                "Некорректные данные товара №"
                f"{row['source_number']}."
            ) from error

        items.append(item)

    return items


def parse_lightshell_inventory_pdf(
    file_content: bytes,
) -> LightShellInventoryDocument:
    if not file_content:
        raise LightShellPdfParseError(
            "Загруженный PDF пуст."
        )

    try:
        reader = PdfReader(
            BytesIO(file_content)
        )
    except (PdfReadError, ValueError) as error:
        raise LightShellPdfParseError(
            "Не удалось открыть PDF-файл."
        ) from error

    if reader.is_encrypted:
        raise LightShellPdfParseError(
            "PDF защищён паролем."
        )

    if not reader.pages:
        raise LightShellPdfParseError(
            "PDF не содержит страниц."
        )

    branch, generated_at = (
        _parse_document_metadata(reader)
    )

    items: list[
        LightShellInventoryItem
    ] = []

    for page_index in range(
        len(reader.pages)
    ):
        items.extend(
            _parse_page_items(
                reader,
                page_index,
            )
        )

    if not items:
        raise LightShellPdfParseError(
            "В PDF не найдено ни одного товара."
        )

    items.sort(
        key=lambda item: item.source_number
    )

    source_numbers = [
        item.source_number
        for item in items
    ]

    expected_numbers = list(
        range(
            1,
            len(items) + 1,
        )
    )

    if source_numbers != expected_numbers:
        raise LightShellPdfParseError(
            "Нумерация товаров в PDF "
            "повреждена или распознана не полностью."
        )

    try:
        return LightShellInventoryDocument(
            branch=branch,
            generated_at=generated_at,
            items=items,
        )
    except ValidationError as error:
        raise LightShellPdfParseError(
            "PDF содержит некорректные "
            "данные ревизии."
        ) from error