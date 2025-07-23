from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import uuid

from app import crud, schemas, models

class ReservationService:
    def reserve_book(self, db: Session, *, reservation_request: schemas.ReservationCreate) -> models.ReservationRecord:
        reader = crud.reader.get_by_reader_id(db, reader_id=reservation_request.reader_id)
        if not reader or reader.status != models.ReaderStatus.NORMAL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reader not found or account not normal")

        book = crud.book.get_by_isbn(db, isbn=reservation_request.isbn)
        if not book or book.status != models.BookStatus.ON_SHELF:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found or not on shelf")
        
        if book.available_count > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is available for borrowing, no reservation needed")

        # Check if user already has an active reservation for this book
        existing_reservation = crud.reservation_record.get_active_reservation_for_book(
            db, reader_id=reader.reader_id, isbn=book.isbn
        )
        if existing_reservation:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have an active reservation for this book")

        new_reservation_data = schemas.ReservationCreate(
            reader_id=reservation_request.reader_id,
            isbn=reservation_request.isbn
        )

        new_reservation = models.ReservationRecord(
            **new_reservation_data.model_dump(),
            reservation_id=str(uuid.uuid4()),
            reservation_date=datetime.utcnow(),
            status=models.ReservationStatus.WAITING
        )

        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)

        return new_reservation

    def notify_next_in_line(self, db: Session, *, isbn: str):
        """
        Find the next person in the waiting list for a book and notify them.
        This is called when a book is returned.
        """
        waiting_list = crud.reservation_record.get_waiting_list_for_book(db, isbn=isbn)
        if not waiting_list:
            return # No one is waiting

        next_reservation = waiting_list[0]
        now = datetime.utcnow()
        
        update_data = schemas.ReservationUpdate(
            status=models.ReservationStatus.AVAILABLE,
            available_date=now,
            pickup_deadline=now + timedelta(days=3) # 3 days to pick up
        )
        
        crud.reservation_record.update(db, db_obj=next_reservation, obj_in=update_data)
        
        # Here you would typically trigger a notification (e.g., email, SMS)
        print(f"Notification: Book {isbn} is available for reader {next_reservation.reader_id}")

reservation = ReservationService()
