from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.book import BookDB
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.enums import BookStatus
import uuid


class BookService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_books(self, skip: int = 0, limit: int = 100) -> List[BookResponse]:
        """获取所有图书列表"""
        books = self.db.query(BookDB).offset(skip).limit(limit).all()
        return [BookResponse.from_orm(book) for book in books]

    def get_book_by_isbn(self, isbn: str) -> Optional[BookResponse]:
        """根据ISBN获取图书"""
        book = self.db.query(BookDB).filter(BookDB.isbn == isbn).first()
        if book:
            return BookResponse.from_orm(book)
        return None

    def add_book(self, book_data: BookCreate) -> BookResponse:
        """添加新图书"""
        if book_data.available_quantity > book_data.total_quantity:
            raise ValueError("可借数量不能大于总库存")
        
        # 检查ISBN是否已存在
        existing_book = self.db.query(BookDB).filter(BookDB.isbn == book_data.isbn).first()
        if existing_book:
            raise ValueError(f"ISBN {book_data.isbn} 已存在")
        
        db_book = BookDB(**book_data.dict())
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return BookResponse.from_orm(db_book)

    def update_book(self, isbn: str, book_data: BookUpdate) -> BookResponse:
        """更新图书信息"""
        book = self.db.query(BookDB).filter(BookDB.isbn == isbn).first()
        if not book:
            raise ValueError(f"图书 {isbn} 不存在")
        
        update_data = book_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(book, field, value)
        
        # 验证可借数量不超过总库存
        if book.available_quantity > book.total_quantity:
            raise ValueError("可借数量不能大于总库存")
        
        self.db.commit()
        self.db.refresh(book)
        return BookResponse.from_orm(book)

    def remove_book(self, isbn: str) -> None:
        """下架图书"""
        book = self.db.query(BookDB).filter(BookDB.isbn == isbn).first()
        if not book:
            raise ValueError(f"图书 {isbn} 不存在")
        
        if book.available_quantity != book.total_quantity:
            raise ValueError("存在未归还的图书，无法下架")
        
        book.status = BookStatus.REMOVED
        self.db.commit()

    def search_books(self, keyword: str = None, category: str = None) -> List[BookResponse]:
        """搜索图书"""
        query = self.db.query(BookDB)
        
        if keyword:
            query = query.filter(
                (BookDB.title.contains(keyword)) |
                (BookDB.author.contains(keyword)) |
                (BookDB.publisher.contains(keyword))
            )
        
        if category:
            query = query.filter(BookDB.category == category)
        
        books = query.all()
        return [BookResponse.from_orm(book) for book in books]