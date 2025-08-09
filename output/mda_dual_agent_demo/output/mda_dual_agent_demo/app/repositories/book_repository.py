from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.book import Book


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        """根据ISBN获取图书"""
        return self.db.query(Book).filter(Book.isbn == isbn).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Book]:
        """获取所有图书"""
        return self.db.query(Book).offset(skip).limit(limit).all()

    def save(self, book: Book) -> Book:
        """保存图书"""
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def update(self, book: Book) -> Book:
        """更新图书"""
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        """删除图书"""
        self.db.delete(book)
        self.db.commit()