import uuid
from datetime import datetime, timedelta, date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.models.reader import ReaderStatus, ReaderType
from app.models.book import BookStatus
from app.models.borrow_record import BorrowStatus
from app.models.reservation_record import ReservationStatus

class BorrowingService:
    def _get_borrow_limit(self, reader_type: ReaderType) -> int:
        limits = {
            ReaderType.STUDENT: 10,
            ReaderType.TEACHER: 20,
            ReaderType.STAFF: 5,
        }
        return limits.get(reader_type, 5)

    def _calculate_due_date(self, borrow_date: date, reader_type: ReaderType) -> date:
        days = {
            ReaderType.STUDENT: 30,
            ReaderType.TEACHER: 60,
            ReaderType.STAFF: 20,
        }
        return borrow_date + timedelta(days=days.get(reader_type, 20))

    def borrow_book(self, db: Session, borrow_request: schemas.BorrowCreateAction) -> models.BorrowRecord:
        reader = crud.reader.get_by_reader_id(db, reader_id=borrow_request.reader_id)
        if not reader:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")

        if reader.status != ReaderStatus.NORMAL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reader account is not normal")
        if reader.credit_score < 60:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient credit score")

        limit = self._get_borrow_limit(reader.reader_type)
        current_borrows = crud.borrow_record.count_active_borrows_by_reader(db, reader_id=reader.reader_id)
        if current_borrows >= limit:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Borrowing limit reached")

        book = crud.book.get_by_isbn(db, isbn=borrow_request.isbn)
        if not book or book.status == BookStatus.OFF_SHELF:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found or is off shelf")

        if book.available_stock <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No available stock")

        # Check if this reader is first in reservation queue if book is reserved
        waiting_list = crud.reservation_record.get_waiting_list_for_book(db, isbn=book.isbn)
        if waiting_list and waiting_list[0].reader_id != reader.reader_id:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is reserved by another reader.")

        # Create borrow record
        borrow_date = date.today()
        new_record_schema = schemas.BorrowRecordCreate(
            borrow_id=str(uuid.uuid4()),
            reader_id=reader.reader_id,
            isbn=book.isbn,
            due_date=self._calculate_due_date(borrow_date, reader.reader_type)
        )
        new_record = crud.borrow_record.create(db, obj_in=new_record_schema)

        # Update book stock
        book.available_stock -= 1
        db.add(book)
        db.commit()
        db.refresh(new_record)
        
        return new_record

    def return_book(self, db: Session, borrow_id: str) -> schemas.ReturnResponse:
        borrow_record = crud.borrow_record.get_by_borrow_id(db, borrow_id=borrow_id)
        if not borrow_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow record not found")
        if borrow_record.status == BorrowStatus.RETURNED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book already returned")

        # Calculate fine
        fine = Decimal("0.00")
        if date.today() > borrow_record.due_date:
            overdue_days = (date.today() - borrow_record.due_date).days
            fine = Decimal(overdue_days) * Decimal("0.50") # 0.5 per day
            borrow_record.status = BorrowStatus.OVERDUE
        else:
            borrow_record.status = BorrowStatus.RETURNED
        
        borrow_record.return_date = datetime.utcnow()
        borrow_record.fine = fine
        
        # Update book stock
        book = crud.book.get_by_isbn(db, isbn=borrow_record.isbn)
        if book:
            book.available_stock += 1
            db.add(book)

        db.add(borrow_record)
        db.commit()

        return schemas.ReturnResponse(message="Book returned successfully", fine=fine)

    def renew_book(self, db: Session, borrow_id: str) -> models.BorrowRecord:
        borrow_record = crud.borrow_record.get_by_borrow_id(db, borrow_id=borrow_id)
        if not borrow_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow record not found")
        if borrow_record.status != BorrowStatus.BORROWED:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only books in 'borrowed' status can be renewed.")
        if borrow_record.renewal_count >= 2: # Max 2 renewals
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum renewal limit reached.")
        
        # Check for reservations
        reservations = crud.reservation_record.get_waiting_list_for_book(db, isbn=borrow_record.isbn)
        if reservations:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot renew a reserved book.")

        borrow_record.due_date += timedelta(days=30) # Renew for 30 days
        borrow_record.renewal_count += 1
        db.add(borrow_record)
        db.commit()
        db.refresh(borrow_record)
        return borrow_record

    def reserve_book(self, db: Session, reservation_request: schemas.ReservationCreateAction) -> models.ReservationRecord:
        reader = crud.reader.get_by_reader_id(db, reader_id=reservation_request.reader_id)
        if not reader:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")

        book = crud.book.get_by_isbn(db, isbn=reservation_request.isbn)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        
        if book.available_stock > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is available for borrowing, no reservation needed.")

        if crud.reservation_record.get_active_reservation_by_book(db, reader_id=reader.reader_id, isbn=book.isbn):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reserved this book.")

        new_reservation_schema = schemas.ReservationRecordCreate(
            reservation_id=str(uuid.uuid4()),
            reader_id=reader.reader_id,
            isbn=book.isbn
        )
        new_reservation = crud.reservation_record.create(db, obj_in=new_reservation_schema)
        return new_reservation

borrowing_service = BorrowingService()
