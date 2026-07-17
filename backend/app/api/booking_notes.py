from datetime import date

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.booking_note import (
    BookingNoteRead,
    BookingNoteUpdate,
)
from app.services.booking_note import (
    BookingNoteService,
    booking_note_service,
)


router = APIRouter(
    prefix="/booking-notes",
    tags=["booking-notes"],
)


def get_booking_note_service() -> (
    BookingNoteService
):
    return booking_note_service


@router.get(
    "/{booking_date}",
    response_model=BookingNoteRead,
)
def get_booking_note(
    booking_date: date,
    db: Session = Depends(get_db),
    service: BookingNoteService = Depends(
        get_booking_note_service,
    ),
) -> BookingNoteRead:
    return service.get_by_date(
        db,
        booking_date,
    )


@router.put(
    "/{booking_date}",
    response_model=BookingNoteRead,
)
def update_booking_note(
    booking_date: date,
    booking_note_data: BookingNoteUpdate,
    db: Session = Depends(get_db),
    service: BookingNoteService = Depends(
        get_booking_note_service,
    ),
) -> BookingNoteRead:
    return service.update(
        db,
        booking_date,
        content=booking_note_data.content,
    )
