"""add booking notes

Revision ID: b17493b8d157
Revises: 5b16e12a9335
Create Date: 2026-07-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b17493b8d157"
down_revision: Union[str, Sequence[str], None] = (
    "5b16e12a9335"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "booking_notes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "booking_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            server_default="",
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_booking_notes_booking_date"),
        "booking_notes",
        ["booking_date"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_booking_notes_booking_date"),
        table_name="booking_notes",
    )

    op.drop_table(
        "booking_notes",
    )
