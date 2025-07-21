"""
Main application entry point.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger

from .core.config import settings
from .core.database import Base, engine
from .api import todos as todo_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    This context manager will run code on startup and shutdown.
    """
    logger.info("Starting up...")
    logger.info("Creating database tables...")
    # In a real production app, you would use Alembic for migrations.
    # For this simple example, we create tables on startup.
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Could not create database tables: {e}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    description="A simple Todo API based on a Platform-Specific Model.",
    version="1.0.0",
)

# Include API routers
app.include_router(todo_api.router, prefix="/todos", tags=["Todos"])


@app.get("/", tags=["Health Check"])
def health_check():
    """
    Health check endpoint. Returns the application status.
    """
    return {"status": "ok", "project_name": settings.PROJECT_NAME}
