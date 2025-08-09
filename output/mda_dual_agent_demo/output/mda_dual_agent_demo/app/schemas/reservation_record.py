from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.enums import ReservationStatus


class ReservationRecordCreate(BaseModel):
    reader_id: str
    isbn: str


class ReservationRecordResponse(BaseModel):
    reservation_id: str
    reader_id: str
    isbn: str
    reserve_date: datetime
    status: ReservationStatus
    notify_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None

    class Config:
        from_attributes = True