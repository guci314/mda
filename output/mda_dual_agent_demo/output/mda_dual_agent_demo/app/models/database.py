"""
SQLAlchemy数据库模型定义
"""
from sqlalchemy import Column, String, Integer, Enum as SQLEnum, ForeignKey, DateTime, Date, Numeric, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from .enums import BookStatus, ReaderType, ReaderStatus, BorrowStatus, ReservationStatus

Base = declarative_base()


class BookDB(Base):
    """图书数据库模型"""
    __tablename__ = "books"
    
    isbn = Column(String(20), primary_key=True, comment="ISBN号")
    title = Column(String(100), nullable=False, comment="书名")
    author = Column(String(50), nullable=False, comment="作者")
    publisher = Column(String(50), nullable=False, comment="出版社")
    publish_year = Column(Integer, nullable=False, comment="出版年份")
    category = Column(String(20), nullable=False, comment="分类")
    total_quantity = Column(Integer, nullable=False, comment="总库存")
    available_quantity = Column(Integer, nullable=False, comment="可借数量")
    location = Column(String(20), nullable=False, comment="存放位置")
    description = Column(Text, comment="图书描述")
    status = Column(SQLEnum(BookStatus), nullable=False, default=BookStatus.AVAILABLE, comment="图书状态")
    
    # 关系
    borrow_records = relationship("BorrowRecordDB", back_populates="book")
    reservation_records = relationship("ReservationRecordDB", back_populates="book")


class ReaderDB(Base):
    """读者数据库模型"""
    __tablename__ = "readers"
    
    reader_id = Column(String(20), primary_key=True, comment="读者ID")
    name = Column(String(50), nullable=False, comment="姓名")
    id_card = Column(String(18), nullable=False, unique=True, comment="身份证号")
    phone = Column(String(11), nullable=False, comment="手机号")
    email = Column(String(100), comment="邮箱")
    reader_type = Column(SQLEnum(ReaderType), nullable=False, comment="读者类型")
    register_date = Column(DateTime, nullable=False, default=datetime.now, comment="注册日期")
    valid_until = Column(Date, nullable=False, comment="有效期至")
    status = Column(SQLEnum(ReaderStatus), nullable=False, default=ReaderStatus.ACTIVE, comment="读者状态")
    credit_score = Column(Integer, nullable=False, default=100, comment="信用分")
    
    # 关系
    borrow_records = relationship("BorrowRecordDB", back_populates="reader")
    reservation_records = relationship("ReservationRecordDB", back_populates="reader")


class BorrowRecordDB(Base):
    """借阅记录数据库模型"""
    __tablename__ = "borrow_records"
    
    borrow_id = Column(String(32), primary_key=True, comment="借阅ID")
    reader_id = Column(String(20), ForeignKey("readers.reader_id"), nullable=False, comment="读者ID")
    isbn = Column(String(20), ForeignKey("books.isbn"), nullable=False, comment="图书ISBN")
    borrow_date = Column(DateTime, nullable=False, default=datetime.now, comment="借阅日期")
    due_date = Column(Date, nullable=False, comment="应还日期")
    return_date = Column(DateTime, comment="实际归还日期")
    renew_count = Column(Integer, nullable=False, default=0, comment="续借次数")
    status = Column(SQLEnum(BorrowStatus), nullable=False, default=BorrowStatus.BORROWED, comment="借阅状态")
    fine = Column(Numeric(10, 2), comment="罚金")
    
    # 关系
    reader = relationship("ReaderDB", back_populates="borrow_records")
    book = relationship("BookDB", back_populates="borrow_records")


class ReservationRecordDB(Base):
    """预约记录数据库模型"""
    __tablename__ = "reservation_records"
    
    reservation_id = Column(String(32), primary_key=True, comment="预约ID")
    reader_id = Column(String(20), ForeignKey("readers.reader_id"), nullable=False, comment="读者ID")
    isbn = Column(String(20), ForeignKey("books.isbn"), nullable=False, comment="图书ISBN")
    reserve_date = Column(DateTime, nullable=False, default=datetime.now, comment="预约日期")
    status = Column(SQLEnum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING, comment="预约状态")
    notify_date = Column(DateTime, comment="通知日期")
    expire_date = Column(DateTime, comment="过期日期")
    
    # 关系
    reader = relationship("ReaderDB", back_populates="reservation_records")
    book = relationship("BookDB", back_populates="reservation_records")