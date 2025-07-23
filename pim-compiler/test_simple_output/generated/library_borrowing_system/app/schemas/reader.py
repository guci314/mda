from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime, date
from app.models.reader import ReaderType, ReaderStatus

# Shared properties
class ReaderBase(BaseModel):
    name: str = Field(..., max_length=100, description="姓名")
    id_card_number: str = Field(..., max_length=18, min_length=18, description="身份证号")
    phone_number: str = Field(..., max_length=15, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    reader_type: ReaderType = Field(..., description="读者类型")

# Properties to receive on item creation
class ReaderCreate(ReaderBase):
    reader_id: str = Field(..., max_length=50, description="读者编号")
    valid_until: date = Field(..., description="有效期至")

# Properties to receive on item update
class ReaderUpdate(BaseModel):
    phone_number: Optional[str] = Field(None, max_length=15, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    reader_type: Optional[ReaderType] = Field(None, description="读者类型")
    valid_until: Optional[date] = Field(None, description="有效期至")
    status: Optional[ReaderStatus] = Field(None, description="状态")
    credit_score: Optional[int] = Field(None, description="信用分")

# Properties shared by models stored in DB
class ReaderInDBBase(ReaderBase):
    model_config = ConfigDict(from_attributes=True)
    
    reader_id: str = Field(..., max_length=50, description="读者编号")
    registration_date: datetime = Field(..., description="注册日期")
    valid_until: date = Field(..., description="有效期至")
    status: ReaderStatus = Field(..., description="状态")
    credit_score: int = Field(..., description="信用分")

# Properties to return to client
class Reader(ReaderInDBBase):
    pass

# Properties stored in DB
class ReaderInDB(ReaderInDBBase):
    pass
