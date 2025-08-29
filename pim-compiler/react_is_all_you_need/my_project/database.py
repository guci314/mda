from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite特定配置
    echo=False,  # 关闭SQL日志以提高性能
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    from models.category import CategoryDB
    from models.article import ArticleDB
    from models.comment import CommentDB
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成")