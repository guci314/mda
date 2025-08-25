from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BlogPost(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    author: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class BlogPostCreate(BaseModel):
    title: str
    content: str
    author: str


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None