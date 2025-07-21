"""
Database Connection and Session Management.

This module sets up the asynchronous database engine and session management
using SQLAlchemy. It provides a dependency to get a database session
for use in API endpoints.
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from .config import settings

# Create an asynchronous engine
# The 'check_same_thread' argument is specific to SQLite.
# It's not needed for other databases like PostgreSQL.
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True to see SQL queries in logs
)

# Create a configured "Session" class
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base class for ORM models
# All models will inherit from this class.
Base = declarative_base()


async def get_db():
    """
    FastAPI dependency that provides a database session.
    It ensures the session is always closed after the request.
    """
    async with AsyncSessionLocal() as session:
        yield session
