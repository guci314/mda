from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.reservation_record import ReservationStatus

# Shared properties
class ReservationRecordBase(BaseModel):
    reader_id: str = Field(..., max_length=50, description="读者编号")
    isbn: str = Field(..., max_length=20, description="国际标准书号")

# Properties to receive on item creation
class ReservationRecordCreate(ReservationRecordBase):
    reservation_id: str = Field(..., max_length=50, description="预约编号")

# Properties to receive on item update
class ReservationRecordUpdate(BaseModel):
    status: Optional[ReservationStatus] = Field(None, description="预约状态")
    notification_date: Optional[datetime] = Field(None, description="通知日期")
    expiry_date: Optional[datetime] = Field(None, description="过期日期")

# Properties shared by models stored in DB
class ReservationRecordInDBBase(ReservationRecordBase):
    model_config = ConfigDict(from_attributes=True)

    reservation_id: str
    reservation_date: datetime
    status: ReservationStatus
    notification_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None

# Properties to return to client
class ReservationRecord(ReservationRecordInDBBase):
    pass

# Schema for creating a reservation action
class ReservationCreateAction(BaseModel):
    reader_id: str
    isbn: str
