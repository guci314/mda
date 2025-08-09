from sqlalchemy import Column, String, Integer, Enum as SQLEnum, DateTime, Date
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import ReaderType, ReaderStatus
from datetime import datetime


class Reader(Base):
    __tablename__ = "readers"

    reader_id = Column(String(36), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    id_card = Column(String(18), nullable=False, unique=True)
    phone = Column(String(11), nullable=False)
    email = Column(String(100))
    reader_type = Column(SQLEnum(ReaderType), nullable=False)
    register_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_until = Column(Date, nullable=False)
    status = Column(SQLEnum(ReaderStatus), nullable=False, default=ReaderStatus.ACTIVE)
    credit_score = Column(Integer, nullable=False, default=100)

    # 关系
    borrow_records = relationship("BorrowRecord", back_populates="reader")
    reservation_records = relationship("ReservationRecord", back_populates="reader")