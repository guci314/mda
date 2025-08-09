from pydantic import BaseModel, Field
from typing import Optional
from app.enums import BookStatus


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=50)
    publisher: str = Field(..., min_length=1, max_length=50)
    publish_year: int = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=20)
    total_quantity: int = Field(..., gt=0)
    available_quantity: int = Field(..., ge=0)
    location: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None


class BookCreate(BookBase):
    isbn: str = Field(..., min_length=10, max_length=20)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=50)
    publisher: Optional[str] = Field(None, min_length=1, max_length=50)
    publish_year: Optional[int] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=20)
    total_quantity: Optional[int] = Field(None, gt=0)
    available_quantity: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None


class BookResponse(BookBase):
    isbn: str
    status: BookStatus

    class Config:
        from_attributes = True