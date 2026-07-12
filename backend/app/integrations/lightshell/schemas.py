from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


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


class LightShellResolutionAction(StrEnum):
    USE_EXISTING = "use_existing"
    CREATE_NEW = "create_new"
    SKIP = "skip"


class LightShellImportResolution(BaseModel):
    source_number: int = Field(
        ge=1,
    )

    action: LightShellResolutionAction

    product_id: UUID | None = None

    @model_validator(
        mode="after",
    )
    def validate_product_id(self) -> Self:
        if (
            self.action
            == LightShellResolutionAction.USE_EXISTING
            and self.product_id is None
        ):
            raise ValueError(
                "Для существующего товара "
                "необходимо указать product_id."
            )

        if (
            self.action
            != LightShellResolutionAction.USE_EXISTING
            and self.product_id is not None
        ):
            raise ValueError(
                "product_id можно указывать "
                "только для существующего товара."
            )

        return self


class LightShellImportApplyResult(BaseModel):
    import_id: UUID

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

    updated_items: int = Field(
        ge=0,
    )

    created_products: int = Field(
        ge=0,
    )

    skipped_items: int = Field(
        ge=0,
    )

    created_mappings: int = Field(
        ge=0,
    )