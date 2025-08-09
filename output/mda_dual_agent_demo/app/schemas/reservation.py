from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.enums import ReservationStatus


class ReservationRecordBase(BaseModel):
    book_id: int = Field(..., gt=0, description="图书ID")
    reader_id: int = Field(..., gt=0, description="读者ID")
    expiry_date: datetime = Field(..., description="预约失效日期")


class ReservationRecordCreate(ReservationRecordBase):
    pass


class ReservationRecordUpdate(BaseModel):
    status: Optional[ReservationStatus] = None
    notification_sent: Optional[bool] = None


class ReservationRecordResponse(ReservationRecordBase):
    id: int
    reservation_date: datetime
    status: ReservationStatus
    notification_sent: bool
    created_at: datetime
    updated_at: datetime
    book_title: Optional[str] = None
    reader_name: Optional[str] = None

    class Config:
        from_attributes = True


class ReservationSearch(BaseModel):
    book_id: Optional[int] = None
    reader_id: Optional[int] = None
    status: Optional[ReservationStatus] = None