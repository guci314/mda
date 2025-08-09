from pydantic import BaseModel
from enum import Enum
from datetime import datetime, date

class BorrowStatus(str, Enum):
    BORROWED = "借阅中"
    RETURNED = "已归还"
    OVERDUE = "已逾期"
    LOST = "已丢失"

class BorrowRecordResponse(BaseModel):
    borrow_id: str
    reader_id: str
    isbn: str
    borrow_date: datetime
    due_date: date
    return_date: datetime | None
    renew_count: int
    status: BorrowStatus
    fine: float | None

    class Config:
        from_attributes = True
