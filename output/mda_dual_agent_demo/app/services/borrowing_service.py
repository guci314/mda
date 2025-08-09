from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import BorrowRecordDB
from app.models.pydantic import BorrowRecordResponse
from app.repositories.borrow_record_repository import BorrowRecordRepository
from app.repositories.book_repository import BookRepository
from app.repositories.reader_repository import ReaderRepository

class BorrowingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.borrow_repo = BorrowRecordRepository(db)
        self.book_repo = BookRepository(db)
        self.reader_repo = ReaderRepository(db)

    async def borrow_book(self, reader_id: str, isbn: str) -> BorrowRecordResponse:
        reader = await self.reader_repo.get_by_id(reader_id)
        if not reader or reader.status != "正常":
            raise ValueError("读者状态异常")
        book = await self.book_repo.get_by_isbn(isbn)
        if not book or book.status != "在架" or book.available_quantity <= 0:
            raise ValueError("图书不可借")
        book.available_quantity -= 1
        await self.book_repo.save(book)
        borrow = BorrowRecordDB(
            reader_id=reader_id,
            isbn=isbn,
            borrow_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            status="借阅中"
        )
        await self.borrow_repo.save(borrow)
        return BorrowRecordResponse.from_orm(borrow)

    async def return_book(self, borrow_id: str) -> None:
        borrow = await self.borrow_repo.get_by_id(borrow_id)
        if not borrow or borrow.status != "借阅中":
            raise ValueError("借阅记录无效")
        book = await self.book_repo.get_by_isbn(borrow.isbn)
        book.available_quantity += 1
        await self.book_repo.save(book)
        borrow.return_date = datetime.now()
        borrow.status = "已归还"
        await self.borrow_repo.save(borrow)

    async def renew_book(self, borrow_id: str) -> datetime:
        borrow = await self.borrow_repo.get_by_id(borrow_id)
        if not borrow or borrow.status != "借阅中":
            raise ValueError("借阅记录无效")
        if borrow.renew_count >= 2:
            raise ValueError("已达最大续借次数")
        borrow.due_date += timedelta(days=30)
        borrow.renew_count += 1
        await self.borrow_repo.save(borrow)
        return borrow.due_date