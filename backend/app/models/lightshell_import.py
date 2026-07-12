from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.product import Product


class LightShellProductMapping(Base):
    __tablename__ = "lightshell_product_mappings"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    normalized_source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    source_category: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    product_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "products.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    product: Mapped["Product"] = relationship()

    def __repr__(self) -> str:
        return (
            "LightShellProductMapping("
            f"id={self.id!r}, "
            f"source_name={self.source_name!r}, "
            f"product_id={self.product_id!r}"
            ")"
        )


class LightShellInventoryImport(Base):
    __tablename__ = "lightshell_inventory_imports"

    __table_args__ = (
        CheckConstraint(
            "total_items >= 0",
            name="ck_lightshell_import_total_items",
        ),
        CheckConstraint(
            "matched_items >= 0",
            name="ck_lightshell_import_matched_items",
        ),
        CheckConstraint(
            "created_items >= 0",
            name="ck_lightshell_import_created_items",
        ),
        CheckConstraint(
            "unresolved_items >= 0",
            name="ck_lightshell_import_unresolved_items",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    branch: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
    )

    source_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    total_items: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    matched_items: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    created_items: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    unresolved_items: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            "LightShellInventoryImport("
            f"id={self.id!r}, "
            f"branch={self.branch!r}, "
            f"generated_at={self.generated_at!r}"
            ")"
        )