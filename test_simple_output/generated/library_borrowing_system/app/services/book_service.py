from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app import crud, schemas, models

class BookService:
    def create_book(self, db: Session, *, book: schemas.BookCreate) -> models.Book:
        """
        Creates a new book.
        """
        db_book = crud.book.get_by_isbn(db, isbn=book.isbn)
        if db_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists.",
            )
        return crud.book.create(db, obj_in=book)

    def get_book(self, db: Session, *, isbn: str) -> Optional[models.Book]:
        """
        Retrieves a book by its ISBN.
        """
        return crud.book.get_by_isbn(db, isbn=isbn)

    def update_book(self, db: Session, *, isbn: str, book_update: schemas.BookUpdate) -> models.Book:
        """
        Updates a book's information.
        """
        db_book = self.get_book(db, isbn=isbn)
        if not db_book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        
        return crud.book.update(db, db_obj=db_book, obj_in=book_update)

    def search_books(self, db: Session, *, query: Optional[str], category: Optional[str]) -> List[models.Book]:
        """
        Searches for books by query (title, author, ISBN) or category.
        """
        return crud.book.search(db, query=query, category=category)

    def remove_book(self, db: Session, *, isbn: str) -> models.Book:
        """
        Marks a book as 'REMOVED'. Does not delete the record.
        """
        db_book = self.get_book(db, isbn=isbn)
        if not db_book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        
        update_data = schemas.BookUpdate(status=models.BookStatus.REMOVED)
        return crud.book.update(db, db_obj=db_book, obj_in=update_data)

book = BookService()
