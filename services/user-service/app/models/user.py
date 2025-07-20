# MDA-GENERATED-START: user-models
"""
User domain models - SQLAlchemy ORM and Pydantic schemas
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from app.core.database import Base


# MDA-GENERATED-START: enums
class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
# MDA-GENERATED-END: enums


# MDA-GENERATED-START: sqlalchemy-model
class User(Base):
    """SQLAlchemy User model"""
    __tablename__ = "users"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
# MDA-GENERATED-END: sqlalchemy-model


# MDA-GENERATED-START: pydantic-schemas
class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=1, max_length=100, description="用户姓名")
    email: EmailStr = Field(..., description="电子邮箱")
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$', description="联系电话")


class UserCreate(UserBase):
    """Schema for creating a user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    status: Optional[UserStatus] = None


class UserInDB(UserBase):
    """User schema with database fields"""
    id: UUID
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """User response schema"""
    pass


class PaginatedUsers(BaseModel):
    """Paginated users response"""
    items: list[UserResponse]
    total: int
    skip: int
    limit: int
# MDA-GENERATED-END: pydantic-schemas