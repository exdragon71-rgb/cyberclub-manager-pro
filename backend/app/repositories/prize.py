from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.models.prize import Prize
from app.schemas.prize import PrizeUpdate


class PrizeRepository:
    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[Prize]:
        statement = (
            select(Prize)
            .options(
                selectinload(
                    Prize.employee
                ),
                selectinload(
                    Prize.product
                ),
            )
            .order_by(
                Prize.created_at.desc(),
            )
        )

        if status is not None:
            statement = statement.where(
                Prize.status == status
            )

        statement = statement.offset(
            offset
        ).limit(
            limit
        )

        return list(
            db.scalars(statement).all()
        )

    def get_by_id(
        self,
        db: Session,
        prize_id: UUID,
    ) -> Prize | None:
        statement = (
            select(Prize)
            .options(
                selectinload(
                    Prize.employee
                ),
                selectinload(
                    Prize.product
                ),
            )
            .where(
                Prize.id == prize_id
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
        ticket_price: Decimal,
        note: str | None,
    ) -> Prize:
        prize = Prize(
            employee_id=employee_id,
            product_id=product_id,
            quantity=quantity,
            ticket_price=ticket_price,
            note=note,
        )

        db.add(prize)
        db.flush()

        return prize

    def update(
        self,
        db: Session,
        prize: Prize,
        prize_data: PrizeUpdate,
    ) -> Prize:
        update_data = (
            prize_data.model_dump(
                exclude_unset=True
            )
        )

        if "note" in update_data:
            note = update_data["note"]

            update_data["note"] = (
                note.strip()
                if note
                and note.strip()
                else None
            )

        for (
            field_name,
            field_value,
        ) in update_data.items():
            setattr(
                prize,
                field_name,
                field_value,
            )

        db.flush()

        return prize

    def mark_written_off(
        self,
        db: Session,
        prize: Prize,
        *,
        written_off_at: datetime,
    ) -> Prize:
        prize.status = "written_off"
        prize.written_off_at = (
            written_off_at
        )

        db.flush()

        return prize


prize_repository = PrizeRepository()