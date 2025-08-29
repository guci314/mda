from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid


class CategoryDB(Base):
    """分类数据库模型"""
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    article_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    articles = relationship("ArticleDB", back_populates="category")