from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    """分类基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")

class CategoryCreate(CategoryBase):
    """创建分类Schema"""
    pass

class CategoryUpdate(BaseModel):
    """更新分类Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")

class CategoryResponse(CategoryBase):
    """分类响应Schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    article_count: int
    created_at: datetime