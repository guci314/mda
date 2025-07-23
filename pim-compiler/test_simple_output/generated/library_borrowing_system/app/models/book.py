import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, Enum as SQLAlchemyEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from .borrow_record import BorrowRecord
    from .reservation_record import ReservationRecord

class BookStatus(enum.Enum):
    ON_SHELF = "在架"
    OFF_SHELF = "已下架"

class Book(Base):
    __tablename__ = 'books'

    isbn: Mapped[str] = mapped_column(String(20), primary_key=True, comment="国际标准书号")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="书名")
    author: Mapped[str] = mapped_column(String(100), nullable=False, comment="作者")
    publisher: Mapped[str] = mapped_column(String(100), nullable=False, comment="出版社")
    publish_year: Mapped[int] = mapped_column(Integer, nullable=False, comment="出版年份")
    category: Mapped[str] = mapped_column(String(50), nullable=False, comment="分类")
    total_stock: Mapped[int] = mapped_column(Integer, nullable=False, comment="总库存")
    available_stock: Mapped[int] = mapped_column(Integer, nullable=False, comment="可借数量")
    location: Mapped[str] = mapped_column(String(100), nullable=False, comment="位置")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="简介")
    status: Mapped[BookStatus] = mapped_column(
        SQLAlchemyEnum(BookStatus), nullable=False, default=BookStatus.ON_SHELF, comment="状态"
    )

    borrow_records: Mapped[List["BorrowRecord"]] = relationship("BorrowRecord", back_populates="book")
    reservation_records: Mapped[List["ReservationRecord"]] = relationship("ReservationRecord", back_populates="book")

    __table_args__ = (
        Index('idx_book_title', 'title'),
        Index('idx_book_author', 'author'),
    )
