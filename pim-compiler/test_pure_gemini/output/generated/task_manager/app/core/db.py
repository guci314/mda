"""
数据库会话管理

此模块负责设置 SQLAlchemy 异步引擎、会话工厂以及声明式基类。
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 创建异步数据库引擎
# echo=True 会打印所有执行的 SQL 语句，便于调试
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# 创建一个异步会话工厂
# expire_on_commit=False 防止在提交后 ORM 对象的属性被过期
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    """
    所有 ORM 模型的基类。
    它提供了一个基础的 __tablename__ 生成策略，并可以包含所有模型共享的通用字段或方法。
    """
    pass
