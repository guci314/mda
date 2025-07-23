from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.models.enums import ReaderType, ReaderStatus

# Base model with shared attributes
class ReaderBase(BaseModel):
    name: str = Field(..., max_length=100)
    id_card_number: str = Field(..., max_length=18, min_length=18)
    phone_number: str = Field(..., max_length=15)
    email: Optional[EmailStr] = None
    reader_type: ReaderType
    valid_until: date

# Schema for creating a new reader
class ReaderCreate(ReaderBase):
    reader_id: str = Field(..., max_length=50, description="Unique ID for the reader")

# Schema for updating a reader's information
class ReaderUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    reader_type: Optional[ReaderType] = None
    valid_until: Optional[date] = None
    status: Optional[ReaderStatus] = None
    credit_score: Optional[int] = Field(None, ge=0, le=100)

# Schema for reading/returning reader data from the API
class Reader(ReaderBase):
    model_config = ConfigDict(from_attributes=True)
    
    reader_id: str
    registration_date: datetime
    status: ReaderStatus
    credit_score: int
