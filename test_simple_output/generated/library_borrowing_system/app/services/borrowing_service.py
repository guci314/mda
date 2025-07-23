from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date, timedelta, datetime
import uuid
from typing import List

from app import crud, schemas, models

class BorrowingService:
    def _get_borrowing_limits(self, reader_type: models.ReaderType):
        if reader_type == models.ReaderType.STUDENT:
            return {"limit": 10, "days": 30}
        if reader_type == models.ReaderType.TEACHER:
            return {"limit": 20, "days": 90}
        return {"limit": 5, "days": 20} # Staff

    def borrow_book(self, db: Session, *, borrow_request: schemas.BorrowCreate) -> models.BorrowRecord:
        reader = crud.reader.get_by_reader_id(db, reader_id=borrow_request.reader_id)
        if not reader:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")
        if reader.status != models.ReaderStatus.NORMAL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reader account is not normal")
        if reader.credit_score < 60:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credit score too low")

        limits = self._get_borrowing_limits(reader.reader_type)
        active_borrows = crud.borrow_record.get_active_borrows_by_reader(db, reader_id=reader.reader_id)
        if len(active_borrows) >= limits["limit"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Borrowing limit reached")

        book = crud.book.get_by_isbn(db, isbn=borrow_request.isbn)
        if not book or book.status != models.BookStatus.ON_SHELF:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found or not on shelf")
        if book.available_count <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is currently unavailable")

        borrow_date = datetime.utcnow()
        due_date = date.today() + timedelta(days=limits["days"])
        
        new_borrow_record_data = schemas.BorrowCreate(
            reader_id=borrow_request.reader_id,
            isbn=borrow_request.isbn
        )
        
        # Manually create the model instance as BorrowCreate doesn't cover all fields
        new_borrow_record = models.BorrowRecord(
            **new_borrow_record_data.model_dump(),
            borrow_id=str(uuid.uuid4()),
            borrow_date=borrow_date,
            due_date=due_date,
            status=models.BorrowStatus.BORROWED
        )

        book.available_count -= 1
        
        db.add(new_borrow_record)
        db.add(book)
        db.commit()
        db.refresh(new_borrow_record)
        
        return new_borrow_record

    def return_book(self, db: Session, *, borrow_id: str) -> models.BorrowRecord:
        borrow_record = crud.borrow_record.get_by_borrow_id(db, borrow_id=borrow_id)
        if not borrow_record or borrow_record.status != models.BorrowStatus.BORROWED:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active borrow record not found")

        book = crud.book.get_by_isbn(db, isbn=borrow_record.isbn)
        if not book:
            # This should not happen if data is consistent
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated book not found")

        borrow_record.return_date = datetime.utcnow()
        fine = 0.0
        if date.today() > borrow_record.due_date:
            borrow_record.status = models.BorrowStatus.OVERDUE
            overdue_days = (date.today() - borrow_record.due_date).days
            fine = overdue_days * 0.5 # Example fine: 0.5 per day
        else:
            borrow_record.status = models.BorrowStatus.RETURNED
        
        borrow_record.fine = fine
        book.available_count += 1

        db.add(borrow_record)
        db.add(book)
        db.commit()
        db.refresh(borrow_record)

        # Check for reservations
        from app.services.reservation_service import reservation as reservation_service
        reservation_service.notify_next_in_line(db, isbn=book.isbn)

        return borrow_record

    def renew_book(self, db: Session, *, borrow_id: str) -> models.BorrowRecord:
        borrow_record = crud.borrow_record.get_by_borrow_id(db, borrow_id=borrow_id)
        if not borrow_record or borrow_record.status != models.BorrowStatus.BORROWED:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active borrow record not found")
        
        if date.today() > borrow_record.due_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot renew an overdue book")
        
        if borrow_record.renewal_count >= 1: # Limit to 1 renewal
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Renewal limit reached")

        reader = crud.reader.get_by_reader_id(db, reader_id=borrow_record.reader_id)
        limits = self._get_borrowing_limits(reader.reader_type)
        
        borrow_record.due_date += timedelta(days=limits["days"])
        borrow_record.renewal_count += 1
        
        db.add(borrow_record)
        db.commit()
        db.refresh(borrow_record)
        
        return borrow_record

    def get_overdue_records(self, db: Session) -> List[models.BorrowRecord]:
        return crud.borrow_record.get_overdue_records(db)

borrowing = BorrowingService()
