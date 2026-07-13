from uuid import UUID

from sqlalchemy.orm import Session

from app.models.inventory_balance import InventoryBalance
from app.repositories.inventory_balance import (
    InventoryBalanceRepository,
    inventory_balance_repository,
)
from app.schemas.inventory_balance import (
    InventoryBalanceUpdate,
)
from app.services.action_log import (
    ActionLogService,
    action_log_service,
)


class InventoryBalanceNotFoundError(Exception):
    pass


class InventoryBalanceService:
    def __init__(
        self,
        repository: InventoryBalanceRepository,
        action_log_service: ActionLogService,
    ) -> None:
        self.repository = repository
        self.action_log_service = action_log_service

    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[InventoryBalance]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
            include_inactive=include_inactive,
        )

    def get_by_product_id(
        self,
        db: Session,
        product_id: UUID,
    ) -> InventoryBalance:
        balance = self.repository.get_by_product_id(
            db,
            product_id,
        )

        if balance is None:
            raise InventoryBalanceNotFoundError(
                "Остатки для товара не найдены."
            )

        return balance

    def update(
        self,
        db: Session,
        product_id: UUID,
        balance_data: InventoryBalanceUpdate,
    ) -> InventoryBalance:
        balance = self.get_by_product_id(
            db,
            product_id,
        )

        program_quantity_before = (
            balance.program_quantity
        )

        actual_quantity_before = (
            balance.actual_quantity
        )

        try:
            updated_balance = (
                self.repository.update(
                    db,
                    balance,
                    balance_data,
                )
            )

            values_changed = (
                program_quantity_before
                != updated_balance.program_quantity
                or actual_quantity_before
                != updated_balance.actual_quantity
            )

            if values_changed:
                self.action_log_service.record(
                    db,
                    event_type=(
                        "inventory_balance_updated"
                    ),
                    entity_type="inventory_balance",
                    entity_id=updated_balance.id,
                    message=(
                        "Изменены остатки товара "
                        f"«{updated_balance.product.name}»."
                    ),
                    details={
                        "product_id": str(
                            updated_balance.product_id
                        ),
                        "product_name": (
                            updated_balance.product.name
                        ),
                        "before": {
                            "program_quantity": str(
                                program_quantity_before
                            ),
                            "actual_quantity": str(
                                actual_quantity_before
                            ),
                        },
                        "after": {
                            "program_quantity": str(
                                updated_balance
                                .program_quantity
                            ),
                            "actual_quantity": str(
                                updated_balance
                                .actual_quantity
                            ),
                        },
                    },
                )

            db.commit()
            db.refresh(
                updated_balance,
            )

            return self.get_by_product_id(
                db,
                updated_balance.product_id,
            )

        except Exception:
            db.rollback()
            raise


inventory_balance_service = InventoryBalanceService(
    repository=inventory_balance_repository,
    action_log_service=action_log_service,
)