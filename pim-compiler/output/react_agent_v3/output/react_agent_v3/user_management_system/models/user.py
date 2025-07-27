from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, constr

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")  # E.164格式
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: constr(min_length=1, max_length=50) | None = None
    email: EmailStr | None = None
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$") | None = None
    status: UserStatus | None = None

class UserInDB(UserBase):
    id: str  # UUID格式
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True