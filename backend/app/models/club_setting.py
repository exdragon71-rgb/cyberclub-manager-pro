from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ClubSetting(Base):
    __tablename__ = "club_settings"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    setting_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        default="default",
        server_default="default",
    )

    club_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="CyberClub",
        server_default="CyberClub",
    )

    branch: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="#1",
        server_default="#1",
    )

    lottery_ticket_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("85.00"),
        server_default="85.00",
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

    def __repr__(self) -> str:
        return (
            "ClubSetting("
            f"id={self.id!r}, "
            f"club_name={self.club_name!r}, "
            f"branch={self.branch!r}"
            ")"
        )