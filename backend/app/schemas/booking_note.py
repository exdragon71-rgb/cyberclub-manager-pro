from datetime import date, datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class BookingNoteUpdate(BaseModel):
    content: str = Field(
        max_length=20000,
    )


class BookingNoteRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    booking_date: date
    content: str

    created_at: datetime
    updated_at: datetime
