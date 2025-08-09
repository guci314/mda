from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import ReservationStatus
from datetime import datetime


class ReservationRecordDB(Base):
    __tablename__ = "reservation_records"

    reservation_id = Column(String(36), primary_key=True, index=True)
    reader_id = Column(String(36), ForeignKey("readers.reader_id"), nullable=False)
    isbn = Column(String(20), ForeignKey("books.isbn"), nullable=False)
    reserve_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(SQLEnum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING)
    notify_date = Column(DateTime)
    expire_date = Column(DateTime)

    # 关系
    reader = relationship("ReaderDB", back_populates="reservation_records")
    book = relationship("BookDB", back_populates="reservation_records")