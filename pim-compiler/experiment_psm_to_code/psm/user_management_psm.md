# 用户管理系统 PSM - FastAPI 平台

## 1. 技术架构
- **框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **验证**: Pydantic
- **API文档**: 自动生成的 OpenAPI/Swagger

## 2. 数据模型实现

### User 实体
```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Pydantic Schemas
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## 3. API 实现

### 路由定义
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查邮箱是否已存在
    # 检查用户名是否已存在
    # 创建新用户
    # 返回用户信息
    pass

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    # 查询用户
    # 如果不存在抛出 404
    # 返回用户信息
    pass
```

## 4. 业务逻辑实现

### UserService
```python
from typing import Optional
import bcrypt
from uuid import uuid4

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        # 验证邮箱唯一性
        # 验证用户名唯一性
        # 哈希密码
        # 创建用户记录
        # 发送验证邮件（异步）
        pass
    
    def verify_email(self, token: str) -> bool:
        # 验证令牌
        # 更新用户状态
        pass
```

## 5. 项目结构
```
src/
├── models/
│   └── user.py          # SQLAlchemy 模型
├── schemas/
│   └── user.py          # Pydantic schemas
├── api/
│   └── v1/
│       └── users.py     # API 路由
├── services/
│   └── user_service.py  # 业务逻辑
├── core/
│   ├── config.py        # 配置
│   └── database.py      # 数据库连接
└── main.py              # FastAPI 应用入口
```

## 6. 依赖项
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```
