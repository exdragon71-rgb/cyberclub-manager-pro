from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.debt import Debt
from app.schemas.debt import DebtUpdate


class DebtRepository:
    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[Debt]:
        statement = (
            select(Debt)
            .options(
                selectinload(Debt.employee),
                selectinload(Debt.product),
            )
            .order_by(
                Debt.created_at.desc(),
            )
        )

        if status is not None:
            statement = statement.where(
                Debt.status == status
            )

        statement = statement.offset(offset).limit(limit)

        return list(
            db.scalars(statement).all()
        )

    def get_by_id(
        self,
        db: Session,
        debt_id: UUID,
    ) -> Debt | None:
        statement = (
            select(Debt)
            .options(
                selectinload(Debt.employee),
                selectinload(Debt.product),
            )
            .where(
                Debt.id == debt_id
            )
        )

        return db.scalar(statement)

    def create(
        self,
        db: Session,
        *,
        employee_id: UUID,
        product_id: UUID,
        quantity: Decimal,
        unit_price: Decimal,
        note: str | None,
    ) -> Debt:
        debt = Debt(
            employee_id=employee_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            note=note,
        )

        db.add(debt)
        db.flush()

        return debt

    def update(
        self,
        db: Session,
        debt: Debt,
        debt_data: DebtUpdate,
    ) -> Debt:
        update_data = debt_data.model_dump(
            exclude_unset=True
        )

        if "note" in update_data:
            note = update_data["note"]

            update_data["note"] = (
                note.strip()
                if note and note.strip()
                else None
            )

        for field_name, field_value in update_data.items():
            setattr(
                debt,
                field_name,
                field_value,
            )

        db.flush()

        return debt

    def mark_paid(
        self,
        db: Session,
        debt: Debt,
        *,
        paid_at: datetime,
    ) -> Debt:
        debt.status = "paid"
        debt.paid_at = paid_at

        db.flush()

        return debt


debt_repository = DebtRepository()