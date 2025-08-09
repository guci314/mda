from sqlalchemy import Column, String, Integer, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import BookStatus


class BookDB(Base):
    __tablename__ = "books"

    isbn = Column(String(20), primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(50), nullable=False)
    publisher = Column(String(50), nullable=False)
    publish_year = Column(Integer, nullable=False)
    category = Column(String(20), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    location = Column(String(20), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(BookStatus), nullable=False, default=BookStatus.AVAILABLE)

    # 关系
    borrow_records = relationship("BorrowRecordDB", back_populates="book")
    reservation_records = relationship("ReservationRecordDB", back_populates="book")