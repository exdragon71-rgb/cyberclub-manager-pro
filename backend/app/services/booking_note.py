from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.booking_note import BookingNote
from app.repositories.booking_note import (
    BookingNoteRepository,
    booking_note_repository,
)


class BookingNoteService:
    def __init__(
        self,
        repository: BookingNoteRepository,
    ) -> None:
        self.repository = repository

    def get_by_date(
        self,
        db: Session,
        booking_date: date,
    ) -> BookingNote:
        booking_note = (
            self.repository.get_by_date(
                db,
                booking_date,
            )
        )

        if booking_note is not None:
            return booking_note

        try:
            booking_note = (
                self.repository.create(
                    db,
                    booking_date=booking_date,
                )
            )

            db.commit()
            db.refresh(booking_note)

            return booking_note

        except IntegrityError:
            db.rollback()

            booking_note = (
                self.repository.get_by_date(
                    db,
                    booking_date,
                )
            )

            if booking_note is None:
                raise

            return booking_note

        except Exception:
            db.rollback()
            raise

    def update(
        self,
        db: Session,
        booking_date: date,
        *,
        content: str,
    ) -> BookingNote:
        booking_note = self.get_by_date(
            db,
            booking_date,
        )

        try:
            updated_booking_note = (
                self.repository.update(
                    db,
                    booking_note,
                    content=content,
                )
            )

            db.commit()
            db.refresh(
                updated_booking_note,
            )

            return updated_booking_note

        except Exception:
            db.rollback()
            raise


booking_note_service = BookingNoteService(
    repository=booking_note_repository,
)
