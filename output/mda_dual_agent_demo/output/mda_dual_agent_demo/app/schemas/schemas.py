from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from app.models.enums import BookStatus, ReaderType, ReaderStatus, BorrowStatus, ReservationStatus

# Book Schemas
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=50)
    publisher: str = Field(..., min_length=1, max_length=50)
    publish_year: int = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=20)
    total_quantity: int = Field(..., gt=0)
    available_quantity: int = Field(..., ge=0)
    location: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None

class BookCreate(BookBase):
    isbn: str = Field(..., min_length=10, max_length=20)

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=50)
    publisher: Optional[str] = Field(None, min_length=1, max_length=50)
    publish_year: Optional[int] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=20)
    total_quantity: Optional[int] = Field(None, gt=0)
    available_quantity: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None
    status: Optional[BookStatus] = None

class BookResponse(BookBase):
    isbn: str
    status: BookStatus
    
    model_config = ConfigDict(from_attributes=True)

# Reader Schemas
class ReaderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    id_card: str = Field(..., min_length=15, max_length=18)
    phone: str = Field(..., min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    reader_type: ReaderType

class ReaderCreate(ReaderBase):
    valid_until: date

class ReaderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    valid_until: Optional[date] = None
    status: Optional[ReaderStatus] = None

class ReaderResponse(ReaderBase):
    reader_id: str
    register_date: datetime
    valid_until: date
    status: ReaderStatus
    credit_score: int
    
    model_config = ConfigDict(from_attributes=True)

# Borrow Record Schemas
class BorrowRecordCreate(BaseModel):
    reader_id: str
    isbn: str
    due_date: date

class BorrowRecordUpdate(BaseModel):
    return_date: Optional[datetime] = None
    status: Optional[BorrowStatus] = None
    fine: Optional[float] = None

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
    
    model_config = ConfigDict(from_attributes=True)

# Reservation Record Schemas
class ReservationRecordCreate(BaseModel):
    reader_id: str
    isbn: str

class ReservationRecordUpdate(BaseModel):
    status: Optional[ReservationStatus] = None
    notify_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None

class ReservationRecordResponse(BaseModel):
    reservation_id: str
    reader_id: str
    isbn: str
    reserve_date: datetime
    status: ReservationStatus
    notify_date: Optional[datetime]
    expire_date: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)