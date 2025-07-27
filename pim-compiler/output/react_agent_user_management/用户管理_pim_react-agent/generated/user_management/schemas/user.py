from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# Base user model
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, example="张三")
    email: EmailStr = Field(..., example="user@example.com")
    phone: Optional[str] = Field(
        None, 
        min_length=10, 
        max_length=20, 
        regex=r"^\d+$",
        example="13800138000"
    )

# Create user request model
class UserCreate(UserBase):
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError("Phone number must contain only digits")
        return v

# Update user request model
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50, example="李四")
    email: Optional[EmailStr] = Field(None, example="new@example.com")
    phone: Optional[str] = Field(
        None, 
        min_length=10, 
        max_length=20, 
        regex=r"^\d+$",
        example="13900139000"
    )
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError("Phone number must contain only digits")
        return v

# User response model
class UserResponse(UserBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True