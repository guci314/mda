from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.enums import BorrowStatus


class BorrowRecordBase(BaseModel):
    book_id: int = Field(..., gt=0, description="图书ID")
    reader_id: int = Field(..., gt=0, description="读者ID")
    due_date: datetime = Field(..., description="应还日期")


class BorrowRecordCreate(BorrowRecordBase):
    pass


class BorrowRecordUpdate(BaseModel):
    return_date: Optional[datetime] = Field(None, description="实际还书日期")
    status: Optional[BorrowStatus] = None


class BorrowRecordResponse(BorrowRecordBase):
    id: int
    borrow_date: datetime
    return_date: Optional[datetime]
    status: BorrowStatus
    created_at: datetime
    updated_at: datetime
    book_title: Optional[str] = None
    reader_name: Optional[str] = None

    class Config:
        from_attributes = True


class BorrowSearch(BaseModel):
    book_id: Optional[int] = None
    reader_id: Optional[int] = None
    status: Optional[BorrowStatus] = None
    overdue_only: Optional[bool] = False