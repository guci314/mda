from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.enums import BookStatus


class BookBase(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=13, description="ISBN号")
    title: str = Field(..., min_length=1, max_length=255, description="书名")
    author: str = Field(..., min_length=1, max_length=255, description="作者")
    publisher: Optional[str] = Field(None, max_length=255, description="出版社")
    publication_year: Optional[int] = Field(None, ge=1000, le=9999, description="出版年份")
    category: Optional[str] = Field(None, max_length=100, description="图书分类")
    total_copies: int = Field(1, ge=1, description="总册数")
    available_copies: int = Field(1, ge=0, description="可借册数")


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    publisher: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1000, le=9999)
    category: Optional[str] = Field(None, max_length=100)
    total_copies: Optional[int] = Field(None, ge=1)
    available_copies: Optional[int] = Field(None, ge=0)


class BookResponse(BookBase):
    id: int
    status: BookStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookSearch(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    status: Optional[BookStatus] = None