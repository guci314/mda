"""
数据库连接配置
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

# 数据库URL配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./library_borrowing_system.db"
)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 开发环境显示SQL语句
    future=True
)

# 创建异步会话工厂
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 声明基类
Base = declarative_base()


async def get_async_db() -> AsyncSession:
    """获取异步数据库会话"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """创建数据库表"""
    from .models.database import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """删除数据库表"""
    from .models.database import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 兼容性函数（同步版本）
def get_db():
    """同步数据库会话（已弃用，请使用get_async_db）"""
    raise NotImplementedError("请使用异步版本 get_async_db")


def init_db():
    """初始化数据库（已弃用，请使用create_tables）"""
    raise NotImplementedError("请使用异步版本 create_tables")