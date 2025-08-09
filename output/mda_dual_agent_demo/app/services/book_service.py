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
        book_data_dict = book_data.dict()
        book_data_dict['publication_year'] = book_data_dict.pop('publish_year')
        book_data_dict['total_copies'] = book_data_dict.pop('total_quantity')
        book_data_dict['available_copies'] = book_data_dict.pop('available_quantity')
        book = BookDB(**book_data_dict, status="在架")
        await self.repository.save(book)
        return BookResponse.from_orm(book)

    async def update_book(self, isbn: str, book_data: BookCreate) -> BookResponse:
        book = await self.repository.get_by_isbn(isbn)
        if not book:
            raise ValueError("图书不存在")
        book_data_dict = book_data.dict()
        book_data_dict['publication_year'] = book_data_dict.pop('publish_year')
        book_data_dict['total_copies'] = book_data_dict.pop('total_quantity')
        book_data_dict['available_copies'] = book_data_dict.pop('available_quantity')
        for key, value in book_data_dict.items():
            setattr(book, key, value)
        await self.repository.save(book)
        return BookResponse.from_orm(book)

    async def remove_book(self, isbn: str) -> None:
        book = await self.repository.get_by_isbn(isbn)
        if not book:
            raise ValueError("图书不存在")
        book.status = "已下架"
        await self.repository.save(book)