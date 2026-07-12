from collections.abc import Collection
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.models.debt import Debt
from app.models.inventory_balance import (
    InventoryBalance,
)
from app.models.prize import Prize
from app.models.product import Product
from app.schemas.inventory_balance import (
    InventoryBalanceUpdate,
)


class InventoryBalanceRepository:
    @staticmethod
    def active_debt_quantity_query():
        return (
            select(
                func.coalesce(
                    func.sum(Debt.quantity),
                    0,
                )
            )
            .where(
                Debt.product_id
                == InventoryBalance.product_id,
                Debt.status == "active",
            )
            .correlate(
                InventoryBalance
            )
            .scalar_subquery()
        )

    @staticmethod
    def active_prize_quantity_query():
        return (
            select(
                func.coalesce(
                    func.sum(Prize.quantity),
                    0,
                )
            )
            .where(
                Prize.product_id
                == InventoryBalance.product_id,
                Prize.status == "active",
            )
            .correlate(
                InventoryBalance
            )
            .scalar_subquery()
        )

    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[InventoryBalance]:
        active_debt_quantity = (
            self.active_debt_quantity_query()
            .label(
                "active_debt_quantity"
            )
        )

        active_prize_quantity = (
            self.active_prize_quantity_query()
            .label(
                "active_prize_quantity"
            )
        )

        statement = (
            select(
                InventoryBalance,
                active_debt_quantity,
                active_prize_quantity,
            )
            .join(
                InventoryBalance.product
            )
            .options(
                selectinload(
                    InventoryBalance.product
                )
            )
            .order_by(
                Product.name
            )
        )

        if not include_inactive:
            statement = statement.where(
                Product.is_active.is_(True)
            )

        statement = statement.offset(
            offset
        ).limit(
            limit
        )

        rows = db.execute(
            statement
        ).all()

        balances: list[
            InventoryBalance
        ] = []

        for (
            balance,
            debt_quantity,
            prize_quantity,
        ) in rows:
            balance.active_debt_quantity = (
                debt_quantity
            )

            balance.active_prize_quantity = (
                prize_quantity
            )

            balances.append(
                balance
            )

        return balances

    def get_by_product_id(
        self,
        db: Session,
        product_id: UUID,
    ) -> InventoryBalance | None:
        active_debt_quantity = (
            self.active_debt_quantity_query()
            .label(
                "active_debt_quantity"
            )
        )

        active_prize_quantity = (
            self.active_prize_quantity_query()
            .label(
                "active_prize_quantity"
            )
        )

        statement = (
            select(
                InventoryBalance,
                active_debt_quantity,
                active_prize_quantity,
            )
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

        row = db.execute(
            statement
        ).one_or_none()

        if row is None:
            return None

        (
            balance,
            debt_quantity,
            prize_quantity,
        ) = row

        balance.active_debt_quantity = (
            debt_quantity
        )

        balance.active_prize_quantity = (
            prize_quantity
        )

        return balance

    def get_by_product_ids(
        self,
        db: Session,
        product_ids: Collection[UUID],
    ) -> dict[
        UUID,
        InventoryBalance,
    ]:
        if not product_ids:
            return {}

        statement = select(
            InventoryBalance
        ).where(
            InventoryBalance.product_id.in_(
                product_ids
            )
        )

        balances = list(
            db.scalars(
                statement
            ).all()
        )

        return {
            balance.product_id: balance
            for balance in balances
        }

    def create_for_product(
        self,
        db: Session,
        product_id: UUID,
    ) -> InventoryBalance:
        balance = InventoryBalance(
            product_id=product_id,
        )

        db.add(
            balance
        )

        db.flush()

        return balance

    def update(
        self,
        db: Session,
        balance: InventoryBalance,
        balance_data: InventoryBalanceUpdate,
    ) -> InventoryBalance:
        update_data = (
            balance_data.model_dump(
                exclude_unset=True
            )
        )

        for (
            field_name,
            field_value,
        ) in update_data.items():
            setattr(
                balance,
                field_name,
                field_value,
            )

        db.flush()

        return balance

    def update_program_quantity(
        self,
        db: Session,
        balance: InventoryBalance,
        program_quantity: Decimal,
    ) -> InventoryBalance:
        balance.program_quantity = (
            program_quantity
        )

        db.flush()

        return balance


inventory_balance_repository = (
    InventoryBalanceRepository()
)