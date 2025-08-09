from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app.services.book_service import BookService
from app.services.reader_service import ReaderService
from app.services.borrowing_service import BorrowingService
from app.services.reservation_service import ReservationService

def get_book_service(db: AsyncSession = Depends(get_async_db)) -> BookService:
    return BookService(db)

def get_reader_service(db: AsyncSession = Depends(get_async_db)) -> ReaderService:
    return ReaderService(db)

def get_borrowing_service(db: AsyncSession = Depends(get_async_db)) -> BorrowingService:
    return BorrowingService(db)

def get_reservation_service(db: AsyncSession = Depends(get_async_db)) -> ReservationService:
    return ReservationService(db)