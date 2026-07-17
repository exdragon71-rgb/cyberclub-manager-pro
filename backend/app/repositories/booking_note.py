from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.booking_note import BookingNote


class BookingNoteRepository:
    def get_by_date(
        self,
        db: Session,
        booking_date: date,
    ) -> BookingNote | None:
        statement = select(
            BookingNote
        ).where(
            BookingNote.booking_date
            == booking_date
        )

        return db.scalar(statement)

    def create(
        self,
        db: Session,
        *,
        booking_date: date,
        content: str = "",
    ) -> BookingNote:
        booking_note = BookingNote(
            booking_date=booking_date,
            content=content,
        )

        db.add(booking_note)
        db.flush()

        return booking_note

    def update(
        self,
        db: Session,
        booking_note: BookingNote,
        *,
        content: str,
    ) -> BookingNote:
        booking_note.content = content

        db.flush()

        return booking_note


booking_note_repository = (
    BookingNoteRepository()
)
