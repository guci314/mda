from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.enums import ReservationStatus

# Schema for creating a new reservation (request)
class ReservationCreate(BaseModel):
    reader_id: str = Field(..., description="The ID of the reader making the reservation")
    isbn: str = Field(..., description="The ISBN of the book to reserve")

# Base model for reservation record data
class ReservationRecordBase(BaseModel):
    reservation_id: str
    reader_id: str
    isbn: str
    reservation_date: datetime
    status: ReservationStatus

# Schema for updating a reservation record (internal use)
class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None
    available_date: Optional[datetime] = None
    pickup_deadline: Optional[datetime] = None

# Schema for reading/returning reservation data from the API
class ReservationRecord(ReservationRecordBase):
    model_config = ConfigDict(from_attributes=True)
    
    available_date: Optional[datetime] = None
    pickup_deadline: Optional[datetime] = None
