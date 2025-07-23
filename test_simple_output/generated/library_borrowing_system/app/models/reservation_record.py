from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from app.models.enums import ReservationStatus
from datetime import datetime

class ReservationRecord(Base):
    __tablename__ = "reservation_records"

    reservation_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True, unique=True)
    reader_id: Mapped[str] = mapped_column(String(50), ForeignKey("readers.reader_id"), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(String(20), ForeignKey("books.isbn"), nullable=False, index=True)
    reservation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(Enum(ReservationStatus), nullable=False, default=ReservationStatus.WAITING)
    available_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    pickup_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    reader: Mapped["Reader"] = relationship()
    book: Mapped["Book"] = relationship()
