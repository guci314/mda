from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    author: str
    published_at: Optional[datetime] = None
    status: Optional[str] = "draft"
    view_count: Optional[int] = 0
    category_id: int

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    status: Optional[str] = None
    view_count: Optional[int] = None
    category_id: Optional[int] = None

class Article(ArticleBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    article_count: Optional[int] = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    article_count: Optional[int] = None

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    article_id: int
    author_name: str
    email: EmailStr
    content: str
    published_at: Optional[datetime] = None
    status: Optional[str] = "pending"

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    article_id: Optional[int] = None
    author_name: Optional[str] = None
    email: Optional[EmailStr] = None
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    status: Optional[str] = None

class Comment(CommentBase):
    id: int

    class Config:
        from_attributes = True