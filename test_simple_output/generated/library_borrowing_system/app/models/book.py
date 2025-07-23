from sqlalchemy import Column, String, Integer, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.enums import BookStatus

class Book(Base):
    __tablename__ = "books"
    
    isbn: Mapped[str] = mapped_column(String(20), primary_key=True, index=True, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    publisher: Mapped[str] = mapped_column(String(100), nullable=False)
    publish_year: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    total_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    available_count: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[BookStatus] = mapped_column(Enum(BookStatus), nullable=False, default=BookStatus.ON_SHELF)
