from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.debt import Debt
from app.repositories.debt import (
    DebtRepository,
    debt_repository,
)
from app.repositories.employee import (
    EmployeeRepository,
    employee_repository,
)
from app.repositories.inventory_balance import (
    InventoryBalanceRepository,
    inventory_balance_repository,
)
from app.repositories.product import (
    ProductRepository,
    product_repository,
)
from app.schemas.debt import (
    DebtCreate,
    DebtUpdate,
)
from app.services.action_log import (
    ActionLogService,
    action_log_service,
)


class DebtNotFoundError(Exception):
    pass


class DebtValidationError(Exception):
    pass


class DebtService:
    def __init__(
        self,
        repository: DebtRepository,
        employee_repository: EmployeeRepository,
        product_repository: ProductRepository,
        balance_repository: InventoryBalanceRepository,
        action_log_service: ActionLogService,
    ) -> None:
        self.repository = repository
        self.employee_repository = employee_repository
        self.product_repository = product_repository
        self.balance_repository = balance_repository
        self.action_log_service = action_log_service

    @staticmethod
    def _get_log_details(
        debt: Debt,
    ) -> dict[str, Any]:
        return {
            "employee_id": str(
                debt.employee_id
            ),
            "product_id": str(
                debt.product_id
            ),
            "quantity": str(
                debt.quantity
            ),
            "unit_price": str(
                debt.unit_price
            ),
            "total_amount": str(
                debt.total_amount
            ),
            "status": debt.status,
            "note": debt.note,
            "paid_at": (
                debt.paid_at.isoformat()
                if debt.paid_at
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
    ) -> list[Debt]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
            status=status,
        )

    def get_by_id(
        self,
        db: Session,
        debt_id: UUID,
    ) -> Debt:
        debt = self.repository.get_by_id(
            db,
            debt_id,
        )

        if debt is None:
            raise DebtNotFoundError(
                "Долг не найден."
            )

        return debt

    def create(
        self,
        db: Session,
        debt_data: DebtCreate,
    ) -> Debt:
        employee = (
            self.employee_repository.get_by_id(
                db,
                debt_data.employee_id,
            )
        )

        if employee is None:
            raise DebtValidationError(
                "Сотрудник не найден."
            )

        if not employee.is_active:
            raise DebtValidationError(
                "Нельзя оформить долг "
                "на сотрудника из архива."
            )

        product = (
            self.product_repository.get_by_id(
                db,
                debt_data.product_id,
            )
        )

        if product is None:
            raise DebtValidationError(
                "Товар не найден."
            )

        if not product.is_active:
            raise DebtValidationError(
                "Нельзя оформить долг "
                "на товар из архива."
            )

        note = (
            debt_data.note.strip()
            if (
                debt_data.note
                and debt_data.note.strip()
            )
            else None
        )

        try:
            debt = self.repository.create(
                db,
                employee_id=employee.id,
                product_id=product.id,
                quantity=debt_data.quantity,
                unit_price=product.price,
                note=note,
            )

            self.action_log_service.record(
                db,
                event_type="debt_created",
                entity_type="debt",
                entity_id=debt.id,
                message=(
                    "Добавлен долг сотрудника "
                    f"«{employee.name}» за товар "
                    f"«{product.name}»."
                ),
                details={
                    **self._get_log_details(
                        debt,
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
                debt.id,
            )

        except Exception:
            db.rollback()
            raise

    def update(
        self,
        db: Session,
        debt_id: UUID,
        debt_data: DebtUpdate,
    ) -> Debt:
        debt = self.get_by_id(
            db,
            debt_id,
        )

        if debt.status == "paid":
            raise DebtValidationError(
                "Погашенный долг нельзя изменить."
            )

        before_details = (
            self._get_log_details(
                debt,
            )
        )

        try:
            updated_debt = (
                self.repository.update(
                    db,
                    debt,
                    debt_data,
                )
            )

            after_details = (
                self._get_log_details(
                    updated_debt,
                )
            )

            if before_details != after_details:
                self.action_log_service.record(
                    db,
                    event_type="debt_updated",
                    entity_type="debt",
                    entity_id=updated_debt.id,
                    message=(
                        "Изменён долг сотрудника "
                        f"«{updated_debt.employee.name}» "
                        "за товар "
                        f"«{updated_debt.product.name}»."
                    ),
                    details={
                        "before": before_details,
                        "after": after_details,
                        "employee_name": (
                            updated_debt
                            .employee
                            .name
                        ),
                        "product_name": (
                            updated_debt
                            .product
                            .name
                        ),
                    },
                )

            db.commit()

            return self.get_by_id(
                db,
                updated_debt.id,
            )

        except Exception:
            db.rollback()
            raise

    def mark_paid(
        self,
        db: Session,
        debt_id: UUID,
    ) -> Debt:
        debt = self.get_by_id(
            db,
            debt_id,
        )

        if debt.status == "paid":
            return debt

        balance = (
            self.balance_repository
            .get_by_product_id(
                db,
                debt.product_id,
            )
        )

        if balance is None:
            raise DebtValidationError(
                "Остатки товара не найдены."
            )

        program_quantity_before = (
            balance.program_quantity
        )

        try:
            balance.program_quantity = (
                balance.program_quantity
                - debt.quantity
            )

            paid_debt = (
                self.repository.mark_paid(
                    db,
                    debt,
                    paid_at=datetime.now(
                        timezone.utc
                    ),
                )
            )

            self.action_log_service.record(
                db,
                event_type="debt_paid",
                entity_type="debt",
                entity_id=paid_debt.id,
                message=(
                    "Погашен долг сотрудника "
                    f"«{paid_debt.employee.name}» "
                    "за товар "
                    f"«{paid_debt.product.name}»."
                ),
                details={
                    **self._get_log_details(
                        paid_debt,
                    ),
                    "employee_name": (
                        paid_debt
                        .employee
                        .name
                    ),
                    "product_name": (
                        paid_debt
                        .product
                        .name
                    ),
                    "program_quantity_before": str(
                        program_quantity_before
                    ),
                    "program_quantity_after": str(
                        balance.program_quantity
                    ),
                },
            )

            db.commit()

            return self.get_by_id(
                db,
                paid_debt.id,
            )

        except Exception:
            db.rollback()
            raise


debt_service = DebtService(
    repository=debt_repository,
    employee_repository=employee_repository,
    product_repository=product_repository,
    balance_repository=inventory_balance_repository,
    action_log_service=action_log_service,
)