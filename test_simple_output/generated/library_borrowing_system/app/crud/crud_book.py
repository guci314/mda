from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate

class CRUDBook(CRUDBase[Book, BookCreate, BookUpdate]):
    def get_by_isbn(self, db: Session, *, isbn: str) -> Optional[Book]:
        return db.query(Book).filter(Book.isbn == isbn).first()

    def search(self, db: Session, *, query: Optional[str], category: Optional[str]) -> List[Book]:
        db_query = db.query(Book)
        if query:
            search_term = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    Book.title.ilike(search_term),
                    Book.author.ilike(search_term),
                    Book.isbn.ilike(search_term),
                )
            )
        if category:
            db_query = db_query.filter(Book.category == category)
        
        return db_query.all()

book = CRUDBook(Book)
