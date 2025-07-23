import enum
from datetime import datetime, date
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from .borrow_record import BorrowRecord
    from .reservation_record import ReservationRecord

class ReaderType(enum.Enum):
    STUDENT = "学生"
    TEACHER = "教师"
    STAFF = "社会人员"

class ReaderStatus(enum.Enum):
    NORMAL = "正常"
    FROZEN = "冻结"
    CANCELLED = "注销"

class Reader(Base):
    __tablename__ = 'readers'

    reader_id: Mapped[str] = mapped_column(String(50), primary_key=True, comment="读者编号")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="姓名")
    id_card_number: Mapped[str] = mapped_column(String(18), nullable=False, unique=True, comment="身份证号")
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False, comment="手机号")
    email: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, comment="邮箱")
    reader_type: Mapped[ReaderType] = mapped_column(SQLAlchemyEnum(ReaderType), nullable=False, comment="读者类型")
    registration_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="注册日期"
    )
    valid_until: Mapped[date] = mapped_column(Date, nullable=False, comment="有效期至")
    status: Mapped[ReaderStatus] = mapped_column(
        SQLAlchemyEnum(ReaderStatus), nullable=False, default=ReaderStatus.NORMAL, comment="状态"
    )
    credit_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100, comment="信用分")

    borrow_records: Mapped[List["BorrowRecord"]] = relationship("BorrowRecord", back_populates="reader")
    reservation_records: Mapped[List["ReservationRecord"]] = relationship("ReservationRecord", back_populates="reader")
