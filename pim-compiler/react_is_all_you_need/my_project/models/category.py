from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

class CategoryDB(Base):
    """分类数据库模型"""
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    article_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # 关系
    articles = relationship("ArticleDB", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"