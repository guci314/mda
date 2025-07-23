from sqlalchemy import Column, String, Integer, DateTime, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.enums import ReaderType, ReaderStatus
from datetime import date as date_type

class Reader(Base):
    __tablename__ = "readers"
    
    reader_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    id_card_number: Mapped[str] = mapped_column(String(18), nullable=False, unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    reader_type: Mapped[ReaderType] = mapped_column(Enum(ReaderType), nullable=False)
    registration_date: Mapped[date_type] = mapped_column(DateTime(timezone=True), server_default=func.now())
    valid_until: Mapped[date_type] = mapped_column(Date, nullable=False)
    status: Mapped[ReaderStatus] = mapped_column(Enum(ReaderStatus), nullable=False, default=ReaderStatus.NORMAL)
    credit_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
