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


class InventoryBalanceNotFoundError(Exception):
    pass


class InventoryBalanceService:
    def __init__(
        self,
        repository: InventoryBalanceRepository,
    ) -> None:
        self.repository = repository

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

        try:
            updated_balance = self.repository.update(
                db,
                balance,
                balance_data,
            )

            db.commit()
            db.refresh(updated_balance)

            return updated_balance

        except Exception:
            db.rollback()
            raise


inventory_balance_service = InventoryBalanceService(
    repository=inventory_balance_repository
)   