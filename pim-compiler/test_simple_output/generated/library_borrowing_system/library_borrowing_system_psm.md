# 平台特定模型 (PSM): 图书借阅系统 (FastAPI)

本文档基于平台无关模型 (PIM)，为图书借阅系统定义了在 FastAPI 平台上的具体技术实现方案。

## 1. 技术架构

系统将采用基于 **FastAPI** 的分层架构，以实现关注点分离 (Separation of Concerns) 和高可维护性。

- **表示层 (API Layer)**: 使用 FastAPI 的 `APIRouter` 构建 RESTful 接口。负责处理 HTTP 请求、验证输入数据（使用 Pydantic）、序列化响应数据，并将业务逻辑委托给服务层。
- **服务层 (Service Layer)**: 封装核心业务逻辑。例如，`BorrowingService` 将包含借阅、归还和续借图书的完整流程。该层不直接与数据库交互，而是通过 CRUD 层。
- **数据访问层 (CRUD Layer / Repository)**: 负责与数据库的直接交互。提供对每个数据模型的基本增、删、改、查 (CRUD) 操作。这使得业务逻辑与数据访问技术解耦。
- **数据模型层 (DB Layer)**: 使用 **SQLAlchemy 2.0** 定义数据模型，映射到数据库表结构。
- **配置与核心 (Core)**: 管理应用配置（如数据库连接字符串、密钥等）和核心功能（如安全、中间件）。

```mermaid
graph TD
    Client[客户端] -->|HTTP Request| API_Layer[API 层 (FastAPI Routers)]
    API_Layer -->|Call Function| Service_Layer[服务层 (Business Logic)]
    Service_Layer -->|Call CRUD Function| CRUD_Layer[CRUD 层 (Repositories)]
    CRUD_Layer -->|ORM Operation| DB_Layer[数据库层 (SQLAlchemy Models)]
    DB_Layer <--> Database[(PostgreSQL / SQLite)]

    subgraph "应用服务"
        API_Layer
        Service_Layer
        CRUD_Layer
        DB_Layer
    end

    Pydantic[Pydantic V2 Schemas] -->|Data Validation & Serialization| API_Layer
```

## 2. 技术栈和依赖

- **Web 框架**: `fastapi`
- **ASGI 服务器**: `uvicorn[standard]`
- **ORM**: `sqlalchemy` (使用 2.0 异步特性)
- **数据库驱动**: `psycopg2-binary` (用于 PostgreSQL) 或 `aiosqlite` (用于 SQLite 异步)
- **数据验证**: `pydantic[email]` (v2)
- **密码与安全**: `passlib[bcrypt]`
- **测试**: `pytest`, `httpx` (用于异步测试客户端)

**requirements.txt:**
```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
aiosqlite
pydantic[email]
passlib[bcrypt]
pytest
httpx
```

## 3. 项目结构

采用模块化的项目结构，便于扩展和维护。

```
.
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # 聚合所有 v1 路由
│   │       └── endpoints/
│   │           ├── books.py
│   │           ├── readers.py
│   │           └── borrowing.py
│   ├── core/
│   │   ├── config.py             # 配置管理 (Pydantic Settings)
│   │   └── security.py           # 安全相关（未来扩展，如JWT）
│   ├── crud/
│   │   ├── base.py               # CRUD 基类
│   │   ├── crud_book.py
│   │   ├── crud_reader.py
│   │   └── crud_borrow_record.py
│   ├── db/
│   │   ├── base.py               # 声明式基类和所有模型的导入
│   │   └── session.py            # 数据库会话管理
│   ├── models/
│   │   ├── book.py
│   │   ├���─ reader.py
│   │   ├── borrow_record.py
│   │   └── reservation_record.py
│   ├── schemas/
│   │   ├── book.py
│   │   ├── reader.py
│   │   ├── borrow_record.py
│   │   └── reservation_record.py
│   ├── services/
│   │   ├── book_service.py
│   │   ├── reader_service.py
│   │   └── borrowing_service.py
│   └── main.py                   # FastAPI 应用实例和启动
├── tests/                        # 测试目录
│   ├── conftest.py               # Pytest 夹具
│   ├── test_api/
│   └── test_services/
└── requirements.txt
```

## 4. 数据模型设计 (SQLAlchemy)

将 PIM 实体映射为 SQLAlchemy 数据模型。使用 PostgreSQL 作为目标数据库，其类型具有更好的兼容性。

### 枚举类型 (Enums)
```python
# app/models/enums.py
import enum

class BookStatus(str, enum.Enum):
    ON_SHELF = "在架"
    OFF_SHELF = "已下架"

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

### Book 模型
```python
# app/models/book.py
from sqlalchemy import Column, String, Integer, Text, Enum
from app.db.base_class import Base
from .enums import BookStatus

class Book(Base):
    __tablename__ = "books"

    isbn = Column(String(13), primary_key=True, index=True, comment="国际标准书号")
    title = Column(String, nullable=False, index=True, comment="书名")
    author = Column(String, nullable=False, index=True, comment="作者")
    publisher = Column(String, nullable=False, comment="出版社")
    publish_year = Column(Integer, nullable=False, comment="出版年份")
    category = Column(String, nullable=False, index=True, comment="分类")
    total_stock = Column(Integer, nullable=False, comment="总库存")
    available_stock = Column(Integer, nullable=False, comment="可借数量")
    location = Column(String, nullable=False, comment="位置")
    summary = Column(Text, nullable=True, comment="简介")
    status = Column(Enum(BookStatus), nullable=False, default=BookStatus.ON_SHELF, comment="状态")
```

### Reader 模型
```python
# app/models/reader.py
from sqlalchemy import Column, String, Integer, Enum, DateTime, Date
from sqlalchemy.sql import func
from app.db.base_class import Base
from .enums import ReaderType, ReaderStatus

class Reader(Base):
    __tablename__ = "readers"

    reader_id = Column(String, primary_key=True, index=True, comment="读者编号")
    name = Column(String, nullable=False, comment="姓名")
    id_card_number = Column(String, nullable=False, unique=True, index=True, comment="身份证号")
    phone_number = Column(String, nullable=False, comment="手机号")
    email = Column(String, nullable=True, unique=True, index=True, comment="邮箱")
    reader_type = Column(Enum(ReaderType), nullable=False, comment="读者类型")
    registration_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="注册日期")
    valid_until = Column(Date, nullable=False, comment="有效期至")
    status = Column(Enum(ReaderStatus), nullable=False, default=ReaderStatus.NORMAL, comment="状态")
    credit_score = Column(Integer, nullable=False, default=100, comment="信用分")
```

### BorrowRecord 模型
```python
# app/models/borrow_record.py
from sqlalchemy import Column, String, Integer, Enum, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from .enums import BorrowStatus

class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    borrow_id = Column(String, primary_key=True, index=True, comment="借阅编号")
    reader_id = Column(String, ForeignKey("readers.reader_id"), nullable=False, index=True)
    book_isbn = Column(String(13), ForeignKey("books.isbn"), nullable=False, index=True)
    borrow_date = Column(DateTime(timezone=True), nullable=False, comment="借阅日期")
    due_date = Column(Date, nullable=False, comment="应还日期")
    return_date = Column(DateTime(timezone=True), nullable=True, comment="实际归还日期")
    renew_count = Column(Integer, nullable=False, default=0, comment="续借次数")
    status = Column(Enum(BorrowStatus), nullable=False, default=BorrowStatus.BORROWED, comment="状态")
    fine = Column(Numeric(10, 2), nullable=True, default=0.0, comment="罚金")

    reader = relationship("Reader")
    book = relationship("Book")
```

## 5. API 接口设计 (RESTful)

使用 Pydantic v2 进行数据验证和序列化。

### Pydantic Schemas 示例
```python
# app/schemas/book.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from app.models.enums import BookStatus

class BookBase(BaseModel):
    isbn: str = Field(..., max_length=13, description="国际标准书号")
    title: str
    author: str
    publisher: str
    publish_year: int
    category: str
    total_stock: int = Field(..., gt=0)
    available_stock: int
    location: str
    summary: Optional[str] = None
    status: BookStatus = BookStatus.ON_SHELF

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    # ... 其他可更新字段

class BookInDB(BookBase):
    model_config = ConfigDict(from_attributes=True)

    # Pydantic v2 使用 from_attributes 替代 orm_mode
```

### API Endpoints

#### Book Management Service
- **添加图书**: `POST /v1/books/`
  - **Request Body**: `schemas.BookCreate`
  - **Response (201 Created)**: `schemas.BookInDB`
  - **Error (422 Unprocessable Entity)**: 输入验证失败。
- **更新图书信息**: `PUT /v1/books/{isbn}`
  - **Request Body**: `schemas.BookUpdate`
  - **Response (200 OK)**: `schemas.BookInDB`
  - **Error (404 Not Found)**: 图书不存在。
- **下架图书**: `POST /v1/books/{isbn}/remove`
  - **Request Body**: None
  - **Response (200 OK)**: `{"message": "Book removed successfully"}`
  - **Error (404 Not Found)**: 图书不存在。
  - **Error (400 Bad Request)**: 图书不满足下架条件。
- **查询图书**: `GET /v1/books/search`
  - **Query Params**: `query: str`, `category: Optional[str] = None`
  - **Response (200 OK)**: `List[schemas.BookInDB]`

#### Reader Management Service
- **注册读者**: `POST /v1/readers/`
  - **Request Body**: `schemas.ReaderCreate`
  - **Response (201 Created)**: `schemas.ReaderInDB`
- **更新读者信息**: `PUT /v1/readers/{reader_id}`
  - **Request Body**: `schemas.ReaderUpdate`
  - **Response (200 OK)**: `schemas.ReaderInDB`
- **冻结读者**: `POST /v1/readers/{reader_id}/freeze`
  - **Response (200 OK)**: `schemas.ReaderInDB`

#### Borrowing Service
- **借阅图书**: `POST /v1/borrow/`
  - **Request Body**: `schemas.BorrowCreate` (包含 `reader_id`, `isbn`)
  - **Response (201 Created)**: `schemas.BorrowRecordInDB`
  - **Error (400 Bad Request)**: 读者状态异常、信用分不足、库存不足等。
- **归还图书**: `POST /v1/return/{borrow_id}`
  - **Response (200 OK)**: `schemas.BorrowRecordInDB`
  - **Error (404 Not Found)**: 借阅记录不存在。
- **续借图书**: `POST /v1/renew/{borrow_id}`
  - **Response (200 OK)**: `schemas.BorrowRecordInDB`
  - **Error (400 Bad Request)**: 不满足续借条件。
- **预约图书**: `POST /v1/reserve/`
  - **Request Body**: `schemas.ReservationCreate`
  - **Response (201 Created)**: `schemas.ReservationRecordInDB`

## 6. 业务逻辑实现方案

业务逻辑将在 **服务层** 中实现，以���持 API 控制器的简洁。服务层将依赖注入数据库会话和 CRUD 对象。

**示例: 借阅服务 (`app/services/borrowing_service.py`)**
```python
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.core.exceptions import BusinessException # 自定义异常
from datetime import datetime, timedelta

class BorrowingService:
    def __init__(self, db: Session):
        self.db = db

    def borrow_book(self, reader_id: str, isbn: str) -> models.BorrowRecord:
        # 1. 获取读者和图书信息
        reader = crud.reader.get(self.db, id=reader_id)
        book = crud.book.get(self.db, id=isbn)

        # 2. 检查业务规则 (PIM 中定义的流程)
        if not reader or reader.status != "正常":
            raise BusinessException(status_code=400, detail="读者状态异常")
        if reader.credit_score < 60:
            raise BusinessException(status_code=400, detail="信用分不足")
        if book.available_stock <= 0:
            raise BusinessException(status_code=400, detail="图书无可借数量")
        
        # ... 检查借阅限额等其他规则

        # 3. 创建借阅记录
        # ... 计算应还日期
        due_date = datetime.utcnow().date() + timedelta(days=30) # 简化示例
        
        borrow_record_in = schemas.BorrowRecordCreate(
            reader_id=reader_id,
            book_isbn=isbn,
            due_date=due_date
        )
        new_record = crud.borrow_record.create(self.db, obj_in=borrow_record_in)

        # 4. 更新图书库存
        book.available_stock -= 1
        self.db.add(book)
        self.db.commit()
        self.db.refresh(new_record)

        return new_record
```
FastAPI 路由将使用 `Depends` 来注入服务实例。

```python
# app/api/v1/endpoints/borrowing.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.borrowing_service import BorrowingService
from app.db.session import get_db

router = APIRouter()

@router.post("/borrow/", response_model=schemas.BorrowRecordInDB)
def borrow_book_endpoint(
    borrow_request: schemas.BorrowCreate,
    db: Session = Depends(get_db)
):
    service = BorrowingService(db)
    record = service.borrow_book(
        reader_id=borrow_request.reader_id, 
        isbn=borrow_request.isbn
    )
    return record
```

## 7. 测试策略

- **单元测试 (`tests/test_services`)**: 使用 `pytest` 测试服务层中的业务逻辑，例如信用分计算、罚金计算等。可以模拟 (mock) CRUD 层，隔离数据库依赖。
- **集成测试 (`tests/test_api`)**: 使用 FastAPI 的 `TestClient` 和 `httpx.AsyncClient` 对 API 端点进行测试。这将覆盖从 API 请求到数据库操作的完整流程。测试将在一个独立的测试数据库上运行，以确保隔离性。
- **端到端测试**: 模拟真实用户场景，例如一个完整的“预约 -> 借阅 -> 续借 -> 逾期归还”流程。

**测试用例示例 (`tests/test_api/test_borrowing.py`)**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_borrow_book_success(test_db, normal_user, available_book):
    response = client.post(
        "/v1/borrow/",
        json={"reader_id": normal_user.reader_id, "isbn": available_book.isbn}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["reader_id"] == normal_user.reader_id
    assert data["status"] == "借阅中"

def test_borrow_book_insufficient_credit(test_db, low_credit_user, available_book):
    response = client.post(
        "/v1/borrow/",
        json={"reader_id": low_credit_user.reader_id, "isbn": available_book.isbn}
    )
    assert response.status_code == 400
    assert "信用分不足" in response.json()["detail"]
```
其中 `test_db`, `normal_user`, `low_credit_user`, `available_book` 等是定义在 `conftest.py` 中的 pytest fixtures，用于准备测试数据。
