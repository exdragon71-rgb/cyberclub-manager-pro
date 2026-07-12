from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class LightShellInventoryItem(BaseModel):
    source_number: int = Field(
        ge=1,
    )

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    category: str = Field(
        min_length=1,
        max_length=255,
    )

    program_quantity: Decimal = Field(
        ge=0,
        decimal_places=3,
    )


class LightShellInventoryDocument(BaseModel):
    branch: str = Field(
        min_length=1,
        max_length=255,
    )

    generated_at: datetime

    items: list[LightShellInventoryItem]


class LightShellMatchStatus(StrEnum):
    EXACT = "exact"
    MAPPED = "mapped"
    UNMATCHED = "unmatched"
    AMBIGUOUS = "ambiguous"


class LightShellImportPreviewItem(BaseModel):
    source_number: int = Field(
        ge=1,
    )

    source_name: str = Field(
        min_length=1,
        max_length=255,
    )

    normalized_source_name: str = Field(
        min_length=1,
        max_length=255,
    )

    source_category: str = Field(
        min_length=1,
        max_length=255,
    )

    program_quantity: Decimal = Field(
        ge=0,
        decimal_places=3,
    )

    status: LightShellMatchStatus

    product_id: UUID | None = None

    product_name: str | None = Field(
        default=None,
        max_length=255,
    )


class LightShellImportPreview(BaseModel):
    branch: str = Field(
        min_length=1,
        max_length=255,
    )

    generated_at: datetime

    source_filename: str = Field(
        min_length=1,
        max_length=255,
    )

    total_items: int = Field(
        ge=0,
    )

    matched_items: int = Field(
        ge=0,
    )

    unmatched_items: int = Field(
        ge=0,
    )

    ambiguous_items: int = Field(
        ge=0,
    )

    items: list[LightShellImportPreviewItem]