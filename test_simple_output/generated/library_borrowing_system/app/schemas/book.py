from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.enums import BookStatus

# Base model with shared attributes
class BookBase(BaseModel):
    isbn: str = Field(..., max_length=20, description="International Standard Book Number")
    title: str = Field(..., max_length=255, description="Book Title")
    author: str = Field(..., max_length=100, description="Book Author")
    publisher: str = Field(..., max_length=100, description="Publisher")
    publish_year: int = Field(..., gt=0, description="Year of Publication")
    category: str = Field(..., max_length=50, description="Book Category")
    total_stock: int = Field(..., ge=0, description="Total stock of the book")
    available_count: int = Field(..., ge=0, description="Number of available copies")
    location: str = Field(..., max_length=100, description="Location in the library")
    summary: Optional[str] = Field(None, description="A brief summary of the book")

# Schema for creating a new book
class BookCreate(BookBase):
    pass

# Schema for updating a book's information
class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=100)
    publisher: Optional[str] = Field(None, max_length=100)
    publish_year: Optional[int] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=50)
    total_stock: Optional[int] = Field(None, ge=0)
    available_count: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=100)
    summary: Optional[str] = None
    status: Optional[BookStatus] = None

# Schema for reading/returning book data from the API
class Book(BookBase):
    model_config = ConfigDict(from_attributes=True)
    
    status: BookStatus
