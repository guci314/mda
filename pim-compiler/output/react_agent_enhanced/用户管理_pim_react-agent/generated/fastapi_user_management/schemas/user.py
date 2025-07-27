from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, constr

# 枚举定义
class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"

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