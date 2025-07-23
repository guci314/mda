# 平台特定模型 (PSM): 用户管理系统 (FastAPI)

本文档基于平台无关模型 (PIM) `user_management_with_tests.md`，为用户管理系统定义了在 FastAPI 平台上的具体技术实现方案。

## 1. 技术架构说明

本系统将采用基于 **FastAPI** 的现代 Python Web 框架进行构建。FastAPI 以其高性能、异步支持、依赖注入系统和基于 Pydantic 的强大数据验证能力而被选中。

- **Web 框架**: FastAPI
- **数据库**: 生产环境推荐使用 PostgreSQL，开发和测试环境可使用 SQLite。
- **ORM**: SQLAlchemy 2.0 (异步模式)
- **数据验证**: Pydantic V2
- **认证机制**: JWT (JSON Web Tokens)
- **密码安全**: Passlib 与 bcrypt 哈希算法
- **测试框架**: Pytest

架构核心思想是分层设计，将数据模型、业务逻辑、API 接口和配置清晰分离，以提高代码的可维护性、可扩展性和可测试性。

## 2. 数据模型设计 (SQLAlchemy)

数据模型将 PIM 中的业务实体映射为具体的数据库表结构。我们将使用 SQLAlchemy ORM 来定义模型。

### 2.1. 用户 (User) 模型

`User` 实体将映射到 `users` 表。

- **数据库表名**: `users`
- **关键索引**: 在 `username` 和 `email` 字段上创建唯一索引以保证快速查询和唯一性约束。

**SQLAlchemy 模型定义 (`app/models/user.py`):**
```python
import enum
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING_VERIFICATION = "pending_verification"

class User(Base):
    """用户数据模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    status = Column(
        SQLAlchemyEnum(UserStatus), 
        nullable=False, 
        default=UserStatus.PENDING_VERIFICATION
    )
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
```

## 3. API 接口设计 (RESTful)

API 将遵循 RESTful 设计原则，使用 Pydantic 模型进行请求和响应的数据验证。

### 3.1. 认证接口

#### `POST /auth/token`
- **描述**: 用户登录，验证凭据并返回 JWT 访问令牌。
- **请求体**: `application/x-www-form-urlencoded` (使用 FastAPI 的 `OAuth2PasswordRequestForm`)
  - `username`: str
  - `password`: str
- **响应 (200 OK)**: `application/json`
  ```json
  {
    "access_token": "your_jwt_token",
    "token_type": "bearer"
  }
  ```
- **Pydantic 模型 (`app/schemas/token.py`):**
  ```python
  from pydantic import BaseModel

  class Token(BaseModel):
      access_token: str
      token_type: str
  ```
- **状态码**:
  - `200 OK`: 登录成功。
  - `401 Unauthorized`: 用户名或密码错误，或账户未激活/被禁用。

### 3.2. 用��服务接口

#### `POST /users/`
- **描述**: 注册新用户。
- **请求体**: `application/json`
- **Pydantic 模型 (`app/schemas/user.py`):**
  ```python
  from pydantic import BaseModel, Field, EmailStr, field_validator
  import re

  class UserCreate(BaseModel):
      username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z][a-zA-Z0-9_]+$")
      email: EmailStr
      password: str = Field(..., min_length=8)
      full_name: str
      phone_number: str | None = None

      @field_validator('password')
      @classmethod
      def password_complexity(cls, v: str) -> str:
          if not re.search(r'[A-Z]', v) or \
             not re.search(r'[a-z]', v) or \
             not re.search(r'[0-9]', v):
              raise ValueError('Password must contain an uppercase letter, a lowercase letter, and a digit')
          return v
  ```
- **响应 (201 Created)**: `application/json`
- **Pydantic 模型 (`app/schemas/user.py`):**
  ```python
  import datetime
  from pydantic import BaseModel, EmailStr
  from app.models.user import UserStatus

  class UserOut(BaseModel):
      id: int
      username: str
      email: EmailStr
      full_name: str
      status: UserStatus
      created_at: datetime.datetime

      class Config:
          from_attributes = True
  ```
- **状态码**:
  - `201 Created`: 用户创建成功。
  - `400 Bad Request`: 输入数据验证失败（如密码太弱、用户名格式错误）。
  - `409 Conflict`: 用户名或邮箱已存在。

## 4. 业务逻辑实现方案

业务逻辑将在服务层 (`app/services`) 中实现，并通过 FastAPI 的依赖注入系统在 API 路由中使用。

### 4.1. 密码安全 (`app/core/security.py`)

使用 `passlib` 库处理密码的哈希和验证。
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 4.2. 用户服务 (`app/services/user_service.py`)

实现用户相关的核心业务逻辑。
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
# ... 其他导入

class UserService:
    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        # 1. 检查用户名和邮箱是否已存在
        # ... (查询数据库)
        # 2. 如果存在，抛出 HTTPException(status_code=409)
        
        # 3. 哈希密码
        hashed_password = get_password_hash(user_in.password)
        
        # 4. 创建 User 模型实例
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            phone_number=user_in.phone_number
        )
        
        # 5. 保存到数据库
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        # 6. (在此处触发发送验证邮件的异步任务)
        
        return db_user
```

## 5. 测试实现方案 (Pytest)

PIM 中定义的测试将使用 `pytest` 和 FastAPI 的 `TestClient` 来实现。

- **数据库**: 测试将使用独立的 SQLite 内存数据库，通过 `pytest` 的 `fixture` 在每次测试会话开始时创建，结束时销毁。
- **测试数据**: 使用 `fixture` 来创建和清理测试数据，确保测试的独立性。

### 示例：用户注册集成测试 (`tests/test_api/test_users.py`)

```python
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app

client = TestClient(app)

def test_user_registration_success(db: Session):
    """对应 PIM 测试: test_user_registration - 场景 1"""
    response = client.post(
        "/users/",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "ValidPassword123",
            "full_name": "New User"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data

def test_user_registration_duplicate_username(db: Session):
    """对应 PIM 测试: test_user_registration - 场景 2"""
    # Fixture `db` 应预���创建一个用户 "existinguser"
    response = client.post(
        "/users/",
        json={
            "username": "existinguser",
            "email": "another@example.com",
            "password": "ValidPassword123",
            "full_name": "Another User"
        },
    )
    assert response.status_code == 409
    assert "Username already registered" in response.json()["detail"]

def test_user_registration_weak_password(db: Session):
    """对应 PIM 测试: test_user_registration - 场景 3"""
    response = client.post(
        "/users/",
        json={
            "username": "weakpassuser",
            "email": "weak@example.com",
            "password": "123", # 密码太短且不符合复杂度要求
            "full_name": "Weak User"
        },
    )
    assert response.status_code == 422 # FastAPI's validation error
```

## 6. 项目结构说明

推荐采用模块化的项目结构，便于管理和扩展。

```
/user_management_with_tests
|-- app/
|   |-- __init__.py
|   |-- api/
|   |   |-- __init__.py
|   |   |-- deps.py              # 依赖注入项
|   |   |-- endpoints/
|   |   |   |-- __init__.py
|   |   |   |-- users.py         # 用户 API 路由
|   |   |   |-- auth.py          # 认证 API 路由
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py            # 应用配置
|   |   |-- security.py          # 密码和JWT安全相关
|   |-- db/
|   |   |-- __init__.py
|   |   |-- base.py              # 声明式 Base 和通用模型
|   |   |-- session.py           # 数据库会话管理
|   |-- models/
|   |   |-- __init__.py
|   |   |-- user.py              # 用户 SQLAlchemy 模型
|   |-- schemas/
|   |   |-- __init__.py
|   |   |-- user.py              # 用户 Pydantic Schema
|   |   |-- token.py             # Token Pydantic Schema
|   |-- services/
|   |   |-- __init__.py
|   |   |-- user_service.py      # 用户业务逻辑服务
|-- tests/
|   |-- __init__.py
|   |-- conftest.py              # Pytest fixtures
|   |-- test_api/
|   |   |-- test_users.py
|   |   |-- test_auth.py
|-- main.py                      # FastAPI 应用入口
|-- requirements.txt             # 项目依赖
|-- .env.example                 # 环境变量示例
```

## 7. 技术栈和依赖���表

以下是 `requirements.txt` 文件的建议内容：

```txt
# Web Framework
fastapi
uvicorn[standard]

# ORM and Database
sqlalchemy[asyncio]
psycopg2-binary      # For PostgreSQL
alembic              # For database migrations

# Data Validation
pydantic
pydantic-settings
email-validator

# Security and Authentication
passlib[bcrypt]
python-jose[cryptography]
python-multipart     # For OAuth2PasswordRequestForm

# Testing
pytest
pytest-cov
httpx                # For TestClient
```