"""Database initialization and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import os

import sys
from pathlib import Path
# Add src to path for proper imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .models import Base, ModelRecord, InstanceRecord, SystemEvent
from core.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Create engine
if settings.database_url.startswith("sqlite"):
    # SQLite specific settings
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        poolclass=StaticPool,  # Better for SQLite
        echo=settings.debug
    )
else:
    # PostgreSQL/MySQL settings
    engine = create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        echo=settings.debug
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize database tables"""
    try:
        logger.info("Initializing database...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a new database session (caller must close it)"""
    return SessionLocal()


__all__ = [
    "init_database",
    "get_db",
    "get_db_session",
    "ModelRecord",
    "InstanceRecord", 
    "SystemEvent",
    "Base"
]