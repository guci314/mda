from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    status = Column(Enum("active", "inactive", name="user_status"), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 如果实现认证系统
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)