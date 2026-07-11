from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
        examples=["Lipton Лимон 0,5"],
    )

    price: Decimal = Field(
        ge=0,
        decimal_places=2,
        examples=[130],
    )

    unit: str = Field(
        default="шт.",
        min_length=1,
        max_length=32,
    )

    minimum_stock: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=3,
    )

    lightshell_id: str | None = Field(
        default=None,
        max_length=255,
    )


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )

    unit: str | None = Field(
        default=None,
        min_length=1,
        max_length=32,
    )

    minimum_stock: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=3,
    )

    lightshell_id: str | None = Field(
        default=None,
        max_length=255,
    )

    is_active: bool | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime