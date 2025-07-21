"""
API 依赖项

此模块定义了 API 路由中常用的依赖项，例如数据库会话管理。
使用依赖注入可以确保每个请求都有一个独立的会话，并在请求结束后正确关闭。
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionFactory

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖项，用于获取数据库会话。

    它是一个异步生成器，会在请求处理前创建一个新的 `AsyncSession`，
    在处理完成后，通过 `finally` 块确保会话被关闭。

    Yields:
        AsyncSession: SQLAlchemy 异步会话实例。
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()
