from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.schemas.product import ProductRead


class InventoryBalanceUpdate(BaseModel):
    program_quantity: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=3,
    )

    actual_quantity: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=3,
    )


class InventoryBalanceRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    product_id: UUID

    program_quantity: Decimal
    actual_quantity: Decimal

    active_debt_quantity: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=3,
    )

    active_prize_quantity: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=3,
    )

    created_at: datetime
    updated_at: datetime

    product: ProductRead