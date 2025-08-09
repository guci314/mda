from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.enums import ReservationStatus


class ReservationRecordBase(BaseModel):
    reader_id: str
    isbn: str


class ReservationRecordCreate(ReservationRecordBase):
    pass


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

    class Config:
        from_attributes = True