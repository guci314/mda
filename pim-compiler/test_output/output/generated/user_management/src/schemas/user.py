"""
Pydantic Schemas for Data Validation and Serialization.

This module defines the Pydantic models used for request and response
data validation. It ensures that the data exchanged with the API
conforms to a specific structure and type.
"""
import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from ..models.user import UserStatus


# --- Base Schemas ---
class UserBase(BaseModel):
    """Base schema for user properties."""
    email: EmailStr = Field(..., description="User's email address.")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username.")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validator to ensure username is alphanumeric."""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores.')
        return v


# --- Schemas for API Operations ---
class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="User's password (min 8 characters).")

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        """Validator to enforce password complexity."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit.')
        if not re.search(r'[\W_]', v):
            raise ValueError('Password must contain at least one special character.')
        return v


class UserUpdate(BaseModel):
    """Schema for updating an existing user. All fields are optional."""
    email: EmailStr | None = Field(None, description="New email address.")
    username: str | None = Field(None, min_length=3, max_length=50, description="New username.")
    status: UserStatus | None = Field(None, description="New user status.")


# --- Schemas for API Responses ---
class UserPublic(UserBase):
    """Schema for publicly available user information."""
    id: int = Field(..., description="Unique user ID.")
    status: UserStatus = Field(..., description="User's current status.")
    created_at: datetime = Field(..., description="Timestamp of user creation.")

    # This configuration tells Pydantic to read data from ORM models
    model_config = ConfigDict(from_attributes=True)


# --- Schemas for Authentication ---
class Token(BaseModel):
    """Schema for the authentication token response."""
    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(default="bearer", description="Type of the token.")


class TokenPayload(BaseModel):
    """Schema for the decoded token payload."""
    sub: str | None = Field(None, description="Subject of the token (username).")
