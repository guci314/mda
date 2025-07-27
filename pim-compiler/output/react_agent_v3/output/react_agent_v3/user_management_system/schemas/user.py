from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, constr

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")  # E.164格式
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    status: Optional[UserStatus] = None

class UserInDB(UserBase):
    id: str  # UUID格式
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode

class UserResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserInDB] = None

class UsersResponse(BaseModel):
    success: bool
    total: int
    users: List[UserInDB]

class UserQueryParams(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[UserStatus] = None
    skip: int = 0
    limit: int = 100