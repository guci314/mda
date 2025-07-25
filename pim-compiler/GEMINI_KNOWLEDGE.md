# Gemini 代码生成和修复知识库

本文档包含了使用 Gemini CLI 生成和修复代码的最佳实践和经验总结。

## 1. FastAPI 项目结构规范

### 1.1 标准目录结构
```
./
├── main.py                 # 应用程序入口点（必须）
├── requirements.txt        # Python 依赖列表（必须）
├── README.md              # 项目说明文档
├── .env.example           # 环境变量示例
├── .gitignore             # Git 忽略文件
├── app/                   # 应用主目录（必须）
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用实例（必须）
│   ├── api/               # API 路由目录
│   │   └── v1/
│   │       ├── api.py     # API 路由聚合
│   │       └── endpoints/ # 端点目录
│   ├── core/              # 核心配置目录
│   │   ├── config.py      # 应用配置（必须）
│   │   └── security.py    # 安全相关
│   ├── models/            # SQLAlchemy 数据模型
│   ├── schemas/           # Pydantic 模型
│   ├── services/          # 业务逻辑
│   ├── crud/              # CRUD 操作
│   └── db/                # 数据库相关
│       ├── base.py        # 数据库基类
│       └── session.py     # 数据库会话
└── tests/                 # 测试目录
    ├── conftest.py        # pytest 配置
    └── test_*.py          # 测试文件
```

### 1.2 关键文件内容

#### 根目录 main.py
```python
#!/usr/bin/env python3
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

#### app/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
```

## 2. Pydantic v2 使用规范

### 2.1 基本模型定义
```python
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date
from typing import Optional

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    email: str
    name: Optional[str] = None
    birth_date: Optional[date] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()
```

### 2.2 Settings 配置
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    PROJECT_NAME: str = "My API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "your-secret-key-here"

settings = Settings()
```

### 2.3 重要注意事项
- **绝不**同时使用 `Config` 类和 `model_config`
- 使用 `from pydantic_settings import BaseSettings` 而不是 `from pydantic import BaseSettings`
- 使用 `@field_validator` 而不是 `@validator`
- 使用 `model_dump()` 而不是 `dict()`
- 验证器必须是 `@classmethod`

## 3. SQLAlchemy 2.0 使用规范

### 3.1 模型定义
```python
from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
from datetime import date

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # 关系
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
```

### 3.2 数据库会话
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 4. 常见错误及解决方案

### 4.1 循环导入问题
```python
# 使用 TYPE_CHECKING 解决
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

# 或使用字符串引用
orders: Mapped[list["Order"]] = relationship(back_populates="user")
```

### 4.2 Pydantic Config 错误
错误信息：`"Config" and "model_config" cannot be used together`

解决方案：
```python
# 错误示例
class User(BaseModel):
    class Config:  # 不要使用这个
        from_attributes = True
    
    model_config = ConfigDict(from_attributes=True)  # 同时又有这个

# 正确示例
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 只用这个
```

### 4.3 日期类型不匹配
- SQLAlchemy 使用 `Date` 类型
- Pydantic 使用 `date` 类型
- 确保导入正确：`from datetime import date`

### 4.4 缺失依赖
常见缺失的包：
- `python-multipart` - FastAPI 文件上传需要
- `python-jose[cryptography]` - JWT 认证需要
- `passlib[bcrypt]` - 密码哈希需要
- `alembic` - 数据库迁移需要

## 5. API 设计规范

### 5.1 RESTful 路由设计
```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.get("/", response_model=List[UserOut])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """列出所有用户"""
    return crud.user.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=UserOut, status_code=201)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """创建新用户"""
    return crud.user.create(db, obj_in=user_in)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取单个用户"""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 5.2 错误处理
```python
from fastapi import HTTPException, status

# 标准错误响应
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)

# 带额外信息的错误
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": "Validation error",
        "errors": ["Email already exists"]
    }
)
```

## 6. 测试规范

### 6.1 测试客户端设置
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.api.deps import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
```

### 6.2 测试示例
```python
# tests/test_users.py
def test_create_user(client):
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_get_user(client, db):
    # 先创建用户
    user = User(email="test@example.com", name="Test")
    db.add(user)
    db.commit()
    
    # 测试获取
    response = client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
```

## 7. 性能优化建议

### 7.1 数据库查询优化
- 使用 `joinedload` 预加载关联数据
- 使用 `limit` 和 `offset` 分页
- 为常用查询字段添加索引

### 7.2 异步处理
- 对于 I/O 密集型操作使用 `async/await`
- 使用 `asyncpg` 代替 `psycopg2` (PostgreSQL)
- 使用 `aioredis` 进行缓存

### 7.3 响应优化
- 使用 `response_model_exclude_unset=True` 减少响应大小
- 实现适当的缓存策略
- 使用 CDN 静态资源

## 8. 安全最佳实践

### 8.1 认证和授权
- 使用 JWT 令牌进行认证
- 实现基于角色的访问控制 (RBAC)
- 密码必须使用 bcrypt 哈希

### 8.2 输入验证
- 使用 Pydantic 模型验证所有输入
- 实现请求频率限制
- 防止 SQL 注入（使用 ORM）

### 8.3 CORS 配置
生产环境应限制 CORS：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 9. 部署准备

### 9.1 环境变量
创建 `.env.example` 文件：
```
PROJECT_NAME=My API
VERSION=1.0.0
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### 9.2 依赖管理
确保 `requirements.txt` 包含所有依赖：
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
alembic==1.12.1
pytest==7.4.3
httpx==0.25.2
```

## 10. 调试技巧

### 10.1 日志记录
```python
import logging

logger = logging.getLogger(__name__)

# 在关键位置添加日志
logger.info(f"Creating user with email: {user_in.email}")
logger.error(f"Failed to create user: {str(e)}")
```

### 10.2 开发工具
- 使用 `--reload` 选项启动 uvicorn
- 访问 `/docs` 查看 Swagger UI
- 使用 `pytest -v` 运行详细测试
- 使用 `flake8` 检查代码规范

## 11. REST API 测试规范

### 11.1 端点测试要求
在测试 FastAPI 应用的 REST 端点时，**不要测试根路径 `/`**，因为 FastAPI 应用通常不在根路径提供内容。

推荐测试的端点：
- `/docs` - Swagger UI 文档页面（应返回 200）
- `/openapi.json` - OpenAPI 规范文件（应返回 200）
- 实际的 API 端点（如 `/api/v1/users`、`/api/v1/patients` 等）

### 11.2 测试示例
```python
# 正确的测试端点
test_endpoints = [
    "/docs",
    "/openapi.json",
    "/api/v1/users",
    "/api/v1/patients"
]

# 避免测试根路径
# 不要测试: "/"
```

---

记住：代码生成的目标是创建**完整可运行**的应用，而不是框架或示例。每个功能都应该有对应的实现，包括 CRUD 操作、API 端点、业务逻辑和测试。