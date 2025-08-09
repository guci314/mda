from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.models.enums import BookStatus, ReaderType, ReaderStatus, BorrowStatus, ReservationStatus
from datetime import datetime

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    
    isbn = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    publisher = Column(String, nullable=False)
    publish_year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    total_quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, nullable=False, default=BookStatus.AVAILABLE)
    
    borrow_records = relationship("BorrowRecord", back_populates="book")
    reservations = relationship("ReservationRecord", back_populates="book")

class Reader(Base):
    __tablename__ = "readers"
    
    reader_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    id_card = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    email = Column(String)
    reader_type = Column(String, nullable=False)
    register_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_until = Column(Date, nullable=False)
    status = Column(String, nullable=False, default=ReaderStatus.ACTIVE)
    credit_score = Column(Integer, nullable=False, default=100)
    
    borrow_records = relationship("BorrowRecord", back_populates="reader")
    reservations = relationship("ReservationRecord", back_populates="reader")

class BorrowRecord(Base):
    __tablename__ = "borrow_records"
    
    borrow_id = Column(String, primary_key=True, index=True)
    reader_id = Column(String, ForeignKey("readers.reader_id"), nullable=False)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    borrow_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(Date, nullable=False)
    return_date = Column(DateTime)
    renew_count = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default=BorrowStatus.BORROWED)
    fine = Column(Numeric(10, 2))
    
    reader = relationship("Reader", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")

class ReservationRecord(Base):
    __tablename__ = "reservation_records"
    
    reservation_id = Column(String, primary_key=True, index=True)
    reader_id = Column(String, ForeignKey("readers.reader_id"), nullable=False)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    reserve_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default=ReservationStatus.PENDING)
    notify_date = Column(DateTime)
    expire_date = Column(DateTime)
    
    reader = relationship("Reader", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")