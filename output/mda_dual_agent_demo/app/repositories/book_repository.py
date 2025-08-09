from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.domain import BookDB as Book
from app.models.enums import BookStatus


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        """根据ISBN获取图书"""
        return self.db.query(Book).filter(Book.isbn == isbn).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Book]:
        """获取所有图书"""
        return self.db.query(Book).offset(skip).limit(limit).all()

    def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Book]:
        """根据分类获取图书"""
        return self.db.query(Book).filter(Book.category == category).offset(skip).limit(limit).all()

    def get_available_books(self, skip: int = 0, limit: int = 100) -> List[Book]:
        """获取可借图书"""
        return self.db.query(Book).filter(
            Book.status == BookStatus.AVAILABLE,
            Book.available_quantity > 0
        ).offset(skip).limit(limit).all()

    def save(self, book: Book) -> Book:
        """保存图书"""
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def update(self, isbn: str, **kwargs) -> Optional[Book]:
        """更新图书信息"""
        book = self.get_by_isbn(isbn)
        if book:
            for key, value in kwargs.items():
                setattr(book, key, value)
            self.db.commit()
            self.db.refresh(book)
        return book

    def delete(self, isbn: str) -> bool:
        """删除图书"""
        book = self.get_by_isbn(isbn)
        if book:
            self.db.delete(book)
            self.db.commit()
            return True
        return False