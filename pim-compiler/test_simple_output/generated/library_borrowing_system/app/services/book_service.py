from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import crud, models, schemas
from app.models.book import BookStatus

class BookService:
    def get_book_by_isbn(self, db: Session, isbn: str) -> models.Book:
        book = crud.book.get_by_isbn(db, isbn=isbn)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        return book

    def create_book(self, db: Session, book_in: schemas.BookCreate) -> models.Book:
        book = crud.book.get_by_isbn(db, isbn=book_in.isbn)
        if book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists",
            )
        return crud.book.create(db, obj_in=book_in)

    def update_book(self, db: Session, isbn: str, book_in: schemas.BookUpdate) -> models.Book:
        book = self.get_book_by_isbn(db, isbn)
        return crud.book.update(db, db_obj=book, obj_in=book_in)

    def remove_book(self, db: Session, isbn: str) -> models.Book:
        book = self.get_book_by_isbn(db, isbn)
        if book.available_stock != book.total_stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove book with items currently on loan",
            )
        
        update_data = schemas.BookUpdate(status=BookStatus.OFF_SHELF)
        return crud.book.update(db, db_obj=book, obj_in=update_data)

book_service = BookService()
