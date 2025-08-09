from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import BookDB
from app.models.pydantic import BookCreate, BookResponse
from app.repositories.book_repository import BookRepository

class BookService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BookRepository(db)

    async def add_book(self, book_data: BookCreate) -> BookResponse:
        if book_data.available_quantity > book_data.total_quantity:
            raise ValueError("可借数量不能大于总库存")
        book = BookDB(**book_data.dict(), status="在架")
        await self.repository.save(book)
        return BookResponse.from_orm(book)

    async def update_book(self, isbn: str, book_data: BookCreate) -> BookResponse:
        book = await self.repository.get_by_isbn(isbn)
        if not book:
            raise ValueError("图书不存在")
        for key, value in book_data.dict().items():
            setattr(book, key, value)
        await self.repository.save(book)
        return BookResponse.from_orm(book)

    async def remove_book(self, isbn: str) -> None:
        book = await self.repository.get_by_isbn(isbn)
        if not book:
            raise ValueError("图书不存在")
        book.status = "已下架"
        await self.repository.save(book)