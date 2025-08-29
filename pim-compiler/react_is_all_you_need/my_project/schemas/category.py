from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CategoryCreate(BaseModel):
    """创建分类的输入模型"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    """更新分类的输入模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    """分类响应模型"""
    id: str
    name: str
    description: Optional[str] = None
    article_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)