from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate

class CRUDBook(CRUDBase[Book, BookCreate, BookUpdate]):
    def get_by_isbn(self, db: Session, *, isbn: str) -> Optional[Book]:
        return db.query(Book).filter(Book.isbn == isbn).first()

    def create(self, db: Session, *, obj_in: BookCreate) -> Book:
        db_obj = Book(
            isbn=obj_in.isbn,
            title=obj_in.title,
            author=obj_in.author,
            publisher=obj_in.publisher,
            publish_year=obj_in.publish_year,
            category=obj_in.category,
            total_stock=obj_in.total_stock,
            available_stock=obj_in.available_stock,
            location=obj_in.location,
            summary=obj_in.summary,
            status=obj_in.status,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def search(
        self, db: Session, *, q: Optional[str] = None, category: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[Book]:
        query = db.query(self.model)
        if q:
            query = query.filter(
                (Book.title.ilike(f"%{q}%")) | (Book.author.ilike(f"%{q}%"))
            )
        if category:
            query = query.filter(Book.category == category)
        
        return query.offset(skip).limit(limit).all()

book = CRUDBook(Book)
