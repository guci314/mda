from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from app.enums import BorrowStatus


class BorrowRecordCreate(BaseModel):
    reader_id: str
    isbn: str
    due_date: date


class BorrowRecordResponse(BaseModel):
    borrow_id: str
    reader_id: str
    isbn: str
    borrow_date: datetime
    due_date: date
    return_date: Optional[datetime] = None
    renew_count: int
    status: BorrowStatus
    fine: Optional[Decimal] = None

    class Config:
        from_attributes = True