from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException
from ..models.domain import BookDB
from ..models.enums import BookStatus
from ..schemas.schemas import BookCreate, BookResponse
from ..repositories.book_repository import BookRepository


class BookService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = BookRepository(db)

    def add_book(self, book_data: BookCreate) -> BookResponse:
        if book_data.available_quantity > book_data.total_quantity:
            raise HTTPException(status_code=400, detail="可借数量不能大于总库存")
        existing_book = self.repository.get_by_isbn(book_data.isbn)
        if existing_book:
            raise HTTPException(status_code=400, detail="图书已存在")
        book = BookDB(**book_data.model_dump(), status=BookStatus.AVAILABLE)
        self.repository.save(book)
        return BookResponse.model_validate(book)

    def get_book(self, isbn: str) -> Optional[BookResponse]:
        book = self.repository.get_by_isbn(isbn)
        if book is None:
            return None
        return BookResponse.model_validate(book)