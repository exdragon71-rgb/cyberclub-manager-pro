from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.schemas.employee import EmployeeRead
from app.schemas.product import ProductRead


PrizeStatus = Literal[
    "active",
    "written_off",
]


class PrizeCreate(BaseModel):
    employee_id: UUID
    product_id: UUID

    quantity: Decimal = Field(
        gt=0,
        decimal_places=3,
        examples=[1],
    )

    note: str | None = Field(
        default=None,
        max_length=2000,
    )


class PrizeUpdate(BaseModel):
    quantity: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=3,
    )

    note: str | None = Field(
        default=None,
        max_length=2000,
    )


class PrizeRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    employee_id: UUID
    product_id: UUID

    quantity: Decimal
    ticket_price: Decimal

    status: PrizeStatus
    note: str | None

    created_at: datetime
    updated_at: datetime
    written_off_at: datetime | None

    employee: EmployeeRead
    product: ProductRead