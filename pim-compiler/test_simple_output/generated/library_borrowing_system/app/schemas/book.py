from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.book import BookStatus

# Shared properties
class BookBase(BaseModel):
    isbn: str = Field(..., max_length=20, description="国际标准书号")
    title: str = Field(..., max_length=255, description="书名")
    author: str = Field(..., max_length=100, description="作者")
    publisher: str = Field(..., max_length=100, description="出版社")
    publish_year: int = Field(..., description="出版年份")
    category: str = Field(..., max_length=50, description="分类")
    total_stock: int = Field(..., gt=0, description="总库存")
    available_stock: int = Field(..., description="可借数量")
    location: str = Field(..., max_length=100, description="位置")
    summary: Optional[str] = Field(None, description="简介")
    status: BookStatus = Field(default=BookStatus.ON_SHELF, description="状态")

# Properties to receive on item creation
class BookCreate(BookBase):
    pass

# Properties to receive on item update
class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="书名")
    author: Optional[str] = Field(None, max_length=100, description="作者")
    publisher: Optional[str] = Field(None, max_length=100, description="出版社")
    publish_year: Optional[int] = Field(None, description="出版年份")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    total_stock: Optional[int] = Field(None, gt=0, description="总库存")
    available_stock: Optional[int] = Field(None, description="可借数量")
    location: Optional[str] = Field(None, max_length=100, description="位置")
    summary: Optional[str] = Field(None, description="简介")
    status: Optional[BookStatus] = Field(None, description="状态")

# Properties shared by models stored in DB
class BookInDBBase(BookBase):
    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Book(BookInDBBase):
    pass

# Properties stored in DB
class BookInDB(BookInDBBase):
    pass
