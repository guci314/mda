from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid


class ArticleDB(Base):
    """文章数据库模型"""
    __tablename__ = "articles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500), nullable=False)
    author = Column(String(50), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    status = Column(String(20), default="draft")  # draft/published
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    category = relationship("CategoryDB", back_populates="articles")
    comments = relationship("CommentDB", back_populates="article")