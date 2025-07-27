# FastAPI 数据模型代码 (User 实体)

以下是符合 FastAPI 最佳实践的完整数据模型代码，包含 SQLAlchemy ORM 模型和 Pydantic 模式：

```python
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy 基础模型
Base = declarative_base()

# SQLAlchemy ORM 模型
class User(Base):
    """用户数据库模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


# Pydantic 模型/模式
class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """创建用户模型"""
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(UserBase):
    """更新用户模型"""
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserInDBBase(UserBase):
    """数据库基础模型"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class UserPublic(UserInDBBase):
    """公开用户模型 (API响应)"""
    pass


class UserPrivate(UserInDBBase):
    """私有用户模型 (包含敏感信息)"""
    hashed_password: str
```

## 代码说明

1. **SQLAlchemy ORM 模型**:
   - 定义了 `User` 表结构，包含常用用户字段
   - 设置了适当的约束（唯一索引、非空等）
   - 包含自动时间戳字段

2. **Pydantic 模型**:
   - 分层设计：基础模型 → 创建/更新模型 → 数据库模型 → 公开/私有模型
   - 使用 `EmailStr` 验证邮箱格式
   - 字段验证（长度限制等）
   - `orm_mode = True` 允许从 ORM 对象自动转换

3. **最佳实践**:
   - 密码字段只在创建/更新模型中出现
   - 公开模型不包含敏感信息
   - 私有模型包含哈希密码（用于内部处理）
   - 使用 `Optional` 和默认值处理可选字段

4. **类型注解**:
   - 所有字段都有明确的类型注解
   - 使用 Python 标准类型和 Pydantic 特殊类型

这个实现遵循了 FastAPI 推荐的数据模型设计模式，适合大多数用户管理场景。