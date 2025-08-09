from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from app.models.enums import ReaderStatus


class ReaderBase(BaseModel):
    library_card_number: str = Field(..., min_length=1, max_length=20, description="借书证号")
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    email: EmailStr = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    address: Optional[str] = Field(None, max_length=500, description="地址")


class ReaderCreate(ReaderBase):
    pass


class ReaderUpdate(BaseModel):
    library_card_number: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    status: Optional[ReaderStatus] = None


class ReaderResponse(ReaderBase):
    id: int
    status: ReaderStatus
    registration_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReaderSearch(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[ReaderStatus] = None