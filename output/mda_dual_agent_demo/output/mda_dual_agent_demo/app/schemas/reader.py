from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date
from app.enums import ReaderType, ReaderStatus


class ReaderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    id_card: str = Field(..., min_length=15, max_length=18)
    phone: str = Field(..., min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    reader_type: ReaderType


class ReaderCreate(ReaderBase):
    pass


class ReaderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=11, max_length=11)
    email: Optional[EmailStr] = None


class ReaderResponse(ReaderBase):
    reader_id: str
    register_date: datetime
    valid_until: date
    status: ReaderStatus
    credit_score: int

    class Config:
        from_attributes = True