from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, constr

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)  # 姓名不能为空
    email: EmailStr
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")  # E.164 电话格式
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: constr(min_length=1, max_length=50) = None
    email: EmailStr = None
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$") = None

class UserInDB(UserBase):
    id: str  # UUID格式的唯一标识符
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True