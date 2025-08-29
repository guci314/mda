from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid


class CommentDB(Base):
    """评论数据库模型"""
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id"), nullable=False)
    author_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending/published/blocked
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    article = relationship("ArticleDB", back_populates="comments")