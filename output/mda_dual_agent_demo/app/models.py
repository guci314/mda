from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    author = Column(String(100), nullable=False)
    published_at = Column(DateTime)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    status = Column(Enum('draft', 'published', name='article_status'), default='draft')
    view_count = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="articles")
    comments = relationship("Comment", back_populates="article")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    article_count = Column(Integer, default=0)

    articles = relationship("Article", back_populates="category")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    author_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, default=func.now())
    status = Column(Enum('pending', 'published', 'blocked', name='comment_status'), default='pending')

    article = relationship("Article", back_populates="comments")