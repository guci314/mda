from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .services import BookService, ReaderService, BorrowingService, ReservationService

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    return BookService(db)

def get_reader_service(db: Session = Depends(get_db)) -> ReaderService:
    return ReaderService(db)

def get_borrowing_service(db: Session = Depends(get_db)) -> BorrowingService:
    return BorrowingService(db)

def get_reservation_service(db: Session = Depends(get_db)) -> ReservationService:
    return ReservationService(db)