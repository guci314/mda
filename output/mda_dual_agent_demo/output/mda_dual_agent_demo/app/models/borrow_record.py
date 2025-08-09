from sqlalchemy import Column, String, Integer, Enum as SQLEnum, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import BorrowStatus
from datetime import datetime


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    borrow_id = Column(String(36), primary_key=True, index=True)
    reader_id = Column(String(36), ForeignKey("readers.reader_id"), nullable=False)
    isbn = Column(String(20), ForeignKey("books.isbn"), nullable=False)
    borrow_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(Date, nullable=False)
    return_date = Column(DateTime)
    renew_count = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(BorrowStatus), nullable=False, default=BorrowStatus.BORROWED)
    fine = Column(Numeric(10, 2))

    # 关系
    reader = relationship("Reader", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")