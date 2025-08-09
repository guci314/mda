from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import datetime, date

class ReaderType(str, Enum):
    STUDENT = "学生"
    TEACHER = "教师"
    SOCIAL = "社会人员"

class ReaderStatus(str, Enum):
    ACTIVE = "正常"
    FROZEN = "冻结"
    DELETED = "注销"

class ReaderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    id_card: str = Field(..., min_length=15, max_length=18)
    phone: str = Field(..., min_length=11, max_length=11)
    email: EmailStr | None = None
    reader_type: ReaderType

class ReaderResponse(BaseModel):
    reader_id: str
    name: str
    id_card: str
    phone: str
    email: str | None
    reader_type: ReaderType
    register_date: datetime
    valid_until: date
    status: ReaderStatus
    credit_score: int
