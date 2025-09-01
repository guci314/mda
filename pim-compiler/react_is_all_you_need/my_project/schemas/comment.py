from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    """评论基础Schema"""
    author_name: str = Field(..., min_length=1, max_length=100, description="评论者姓名")
    email: str = Field(..., min_length=1, max_length=200, description="评论者邮箱")
    content: str = Field(..., min_length=1, description="评论内容")

class CommentCreate(CommentBase):
    """创建评论Schema"""
    article_id: str = Field(..., description="文章ID")

class CommentUpdate(BaseModel):
    """更新评论Schema"""
    status: Optional[str] = Field(None, pattern="^(pending|published|blocked)$", description="评论状态")

class CommentResponse(CommentBase):
    """评论响应Schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    article_id: str
    status: str
    created_at: datetime

class CommentQuery(BaseModel):
    """评论查询Schema"""
    article_id: str = Field(..., description="文章ID")
    status: Optional[str] = Field(None, pattern="^(pending|published|blocked)$", description="评论状态")
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(10, ge=1, le=100, description="每页记录数")