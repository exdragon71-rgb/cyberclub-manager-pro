from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
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
from app.services.action_log import (
    ActionLogService,
    action_log_service,
)
from app.services.club_setting import (
    ClubSettingService,
    club_setting_service,
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
        action_log_service: ActionLogService,
        club_setting_service: ClubSettingService,
    ) -> None:
        self.repository = repository
        self.employee_repository = employee_repository
        self.product_repository = product_repository
        self.action_log_service = action_log_service
        self.club_setting_service = (
            club_setting_service
        )

    @staticmethod
    def _get_log_details(
        prize: Prize,
    ) -> dict[str, Any]:
        return {
            "employee_id": str(
                prize.employee_id
            ),
            "product_id": str(
                prize.product_id
            ),
            "quantity": str(
                prize.quantity
            ),
            "ticket_price": format(
                prize.ticket_price,
                ".2f",
            ),
            "status": prize.status,
            "note": prize.note,
            "written_off_at": (
                prize.written_off_at.isoformat()
                if prize.written_off_at
                else None
            ),
        }

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

        if (
            prize_data.quantity
            != Decimal("1")
        ):
            raise PrizeValidationError(
                "Одна запись должна "
                "соответствовать одной "
                "лотерейке и одному призу. "
                "Количество должно быть равно 1."
            )

        club_setting = (
            self.club_setting_service.get_default(
                db,
            )
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
                quantity=Decimal("1"),
                ticket_price=(
                    club_setting
                    .lottery_ticket_price
                ),
                note=note,
            )

            self.action_log_service.record(
                db,
                event_type="prize_created",
                entity_type="prize",
                entity_id=prize.id,
                message=(
                    "Выдан лотерейный приз "
                    f"«{product.name}». "
                    "Сотрудник: "
                    f"«{employee.name}»."
                ),
                details={
                    **self._get_log_details(
                        prize,
                    ),
                    "employee_name": (
                        employee.name
                    ),
                    "product_name": (
                        product.name
                    ),
                },
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

        if (
            prize_data.quantity is not None
            and prize_data.quantity
            != Decimal("1")
        ):
            raise PrizeValidationError(
                "Количество приза "
                "должно быть равно 1."
            )

        before_details = (
            self._get_log_details(
                prize,
            )
        )

        try:
            updated_prize = (
                self.repository.update(
                    db,
                    prize,
                    prize_data,
                )
            )

            after_details = (
                self._get_log_details(
                    updated_prize,
                )
            )

            if before_details != after_details:
                self.action_log_service.record(
                    db,
                    event_type="prize_updated",
                    entity_type="prize",
                    entity_id=updated_prize.id,
                    message=(
                        "Изменена запись "
                        "лотерейного приза "
                        f"«{updated_prize.product.name}». "
                        "Сотрудник: "
                        f"«{updated_prize.employee.name}»."
                    ),
                    details={
                        "before": before_details,
                        "after": after_details,
                        "employee_name": (
                            updated_prize
                            .employee
                            .name
                        ),
                        "product_name": (
                            updated_prize
                            .product
                            .name
                        ),
                    },
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

            self.action_log_service.record(
                db,
                event_type="prize_reflected",
                entity_type="prize",
                entity_id=updated_prize.id,
                message=(
                    "Подтверждён учёт "
                    "лотерейного приза "
                    f"«{updated_prize.product.name}» "
                    "в LightShell."
                ),
                details={
                    **self._get_log_details(
                        updated_prize,
                    ),
                    "employee_name": (
                        updated_prize
                        .employee
                        .name
                    ),
                    "product_name": (
                        updated_prize
                        .product
                        .name
                    ),
                },
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
    action_log_service=action_log_service,
    club_setting_service=club_setting_service,
)