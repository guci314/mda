from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from app.models.borrow_record import BorrowStatus

# Shared properties
class BorrowRecordBase(BaseModel):
    reader_id: str = Field(..., max_length=50, description="读者编号")
    isbn: str = Field(..., max_length=20, description="国际标准书号")

# Properties to receive on item creation
class BorrowRecordCreate(BorrowRecordBase):
    borrow_id: str = Field(..., max_length=50, description="借阅编号")
    due_date: date = Field(..., description="应还日期")

# Properties to receive on item update
class BorrowRecordUpdate(BaseModel):
    return_date: Optional[datetime] = Field(None, description="实际归还日期")
    renewal_count: Optional[int] = Field(None, description="续借次数")
    status: Optional[BorrowStatus] = Field(None, description="状态")
    fine: Optional[Decimal] = Field(None, description="罚金")

# Properties shared by models stored in DB
class BorrowRecordInDBBase(BorrowRecordBase):
    model_config = ConfigDict(from_attributes=True)

    borrow_id: str
    borrow_date: datetime
    due_date: date
    return_date: Optional[datetime] = None
    renewal_count: int
    status: BorrowStatus
    fine: Optional[Decimal] = None

# Properties to return to client
class BorrowRecord(BorrowRecordInDBBase):
    pass

# Schema for creating a borrow action
class BorrowCreateAction(BaseModel):
    reader_id: str
    isbn: str

# Schema for the response of a return action
class ReturnResponse(BaseModel):
    message: str
    fine: Decimal
