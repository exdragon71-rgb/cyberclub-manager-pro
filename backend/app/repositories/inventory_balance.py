from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.inventory_balance import InventoryBalance
from app.models.product import Product
from app.schemas.inventory_balance import (
    InventoryBalanceUpdate,
)


class InventoryBalanceRepository:
    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[InventoryBalance]:
        statement = (
            select(InventoryBalance)
            .join(InventoryBalance.product)
            .options(
                selectinload(
                    InventoryBalance.product
                )
            )
            .order_by(Product.name)
        )

        if not include_inactive:
            statement = statement.where(
                Product.is_active.is_(True)
            )

        statement = statement.offset(offset).limit(limit)

        return list(
            db.scalars(statement).all()
        )

    def get_by_product_id(
        self,
        db: Session,
        product_id: UUID,
    ) -> InventoryBalance | None:
        statement = (
            select(InventoryBalance)
            .options(
                selectinload(
                    InventoryBalance.product
                )
            )
            .where(
                InventoryBalance.product_id
                == product_id
            )
        )

        return db.scalar(statement)

    def create_for_product(
        self,
        db: Session,
        product_id: UUID,
    ) -> InventoryBalance:
        balance = InventoryBalance(
            product_id=product_id,
        )

        db.add(balance)
        db.flush()

        return balance

    def update(
        self,
        db: Session,
        balance: InventoryBalance,
        balance_data: InventoryBalanceUpdate,
    ) -> InventoryBalance:
        update_data = balance_data.model_dump(
            exclude_unset=True
        )

        for field_name, field_value in update_data.items():
            setattr(
                balance,
                field_name,
                field_value,
            )

        db.flush()

        return balance


inventory_balance_repository = (
    InventoryBalanceRepository()
)