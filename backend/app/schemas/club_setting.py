from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ClubSettingBase(BaseModel):
    club_name: str = Field(
        default="CyberClub",
        min_length=1,
        max_length=255,
        examples=["КиберДом"],
    )

    branch: str = Field(
        default="#1",
        min_length=1,
        max_length=255,
        examples=["1 этаж"],
    )

    lottery_ticket_price: Decimal = Field(
        default=Decimal("85.00"),
        ge=0,
        decimal_places=2,
        examples=[85],
    )


class ClubSettingUpdate(BaseModel):
    club_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    branch: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    lottery_ticket_price: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )


class ClubSettingRead(ClubSettingBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    setting_key: str
    created_at: datetime
    updated_at: datetime