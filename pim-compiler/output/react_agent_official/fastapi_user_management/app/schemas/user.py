from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, constr


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)  # Name cannot be empty
    email: EmailStr
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")  # E.164 phone format
    status: UserStatus = UserStatus.ACTIVE


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: constr(min_length=1, max_length=50) = None
    email: EmailStr = None
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$") = None


class UserInDB(UserBase):
    id: str  # UUID format unique identifier
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True