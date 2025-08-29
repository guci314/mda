from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ArticleCreate(BaseModel):
    """创建文章的输入模型"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=50)
    category_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ArticleUpdate(BaseModel):
    """更新文章的输入模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=50)
    category_id: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    
    model_config = ConfigDict(from_attributes=True)


class ArticleQuery(BaseModel):
    """文章查询参数模型"""
    category_id: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    
    model_config = ConfigDict(from_attributes=True)


class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: str
    title: str
    content: str
    summary: str
    author: str
    category_id: Optional[str] = None
    status: str
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)