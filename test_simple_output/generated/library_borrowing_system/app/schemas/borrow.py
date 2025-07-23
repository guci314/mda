from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from app.models.enums import BorrowStatus

# Schema for creating a new borrow record (request)
class BorrowCreate(BaseModel):
    reader_id: str = Field(..., description="The ID of the reader borrowing the book")
    isbn: str = Field(..., description="The ISBN of the book being borrowed")

# Schema for returning a book (request)
class ReturnCreate(BaseModel):
    borrow_id: str = Field(..., description="The ID of the borrow record to be returned")

# Schema for renewing a book (request)
class RenewCreate(BaseModel):
    borrow_id: str = Field(..., description="The ID of the borrow record to be renewed")

# Base model for borrow record data
class BorrowRecordBase(BaseModel):
    borrow_id: str
    reader_id: str
    isbn: str
    borrow_date: datetime
    due_date: date
    status: BorrowStatus
    renewal_count: int
    fine: float

# Schema for updating a borrow record (internal use)
class BorrowUpdate(BaseModel):
    return_date: Optional[datetime] = None
    status: Optional[BorrowStatus] = None
    fine: Optional[float] = None

# Schema for reading/returning borrow record data from the API
class BorrowRecord(BorrowRecordBase):
    model_config = ConfigDict(from_attributes=True)
    
    return_date: Optional[datetime] = None
