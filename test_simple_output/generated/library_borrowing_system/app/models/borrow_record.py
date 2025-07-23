from sqlalchemy import Column, String, Integer, DateTime, Date, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from app.models.enums import BorrowStatus
from datetime import datetime, date

class BorrowRecord(Base):
    __tablename__ = "borrow_records"
    
    borrow_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True, unique=True)
    reader_id: Mapped[str] = mapped_column(String(50), ForeignKey("readers.reader_id"), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(String(20), ForeignKey("books.isbn"), nullable=False, index=True)
    borrow_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    renewal_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[BorrowStatus] = mapped_column(Enum(BorrowStatus), nullable=False, default=BorrowStatus.BORROWED)
    fine: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True, default=0.0)
    
    reader: Mapped["Reader"] = relationship()
    book: Mapped["Book"] = relationship()
