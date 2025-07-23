import enum
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, DateTime, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from .reader import Reader
    from .book import Book

class ReservationStatus(enum.Enum):
    WAITING = "等待中"
    AVAILABLE = "可借阅"
    CANCELLED = "已取消"
    COMPLETED = "已完成"

class ReservationRecord(Base):
    __tablename__ = 'reservation_records'

    reservation_id: Mapped[str] = mapped_column(String(50), primary_key=True, comment="预约编号")
    reader_id: Mapped[str] = mapped_column(ForeignKey('readers.reader_id'), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(ForeignKey('books.isbn'), nullable=False, index=True)
    reservation_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="预约日期"
    )
    status: Mapped[ReservationStatus] = mapped_column(
        SQLAlchemyEnum(ReservationStatus), nullable=False, default=ReservationStatus.WAITING, comment="预约状态"
    )
    notification_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="通知日期")
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="过期日期")

    reader: Mapped["Reader"] = relationship("Reader", back_populates="reservation_records")
    book: Mapped["Book"] = relationship("Book", back_populates="reservation_records")
