from pydantic import BaseModel, Field
from enum import Enum

class BookStatus(str, Enum):
    AVAILABLE = "在架"
    REMOVED = "已下架"

class BookCreate(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=20)
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=50)
    publisher: str = Field(..., min_length=1, max_length=50)
    publish_year: int = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=20)
    total_quantity: int = Field(..., gt=0)
    available_quantity: int = Field(..., ge=0)
    location: str = Field(..., min_length=1, max_length=20)
    description: str | None = None

class BookResponse(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    publish_year: int
    category: str
    total_quantity: int
    status: BookStatus

    class Config:
        from_attributes = True
