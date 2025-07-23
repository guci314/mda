import enum
from datetime import datetime, date
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from .reader import Reader
    from .book import Book

class BorrowStatus(enum.Enum):
    BORROWED = "借阅中"
    RETURNED = "已归还"
    OVERDUE = "已逾期"
    LOST = "已丢失"

class BorrowRecord(Base):
    __tablename__ = 'borrow_records'

    borrow_id: Mapped[str] = mapped_column(String(50), primary_key=True, comment="借阅编号")
    reader_id: Mapped[str] = mapped_column(ForeignKey('readers.reader_id'), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(ForeignKey('books.isbn'), nullable=False, index=True)
    borrow_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, comment="借阅日期")
    due_date: Mapped[date] = mapped_column(Date, nullable=False, comment="应还日期")
    return_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="实际归还日期")
    renewal_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="续借次数")
    status: Mapped[BorrowStatus] = mapped_column(
        SQLAlchemyEnum(BorrowStatus), nullable=False, default=BorrowStatus.BORROWED, comment="状态"
    )
    fine: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, default=0.0, comment="罚金")

    reader: Mapped["Reader"] = relationship("Reader", back_populates="borrow_records")
    book: Mapped["Book"] = relationship("Book", back_populates="borrow_records")
