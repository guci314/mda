from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional
from ..models.enums import BookStatus, ReaderType, ReaderStatus, BorrowStatus, ReservationStatus

class BookCreate(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=20)
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=50)
    publisher: str = Field(..., min_length=1, max_length=50)
    publish_year: int = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=20)
    total_quantity: int = Field(..., gt=0)
    available_quantity: int = Field(..., ge=0)
    location: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None

class BookResponse(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    publish_year: int
    category: str
    total_quantity: int
    available_quantity: int
    location: str
    description: Optional[str]
    status: BookStatus

    class Config:
        from_attributes = True

class ReaderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    id_card: str = Field(..., min_length=15, max_length=18)
    phone: str = Field(..., min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    reader_type: ReaderType

class ReaderResponse(BaseModel):
    reader_id: str
    name: str
    id_card: str
    phone: str
    email: Optional[str]
    reader_type: ReaderType
    register_date: datetime
    valid_until: date
    status: ReaderStatus
    credit_score: int

    class Config:
        from_attributes = True

class BorrowRecordResponse(BaseModel):
    borrow_id: str
    reader_id: str
    isbn: str
    borrow_date: datetime
    due_date: date
    return_date: Optional[datetime]
    renew_count: int
    status: BorrowStatus
    fine: Optional[float]

    class Config:
        from_attributes = True

class ReservationRecordResponse(BaseModel):
    reservation_id: str
    reader_id: str
    isbn: str
    reserve_date: datetime
    status: ReservationStatus
    notify_date: Optional[datetime]
    expire_date: Optional[datetime]

    class Config:
        from_attributes = True