from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.enums import BorrowStatus


class BorrowRecordBase(BaseModel):
    reader_id: str
    isbn: str
    due_date: date


class BorrowRecordCreate(BorrowRecordBase):
    pass


class BorrowRecordUpdate(BaseModel):
    return_date: Optional[datetime] = None
    status: Optional[BorrowStatus] = None
    fine: Optional[float] = Field(None, ge=0)


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