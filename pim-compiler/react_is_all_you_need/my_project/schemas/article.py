from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ArticleBase(BaseModel):
    """文章基础Schema"""
    title: str = Field(..., min_length=1, max_length=200, description="文章标题")
    content: str = Field(..., min_length=1, description="文章内容")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    author: str = Field("Anonymous", min_length=1, max_length=100, description="作者")
    category_id: Optional[str] = Field(None, description="分类ID")
    status: str = Field("draft", pattern="^(draft|published)$", description="文章状态")

class ArticleCreate(ArticleBase):
    """创建文章Schema"""
    pass

class ArticleUpdate(BaseModel):
    """更新文章Schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文章标题")
    content: Optional[str] = Field(None, min_length=1, description="文章内容")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    author: Optional[str] = Field(None, min_length=1, max_length=100, description="作者")
    category_id: Optional[str] = Field(None, description="分类ID")
    status: Optional[str] = Field(None, pattern="^(draft|published)$", description="文章状态")

class ArticleResponse(ArticleBase):
    """文章响应Schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    view_count: int
    created_at: datetime
    updated_at: datetime

class ArticleQuery(BaseModel):
    """文章查询Schema"""
    category_id: Optional[str] = Field(None, description="分类ID")
    status: Optional[str] = Field(None, pattern="^(draft|published)$", description="文章状态")
    search: Optional[str] = Field(None, min_length=1, description="搜索关键词")
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(10, ge=1, le=100, description="每页记录数")