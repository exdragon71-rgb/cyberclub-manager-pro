from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.product import Product


class Debt(Base):
    __tablename__ = "debts"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_debts_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_debts_unit_price_non_negative",
        ),
        CheckConstraint(
            "status IN ('active', 'paid')",
            name="ck_debts_status_valid",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    employee_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "employees.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    product_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "products.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        server_default="active",
        index=True,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    employee: Mapped["Employee"] = relationship()

    product: Mapped["Product"] = relationship()

    @property
    def total_amount(self) -> Decimal:
        return self.quantity * self.unit_price

    def __repr__(self) -> str:
        return (
            "Debt("
            f"id={self.id!r}, "
            f"employee_id={self.employee_id!r}, "
            f"product_id={self.product_id!r}, "
            f"status={self.status!r}"
            ")"
        )