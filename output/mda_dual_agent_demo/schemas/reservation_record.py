from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class ReservationStatus(str, Enum):
    PENDING = "等待中"
    READY = "可借阅"
    CANCELLED = "已取消"
    COMPLETED = "已完成"

class ReservationRecordResponse(BaseModel):
    reservation_id: str
    reader_id: str
    isbn: str
    reserve_date: datetime
    status: ReservationStatus
    notify_date: datetime | None
    expire_date: datetime | None

    class Config:
        from_attributes = True
