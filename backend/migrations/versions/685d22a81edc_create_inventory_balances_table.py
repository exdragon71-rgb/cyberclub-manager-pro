"""create inventory balances table

Revision ID: 685d22a81edc
Revises: 392563415110
Create Date: 2026-07-11 17:41:40.751829
"""

from decimal import Decimal
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = "685d22a81edc"
down_revision: Union[str, Sequence[str], None] = (
    "392563415110"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inventory_balances",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "program_quantity",
            sa.Numeric(
                precision=12,
                scale=3,
            ),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "actual_quantity",
            sa.Numeric(
                precision=12,
                scale=3,
            ),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f(
            "ix_inventory_balances_product_id"
        ),
        "inventory_balances",
        ["product_id"],
        unique=True,
    )

    products_table = sa.table(
        "products",
        sa.column(
            "id",
            sa.UUID(),
        ),
    )

    inventory_balances_table = sa.table(
        "inventory_balances",
        sa.column(
            "id",
            sa.UUID(),
        ),
        sa.column(
            "product_id",
            sa.UUID(),
        ),
        sa.column(
            "program_quantity",
            sa.Numeric(
                precision=12,
                scale=3,
            ),
        ),
        sa.column(
            "actual_quantity",
            sa.Numeric(
                precision=12,
                scale=3,
            ),
        ),
    )

    connection = op.get_bind()

    product_ids = connection.execute(
        sa.select(products_table.c.id)
    ).scalars().all()

    if product_ids:
        op.bulk_insert(
            inventory_balances_table,
            [
                {
                    "id": uuid4(),
                    "product_id": product_id,
                    "program_quantity": Decimal("0"),
                    "actual_quantity": Decimal("0"),
                }
                for product_id in product_ids
            ],
        )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_inventory_balances_product_id"
        ),
        table_name="inventory_balances",
    )

    op.drop_table(
        "inventory_balances"
    )