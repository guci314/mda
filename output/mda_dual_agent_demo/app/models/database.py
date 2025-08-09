from sqlalchemy import Column, String, Integer, Enum as SQLEnum, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from app.models.enums import BookStatus, ReaderType, ReaderStatus, BorrowStatus, ReservationStatus

Base = declarative_base()

class BookDB(Base):
    __tablename__ = "books"
    isbn = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    publisher = Column(String, nullable=False)
    publish_year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    total_quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    description = Column(String)
    status = Column(SQLEnum(BookStatus), nullable=False)

class ReaderDB(Base):
    __tablename__ = "readers"
    reader_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    id_card = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    email = Column(String)
    reader_type = Column(SQLEnum(ReaderType), nullable=False)
    register_date = Column(DateTime, nullable=False)
    valid_until = Column(Date, nullable=False)
    status = Column(SQLEnum(ReaderStatus), nullable=False)
    credit_score = Column(Integer, nullable=False, default=100)

class BorrowRecordDB(Base):
    __tablename__ = "borrow_records"
    borrow_id = Column(String, primary_key=True)
    reader_id = Column(String, ForeignKey("readers.reader_id"), nullable=False)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    borrow_date = Column(DateTime, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(DateTime)
    renew_count = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(BorrowStatus), nullable=False)
    fine = Column(Numeric(10, 2))

class ReservationRecordDB(Base):
    __tablename__ = "reservation_records"
    reservation_id = Column(String, primary_key=True)
    reader_id = Column(String, ForeignKey("readers.reader_id"), nullable=False)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    reserve_date = Column(DateTime, nullable=False)
    status = Column(SQLEnum(ReservationStatus), nullable=False)
    notify_date = Column(DateTime)
    expire_date = Column(DateTime)