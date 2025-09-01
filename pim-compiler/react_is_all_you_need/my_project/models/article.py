from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

class ArticleDB(Base):
    """文章数据库模型"""
    __tablename__ = "articles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    author = Column(String(100), nullable=False, default="Anonymous")
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    view_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # 关系
    category = relationship("CategoryDB", back_populates="articles")
    comments = relationship("CommentDB", back_populates="article", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title}, status={self.status})>"