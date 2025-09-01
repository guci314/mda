from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

class CommentDB(Base):
    """评论数据库模型"""
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id"), nullable=False)
    author_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # 关系
    article = relationship("ArticleDB", back_populates="comments")
    
    def __repr__(self):
        return f"<Comment(id={self.id}, author={self.author_name}, status={self.status})>"