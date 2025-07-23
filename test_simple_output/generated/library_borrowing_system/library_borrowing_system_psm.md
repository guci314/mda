# 平台特定模型 (PSM): 图书借阅系统 (FastAPI)

本文档基于平台无关模型 (PIM) 进行转换，旨在为使用 FastAPI 框架构建图书借阅系统提供一个详细、可执行的平台特定模型 (PSM)。

## 1. 技术架构

系统将采用经典的分层架构，以实现关注点分离 (Separation of Concerns)，提高代码的可维护性、可扩展性和可测试性。

- **API 层 (API Layer)**: 使用 **FastAPI** 构建，负责处理 HTTP 请求、路由、数据验证和序列化。该层直接与客户端交互，调用服务层来处理业务逻辑。
- **服务层 (Service Layer)**: 独立的业务逻辑核心。封装 PIM 中定义的所有业务操作和规则，不直接依赖于 FastAPI 或数据库 ORM 的特定实现细节，通过依赖注入 (Dependency Injection) 获取数据访问层的能力。
- **数据访问层 (Data Access Layer / CRUD Layer)**: 使用 **SQLAlchemy 2.0** 作为 ORM，负责与 **PostgreSQL** 数据库进行交互。该层将定义数据模型并提供对数据的增删改查 (CRUD) 操作。
- **数据验证层 (Schema Layer)**: 使用 **Pydantic V2** 定义数据传输对象 (DTOs)，用于 API 层的数据验证、序列化以及与服务层的数据交换。

FastAPI 的依赖注入系统 (`Depends`) 将被广泛用于管理数据库会话 (`Session`) 和服务实例的生命周期，确保代码的解耦和高效。

## 2. 数据模型设计 (SQLAlchemy & Pydantic)

数据模型将分为两部分：SQLAlchemy 模型用于数据库表映射，Pydantic 模型用于 API 数据验证和序列化。

### 2.1. 枚举类型 (Enums)

使用 Python 内置的 `enum` 模块来定义 PIM 中的枚举类型。

```python
# app/models/enums.py
import enum

class BookStatus(str, enum.Enum):
    ON_SHELF = "在架"
    REMOVED = "已下架"

class ReaderType(str, enum.Enum):
    STUDENT = "学生"
    TEACHER = "教师"
    STAFF = "社会人员"

class ReaderStatus(str, enum.Enum):
    NORMAL = "正常"
    FROZEN = "冻结"
    CANCELLED = "注销"

class BorrowStatus(str, enum.Enum):
    BORROWED = "借阅中"
    RETURNED = "已归还"
    OVERDUE = "已逾期"
    LOST = "已丢失"

class ReservationStatus(str, enum.Enum):
    WAITING = "等待中"
    AVAILABLE = "可借阅"
    CANCELLED = "已取消"
    COMPLETED = "已完成"
```

### 2.2. SQLAlchemy 模型 (ORM Models)

定义数据库表结构，包含字段类型、约束、索引和关系。

```python
# app/models/book.py
from sqlalchemy import Column, String, Integer, Text, Enum
from app.db.base_class import Base
from .enums import BookStatus

class Book(Base):
    __tablename__ = "books"
    isbn = Column(String(20), primary_key=True, index=True, unique=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(100), nullable=False)
    publisher = Column(String(100), nullable=False)
    publish_year = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    total_stock = Column(Integer, nullable=False)
    available_count = Column(Integer, nullable=False)
    location = Column(String(100), nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(Enum(BookStatus), nullable=False, default=BookStatus.ON_SHELF)

# app/models/reader.py
from sqlalchemy import Column, String, Integer, DateTime, Date, Enum
from sqlalchemy.sql import func
from app.db.base_class import Base
from .enums import ReaderType, ReaderStatus

class Reader(Base):
    __tablename__ = "readers"
    reader_id = Column(String(50), primary_key=True, index=True, unique=True)
    name = Column(String(100), nullable=False)
    id_card_number = Column(String(18), nullable=False, unique=True, index=True)
    phone_number = Column(String(15), nullable=False)
    email = Column(String(255), nullable=True, unique=True)
    reader_type = Column(Enum(ReaderType), nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(Date, nullable=False)
    status = Column(Enum(ReaderStatus), nullable=False, default=ReaderStatus.NORMAL)
    credit_score = Column(Integer, nullable=False, default=100)

# app/models/borrow_record.py
from sqlalchemy import Column, String, Integer, DateTime, Date, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from .enums import BorrowStatus

class BorrowRecord(Base):
    __tablename__ = "borrow_records"
    borrow_id = Column(String(50), primary_key=True, index=True, unique=True)
    reader_id = Column(String(50), ForeignKey("readers.reader_id"), nullable=False, index=True)
    isbn = Column(String(20), ForeignKey("books.isbn"), nullable=False, index=True)
    borrow_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    renewal_count = Column(Integer, nullable=False, default=0)
    status = Column(Enum(BorrowStatus), nullable=False, default=BorrowStatus.BORROWED)
    fine = Column(Numeric(10, 2), nullable=True, default=0.0)
    
    reader = relationship("Reader")
    book = relationship("Book")

# app/models/reservation_record.py
# ... 类似地定义 ReservationRecord 模型
```

### 2.3. Pydantic 模型 (Schemas)

定义用于 API 请求和响应的数据结构。

```python
# app/schemas/book.py
from pydantic import BaseModel, Field
from typing import Optional
from app.models.enums import BookStatus

class BookBase(BaseModel):
    isbn: str = Field(..., max_length=20)
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=100)
    # ... 其他字段

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    # ... 其他可更新字段

class Book(BookBase):
    status: BookStatus
    
    class Config:
        from_attributes = True # Pydantic v2, 替代 orm_mode

# app/schemas/reader.py
# ... 类似地定义 ReaderCreate, ReaderUpdate, Reader 等模型

# app/schemas/borrow.py
from pydantic import BaseModel
from datetime import datetime

class BorrowCreate(BaseModel):
    reader_id: str
    isbn: str

class BorrowRecord(BaseModel):
    borrow_id: str
    reader_id: str
    isbn: str
    borrow_date: datetime
    # ... 其他字段
    
    class Config:
        from_attributes = True
```

## 3. API 接口设计 (RESTful)

使用 FastAPI 的 `APIRouter` 来组织路由，实现 RESTful 风格的 API。

### 3.1. 图书管理接口 (`/api/v1/books`)

```python
# app/api/v1/endpoints/books.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, services, dependencies

router = APIRouter()

@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def add_book(book: schemas.BookCreate, db: Session = Depends(dependencies.get_db)):
    """添加一本新书"""
    return services.book.create_book(db=db, book=book)

@router.put("/{isbn}", response_model=schemas.Book)
def update_book_info(isbn: str, book_update: schemas.BookUpdate, db: Session = Depends(dependencies.get_db)):
    """更新图书信息"""
    # ... 调用服务层
    
@router.get("/search", response_model=list[schemas.Book])
def search_books(query: str, db: Session = Depends(dependencies.get_db)):
    """根据书名、作者、ISBN等搜索图书"""
    # ... 调用服务层
```

### 3.2. 读者管理接口 (`/api/v1/readers`)

- `POST /`: 注册新读者 (registerReader)
- `PUT /{reader_id}`: 更新读者信息 (updateReaderInfo)
- `POST /{reader_id}/freeze`: 冻结读者 (freezeReader)
- `POST /{reader_id}/unfreeze`: 解冻读者 (unfreezeReader)
- `GET /{reader_id}/borrow-history`: 查询借阅历史 (getBorrowHistory)

### 3.3. 借阅流程接口 (`/api/v1/borrowing`)

- `POST /borrow`: 借阅图�� (borrowBook)
  - **Request Body**: `{"reader_id": "...", "isbn": "..."}`
  - **Success Response (201)**: `BorrowRecord`
  - **Error Response (400/404/422)**: `{"detail": "错误信息"}`
- `POST /return`: 归还图书 (returnBook)
  - **Request Body**: `{"borrow_id": "..."}`
- `POST /renew`: 续借图书 (renewBook)
  - **Request Body**: `{"borrow_id": "..."}`
- `POST /reserve`: 预约图书 (reserveBook)
  - **Request Body**: `{"reader_id": "...", "isbn": "..."}`
- `GET /overdue`: 查询所有逾期记录 (getOverdueRecords)

## 4. 业务逻辑实现方案 (服务层)

服务层将包含所有核心业务逻辑，保持 API 控制器的简洁。

**示例: 借阅图书服务 (`borrowBook`)**

```python
# app/services/borrowing_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import crud, schemas, models
from datetime import date, timedelta

def borrow_book(db: Session, borrow_request: schemas.BorrowCreate):
    # 1. 获取并检查读者状态
    reader = crud.reader.get(db, id=borrow_request.reader_id)
    if not reader or reader.status != models.ReaderStatus.NORMAL:
        raise HTTPException(status_code=400, detail="读者状态异常，无法借阅")
    
    # 2. 检查信用分
    if reader.credit_score < 60:
        raise HTTPException(status_code=400, detail="信用分不足")
        
    # 3. 检查借阅限额
    # ... (查询读者当前借阅数量，并根据读者类型判断是否超限)
    
    # 4. 检查图书可借数量
    book = crud.book.get(db, id=borrow_request.isbn)
    if not book or book.available_count <= 0:
        raise HTTPException(status_code=404, detail="图书不存在或已全部借出")
        
    # 5. 创建借阅记录
    # ... (计算应还日期，创建 BorrowRecord 对象)
    
    # 6. 更新图书可借数量
    book.available_count -= 1
    
    # 7. 提交事务
    db.add(new_borrow_record)
    db.commit()
    db.refresh(new_borrow_record)
    
    return new_borrow_record
```

## 5. 项目结构

推荐采用模块化的项目结构，便于管理和扩展。

```
/library_borrowing_system
|-- app/
|   |-- __init__.py
|   |-- main.py             # FastAPI 应用实例和全局中间件
|   |-- api/                # API 路由层
|   |   |-- __init__.py
|   |   |-- v1/
|   |   |   |-- __init__.py
|   |   |   |-- api.py      # 聚合所有 v1 版本的路由
|   |   |   `-- endpoints/  # 各个模块的路由文件 (books.py, readers.py)
|   |-- core/               # 应用配置 (settings.py)
|   |-- crud/               # 数据访问层 (crud_book.py, crud_reader.py)
|   |-- db/                 # 数据库会话管理和基类 (session.py, base_class.py)
|   |-- models/             # SQLAlchemy 模型 (book.py, reader.py, enums.py)
|   |-- schemas/            # Pydantic 模型 (book.py, reader.py)
|   |-- services/           # 业务逻辑层 (book_service.py, borrowing_service.py)
|   `-- dependencies.py     # FastAPI 依赖项 (e.g., get_db)
|
|-- tests/                  # Pytest 测试目录
|   |-- __init__.py
|   |-- conftest.py         # 测试配置和 fixtures
|   `-- api/
|       `-- v1/
|           `-- test_books.py
|
|-- .env                    # 环境变量文件 (数据库连接等)
|-- .gitignore
|-- requirements.txt        # 项目依赖
`-- README.md
```

## 6. 技术栈和依赖

以下是 `requirements.txt` 文件的建议内容���

```
# requirements.txt

# Core Framework
fastapi
uvicorn[standard]

# Database & ORM
sqlalchemy
psycopg2-binary  # For PostgreSQL
# alembic        # For database migrations (recommended)

# Data Validation
pydantic[email]

# Environment Management
python-dotenv

# Testing
pytest
httpx            # For making async requests to the app in tests
```

此 PSM 文档为开发团队提供了一个清晰的蓝图。下一步将是基于此文档搭建项目骨架，并逐步实现各个模块的功能。
