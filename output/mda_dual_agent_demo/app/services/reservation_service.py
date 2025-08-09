from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import ReservationRecordDB
from app.models.pydantic import ReservationRecordResponse
from app.repositories.reservation_record_repository import ReservationRecordRepository
from app.repositories.book_repository import BookRepository
from app.repositories.reader_repository import ReaderRepository

class ReservationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.reservation_repo = ReservationRecordRepository(db)
        self.book_repo = BookRepository(db)
        self.reader_repo = ReaderRepository(db)

    async def reserve_book(self, reader_id: str, isbn: str) -> ReservationRecordResponse:
        reader = await self.reader_repo.get_by_id(reader_id)
        if not reader or reader.status != "正常":
            raise ValueError("读者状态异常")
        book = await self.book_repo.get_by_isbn(isbn)
        if not book or book.status != "在架":
            raise ValueError("图书不可预约")
        reservation = ReservationRecordDB(
            reader_id=reader_id,
            isbn=isbn,
            reserve_date=datetime.now(),
            status="等待中",
            expire_date=datetime.now() + timedelta(days=7)
        )
        await self.reservation_repo.save(reservation)
        return ReservationRecordResponse.from_orm(reservation)