# 平台特定模型 (PSM): 图书借阅系统 (FastAPI)

本文档基于平台无关模型 (PIM) 进行转换，定义了使用 FastAPI 框架构建图书借阅系统的具体技术实现方案。

## 1. 技术架构说明

本系统将采用基于 **FastAPI** 的现代 Web 架构。选择 FastAPI 的主要原因包括：

- **高性能**: 基于 Starlette 和 Pydantic，提供与 NodeJS 和 Go 相媲美的性能。
- **类型安全**: 强制使用 Python 类型提示，通过 Pydantic 实现强大的数据验证、序列化和反序列化，减少运行时错误。
- **开发效率**: 自动生成交互式 API 文档（Swagger UI 和 ReDoc），简化了 API 的调试和协作。
- **依赖注入**: 内置强大的依赖注入系统，便于管理数据库会话、服务依赖和配置，实现代码解耦和可测试性。
- **异步支持**: 天然支持 `async/await`，适用于高并发的 I/O 密集型操作，如数据库查询。

架构将分层设计，主要包括：

- **表示层 (API Routers)**: 负责处理 HTTP 请求，调用业务逻辑，并返回响应。使用 FastAPI 的 `APIRouter`。
- **业务逻辑层 (Services)**: 实现 PIM 中定义的业务操作和规则，保持技术无关性。
- **数据访问层 (Models/ORM)**: 使用 SQLAlchemy 定义数据模型并与数据库交互。
- **数据验证层 (Schemas)**: 使用 Pydantic 定义 API 的数据结构，用于请求和响应的验证与序列化。

## 2. 数据模型设计 (SQLAlchemy)

使用 SQLAlchemy 2.0 作为 ORM，数据库选择 PostgreSQL（推荐用于生产）或 SQLite（用于开发和测试）。

### 数据库表定义

以下是 PIM 实体到 SQLAlchemy 模型的映射。

```python
# app/models.py
import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Date, DateTime,
    Enum as SQLAlchemyEnum, ForeignKey, Numeric, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Enums defined in PIM
class BookStatus(enum.Enum):
    ON_SHELF = "在架"
    OFF_SHELF = "已下架"

class ReaderType(enum.Enum):
    STUDENT = "学生"
    TEACHER = "教师"
    STAFF = "社会人员"

class ReaderStatus(enum.Enum):
    NORMAL = "正常"
    FROZEN = "冻结"
    CANCELLED = "注销"

class BorrowStatus(enum.Enum):
    BORROWED = "借阅中"
    RETURNED = "已归还"
    OVERDUE = "已逾期"
    LOST = "已丢失"

class ReservationStatus(enum.Enum):
    WAITING = "等待中"
    AVAILABLE = "可借阅"
    CANCELLED = "已取消"
    COMPLETED = "已完成"

class Book(Base):
    __tablename__ = 'books'
    isbn = Column(String(20), primary_key=True, comment="国际标准书号")
    title = Column(String(255), nullable=False, comment="书名")
    author = Column(String(100), nullable=False, comment="作者")
    publisher = Column(String(100), nullable=False, comment="出版社")
    publish_year = Column(Integer, nullable=False, comment="出版年份")
    category = Column(String(50), nullable=False, comment="分类")
    total_stock = Column(Integer, nullable=False, comment="总库存")
    available_stock = Column(Integer, nullable=False, comment="可借数量")
    location = Column(String(100), nullable=False, comment="位置")
    summary = Column(Text, nullable=True, comment="简介")
    status = Column(SQLAlchemyEnum(BookStatus), nullable=False, default=BookStatus.ON_SHELF, comment="状态")

    borrow_records = relationship("BorrowRecord", back_populates="book")
    reservation_records = relationship("ReservationRecord", back_populates="book")

    __table_args__ = (
        Index('idx_book_title', 'title'),
        Index('idx_book_author', 'author'),
    )

class Reader(Base):
    __tablename__ = 'readers'
    reader_id = Column(String(50), primary_key=True, comment="读者编号")
    name = Column(String(100), nullable=False, comment="姓名")
    id_card_number = Column(String(18), nullable=False, unique=True, comment="身份证号")
    phone_number = Column(String(15), nullable=False, comment="手机号")
    email = Column(String(100), nullable=True, unique=True, comment="邮箱")
    reader_type = Column(SQLAlchemyEnum(ReaderType), nullable=False, comment="读者类型")
    registration_date = Column(DateTime, nullable=False, default=datetime.utcnow, comment="注册日期")
    valid_until = Column(Date, nullable=False, comment="���效期至")
    status = Column(SQLAlchemyEnum(ReaderStatus), nullable=False, default=ReaderStatus.NORMAL, comment="状态")
    credit_score = Column(Integer, nullable=False, default=100, comment="信用分")

    borrow_records = relationship("BorrowRecord", back_populates="reader")
    reservation_records = relationship("ReservationRecord", back_populates="reader")

class BorrowRecord(Base):
    __tablename__ = 'borrow_records'
    borrow_id = Column(String(50), primary_key=True, comment="借阅编号")
    reader_id = Column(String(50), ForeignKey('readers.reader_id'), nullable=False, index=True)
    isbn = Column(String(20), ForeignKey('books.isbn'), nullable=False, index=True)
    borrow_date = Column(DateTime, nullable=False, default=datetime.utcnow, comment="借阅日期")
    due_date = Column(Date, nullable=False, comment="应还日期")
    return_date = Column(DateTime, nullable=True, comment="实际归还日期")
    renewal_count = Column(Integer, nullable=False, default=0, comment="续借次数")
    status = Column(SQLAlchemyEnum(BorrowStatus), nullable=False, default=BorrowStatus.BORROWED, comment="状态")
    fine = Column(Numeric(10, 2), nullable=True, default=0.0, comment="罚金")

    reader = relationship("Reader", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")

class ReservationRecord(Base):
    __tablename__ = 'reservation_records'
    reservation_id = Column(String(50), primary_key=True, comment="预约编号")
    reader_id = Column(String(50), ForeignKey('readers.reader_id'), nullable=False, index=True)
    isbn = Column(String(20), ForeignKey('books.isbn'), nullable=False, index=True)
    reservation_date = Column(DateTime, nullable=False, default=datetime.utcnow, comment="预约日期")
    status = Column(SQLAlchemyEnum(ReservationStatus), nullable=False, default=ReservationStatus.WAITING, comment="预约状态")
    notification_date = Column(DateTime, nullable=True, comment="通知日期")
    expiry_date = Column(DateTime, nullable=True, comment="过期日期")

    reader = relationship("Reader", back_populates="reservation_records")
    book = relationship("Book", back_populates="reservation_records")
```

## 3. API 接口设计 (RESTful)

使用 Pydantic v2 定义请求和响应的数据模式，确保 API 的健壮性。

### 数据模式 (Schemas)

```python
# app/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .models import BookStatus, ReaderType, ReaderStatus, BorrowStatus, ReservationStatus

# --- Book Schemas ---
class BookBase(BaseModel):
    isbn: str = Field(..., max_length=20)
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=100)
    publisher: str = Field(..., max_length=100)
    publish_year: int
    category: str = Field(..., max_length=50)
    total_stock: int = Field(..., gt=0)
    available_stock: int
    location: str = Field(..., max_length=100)
    summary: Optional[str] = None
    status: BookStatus = BookStatus.ON_SHELF

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=100)
    # ... other updatable fields

class Book(BookBase):
    class Config:
        orm_mode = True

# --- Reader Schemas ---
class ReaderBase(BaseModel):
    name: str = Field(..., max_length=100)
    id_card_number: str = Field(..., max_length=18)
    phone_number: str = Field(..., max_length=15)
    email: Optional[EmailStr] = None
    reader_type: ReaderType

class ReaderCreate(ReaderBase):
    pass

class ReaderUpdate(BaseModel):
    phone_number: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None

class Reader(ReaderBase):
    reader_id: str
    registration_date: datetime
    valid_until: date
    status: ReaderStatus
    credit_score: int

    class Config:
        orm_mode = True

# --- Borrowing Schemas ---
class BorrowCreate(BaseModel):
    reader_id: str
    isbn: str

class BorrowRecord(BaseModel):
    borrow_id: str
    reader_id: str
    isbn: str
    borrow_date: datetime
    due_date: date
    status: BorrowStatus

    class Config:
        orm_mode = True

# ... other schemas for Reservation, Return, etc.
```

### API 端点 (Endpoints)

#### 图书管理 (Book Management)

- **`POST /books/`**: 添加新图书
  - **Request Body**: `BookCreate`
  - **Response (201 Created)**: `Book`
  - **Response (422 Unprocessable Entity)**: 验证错误
- **`PUT /books/{isbn}`**: 更新图书信息
  - **Request Body**: `BookUpdate`
  - **Response (200 OK)**: `Book`
  - **Response (404 Not Found)**: 图书不存在
- **`POST /books/{isbn}/remove`**: 下架图书
  - **Response (200 OK)**: `{"message": "Book removed successfully"}`
  - **Response (404 Not Found)**: 图书不存在
  - **Response (400 Bad Request)**: 图书不满足下架条件
- **`GET /books/`**: 查询图书
  - **Query Params**: `q: str`, `category: str`
  - **Response (200 OK)**: `List[Book]`

#### 读者管理 (Reader Management)

- **`POST /readers/`**: 注册新读者
  - **Request Body**: `ReaderCreate`
  - **Response (201 Created)**: `Reader`
  - **Response (422 Unprocessable Entity)**: 验证错误
- **`PUT /readers/{reader_id}`**: 更新读者信息
  - **Request Body**: `ReaderUpdate`
  - **Response (200 OK)**: `Reader`
  - **Response (404 Not Found)**: 读者不存在
- **`POST /readers/{reader_id}/freeze`**: 冻结读者
  - **Response (200 OK)**: `Reader`
  - **Response (404 Not Found)**: 读者不存在
- **`POST /readers/{reader_id}/unfreeze`**: 解��读者
  - **Response (200 OK)**: `Reader`
  - **Response (404 Not Found)**: 读者不存在

#### 借阅服务 (Borrowing Service)

- **`POST /borrow/`**: 借阅图书
  - **Request Body**: `BorrowCreate`
  - **Response (201 Created)**: `BorrowRecord`
  - **Response (400 Bad Request)**: 不满足借阅条件（如信用分不足、库存不足等）
  - **Response (404 Not Found)**: 读者或图书不存在
- **`POST /return/{borrow_id}`**: 归还图书
  - **Response (200 OK)**: `{"message": "Book returned successfully", "fine": 5.50}`
  - **Response (404 Not Found)**: 借阅记录不存在
- **`POST /renew/{borrow_id}`**: 续借图书
  - **Response (200 OK)**: `BorrowRecord` (with updated `due_date`)
  - **Response (400 Bad Request)**: 不满足续借条件
- **`POST /reservations/`**: 预约图书
  - **Request Body**: `{"reader_id": "...", "isbn": "..."}`
  - **Response (201 Created)**: `ReservationRecord`
  - **Response (400 Bad Request)**: 不满足预约条件

## 4. 业务逻辑实现方案

业务逻辑将在 `app/services.py` 中实现。API 路由函数将通过 FastAPI 的依赖注入系统获取数据库会话 (`db: Session`) 和服务实例，然后调用相应的服务方法。

**示例：借阅图书服务**

```python
# app/services.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import models, schemas

class BorrowingService:
    def borrow_book(self, db: Session, borrow_request: schemas.BorrowCreate):
        reader = db.query(models.Reader).filter(models.Reader.reader_id == borrow_request.reader_id).first()
        if not reader:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")

        # 1. 检查读者状态
        if reader.status != models.ReaderStatus.NORMAL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reader account is not normal")

        # 2. 检查信用分
        if reader.credit_score < 60:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient credit score")

        # 3. 检查借阅限额 (伪代码)
        # current_borrows = count_current_borrows(db, reader.reader_id)
        # limit = get_borrow_limit(reader.reader_type)
        # if current_borrows >= limit:
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Borrowing limit reached")

        book = db.query(models.Book).filter(models.Book.isbn == borrow_request.isbn).first()
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        # 4. 检查图书可借数量
        if book.available_stock <= 0:
            # 检查预约逻辑...
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No available stock")

        # 5. 创建借阅记录 (伪代码)
        # new_record = create_borrow_record(...)
        
        # 6. 更新图书可借数量
        book.available_stock -= 1
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        return new_record

# app/routers/borrowing.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import services, schemas
from ..database import get_db

router = APIRouter(prefix="/borrow", tags=["Borrowing"])
borrowing_service = services.BorrowingService()

@router.post("/", response_model=schemas.BorrowRecord, status_code=status.HTTP_201_CREATED)
def borrow_a_book(borrow_request: schemas.BorrowCreate, db: Session = Depends(get_db)):
    return borrowing_service.borrow_book(db=db, borrow_request=borrow_request)
```

## 5. 项目结构说明

推荐采用以下模块化的项目结构：

```
/library_borrowing_system/
|
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 应用实例和主路由
│   ├── models.py           # SQLAlchemy 数据模型
│   ├── schemas.py          # Pydantic 数据模式
│   ├── services.py         # 业务逻辑服务
│   ├── crud.py             # 底层 CRUD 函数 (可选)
│   ├── database.py         # 数据库连接和会话管理
│   └── routers/
│       ├── __init__.py
│       ├── books.py          # 图书管理路由
│       ├── readers.py        # 读者管理路由
│       └── borrowing.py      # 借阅/归还/预约路由
|
├── tests/                  # pytest 测试目录
│   ├── __init__.py
│   ├── test_books_api.py
│   └── test_borrowing_logic.py
|
├── .env                    # 环境变量 (数据库连接等)
├── .gitignore
└── requirements.txt        # 项目依赖
```

## 6. 技术栈和依赖列表

以下是 `requirements.txt` 文件的建议内容：

```txt
# Web Framework
fastapi
uvicorn[standard]

# ORM and Database Driver
sqlalchemy
psycopg2-binary  # For PostgreSQL
# alembic       # For database migrations (recommended)

# Data Validation
pydantic[email]

# Testing
pytest
httpx          # For making async requests to the API in tests

# Utilities
python-dotenv  # For managing environment variables
```

此 PSM 文档为后续的开发工作提供了清晰、具体的技术蓝图。
