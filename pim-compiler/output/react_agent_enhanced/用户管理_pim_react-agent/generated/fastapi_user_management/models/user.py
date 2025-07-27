from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from pydantic import BaseModel, EmailStr, constr

from ..database.database import Base

# 枚举定义
class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"  # 活跃状态
    INACTIVE = "inactive"  # 停用状态

# 值对象定义
class PhoneNumber(str):
    """电话号码值对象，包含格式验证"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not v:
            return v
        # 简单的电话号码格式验证 (可根据实际需求调整)
        if not v.startswith("+") and not v.isdigit():
            raise ValueError("电话号码格式不正确")
        return cls(v)

# 实体模型 (SQLAlchemy)
class User(Base):
    """用户实体模型"""
    __tablename__ = "users"
    
    # 主键使用UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), nullable=False)  # 姓名，必填，最大50字符
    email = Column(String(100), unique=True, nullable=False, index=True)  # 邮箱，必填，唯一，最大100字符
    phone = Column(String(20))  # 电话号码，可选
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)  # 状态，默认为活跃
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间，自动设置
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间，自动更新

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"

# Pydantic 模型 (用于输入输出验证)
class UserBase(BaseModel):
    """用户基础模型"""
    name: constr(max_length=50)  # 姓名，最大50字符
    email: EmailStr  # 邮箱，自动验证格式
    phone: Optional[PhoneNumber] = None  # 电话号码，可选

class UserCreate(UserBase):
    """创建用户模型"""
    pass

class UserUpdate(BaseModel):
    """更新用户模型"""
    name: Optional[constr(max_length=50)] = None  # 可选更新
    email: Optional[EmailStr] = None  # 可选更新
    phone: Optional[PhoneNumber] = None  # 可选更新

class UserInDB(UserBase):
    """数据库用户模型"""
    id: uuid.UUID
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True  # 允许ORM模型转换