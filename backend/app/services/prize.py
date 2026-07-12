from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.prize import Prize
from app.repositories.employee import (
    EmployeeRepository,
    employee_repository,
)
from app.repositories.prize import (
    PrizeRepository,
    prize_repository,
)
from app.repositories.product import (
    ProductRepository,
    product_repository,
)
from app.schemas.prize import (
    PrizeCreate,
    PrizeUpdate,
)


class PrizeNotFoundError(Exception):
    pass


class PrizeValidationError(Exception):
    pass


class PrizeService:
    def __init__(
        self,
        repository: PrizeRepository,
        employee_repository: EmployeeRepository,
        product_repository: ProductRepository,
    ) -> None:
        self.repository = repository
        self.employee_repository = employee_repository
        self.product_repository = product_repository

    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[Prize]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
            status=status,
        )

    def get_by_id(
        self,
        db: Session,
        prize_id: UUID,
    ) -> Prize:
        prize = self.repository.get_by_id(
            db,
            prize_id,
        )

        if prize is None:
            raise PrizeNotFoundError(
                "Приз не найден."
            )

        return prize

    def create(
        self,
        db: Session,
        prize_data: PrizeCreate,
    ) -> Prize:
        employee = (
            self.employee_repository.get_by_id(
                db,
                prize_data.employee_id,
            )
        )

        if employee is None:
            raise PrizeValidationError(
                "Сотрудник не найден."
            )

        if not employee.is_active:
            raise PrizeValidationError(
                "Нельзя оформить приз "
                "на сотрудника из архива."
            )

        product = (
            self.product_repository.get_by_id(
                db,
                prize_data.product_id,
            )
        )

        if product is None:
            raise PrizeValidationError(
                "Товар не найден."
            )

        if not product.is_active:
            raise PrizeValidationError(
                "Нельзя оформить приз "
                "на товар из архива."
            )

        note = (
            prize_data.note.strip()
            if (
                prize_data.note
                and prize_data.note.strip()
            )
            else None
        )

        try:
            prize = self.repository.create(
                db,
                employee_id=employee.id,
                product_id=product.id,
                quantity=prize_data.quantity,
                note=note,
            )

            db.commit()

            return self.get_by_id(
                db,
                prize.id,
            )

        except Exception:
            db.rollback()
            raise

    def update(
        self,
        db: Session,
        prize_id: UUID,
        prize_data: PrizeUpdate,
    ) -> Prize:
        prize = self.get_by_id(
            db,
            prize_id,
        )

        if prize.status == "written_off":
            raise PrizeValidationError(
                "Приз из истории нельзя изменить."
            )

        try:
            updated_prize = (
                self.repository.update(
                    db,
                    prize,
                    prize_data,
                )
            )

            db.commit()

            return self.get_by_id(
                db,
                updated_prize.id,
            )

        except Exception:
            db.rollback()
            raise

    def mark_written_off(
        self,
        db: Session,
        prize_id: UUID,
    ) -> Prize:
        prize = self.get_by_id(
            db,
            prize_id,
        )

        if prize.status == "written_off":
            raise PrizeValidationError(
                "Приз уже учтён в LightShell."
            )

        try:
            updated_prize = (
                self.repository.mark_written_off(
                    db,
                    prize,
                    written_off_at=datetime.now(
                        UTC
                    ),
                )
            )

            db.commit()

            return self.get_by_id(
                db,
                updated_prize.id,
            )

        except Exception:
            db.rollback()
            raise


prize_service = PrizeService(
    repository=prize_repository,
    employee_repository=employee_repository,
    product_repository=product_repository,
)