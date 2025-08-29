from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    """创建评论的输入模型"""
    article_id: str
    author_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    content: str = Field(..., min_length=1)
    
    model_config = ConfigDict(from_attributes=True)


class CommentUpdate(BaseModel):
    """更新评论的输入模型"""
    author_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    content: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(pending|published|blocked)$")
    
    model_config = ConfigDict(from_attributes=True)


class CommentQuery(BaseModel):
    """评论查询参数模型"""
    article_id: Optional[str] = None
    status: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    
    model_config = ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    """评论响应模型"""
    id: str
    article_id: str
    author_name: str
    email: str
    content: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)