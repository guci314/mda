from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from pydantic import BaseModel, EmailStr, constr
from fastapi import HTTPException, status

from ..database import Base

# Enum definition
class UserStatus(str, Enum):
    """User status enum"""
    ACTIVE = "active"  # Active status
    INACTIVE = "inactive"  # Inactive status

# Value object definition
class PhoneNumber:
    """Phone number value object, immutable and with validation logic"""
    def __init__(self, number: str):
        if not self._validate_phone(number):
            raise ValueError("Invalid phone number format")
        self._number = number
    
    @property
    def number(self) -> str:
        return self._number
    
    @staticmethod
    def _validate_phone(phone: str) -> bool:
        """Validate phone number format (simple example)"""
        return len(phone) >= 10 and phone.isdigit()

# SQLAlchemy entity model
class User(Base):
    """User entity model"""
    __tablename__ = "users"
    
    # Primary key using UUID for global uniqueness
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Username, required, length limit 2-50 characters
    name = Column(String(50), nullable=False)
    
    # Email, required, unique index, length limit 255 characters
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Phone number, optional, length limit 20 characters
    phone = Column(String(20))
    
    # User status, using enum, default active status
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    
    # Creation time, automatically set to current time
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Update time, automatically updated
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }