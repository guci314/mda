"""
Main Application File.

This file contains the main FastAPI application instance, configures the logging,
includes the API routers, and sets up event handlers like creating database tables on startup.
"""
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from .api.router import api_router
from .core.config import settings
from .core.database import Base, engine


# --- Logging Configuration ---
# Remove default handler
logger.remove()
# Add a new handler to output to stderr
logger.add(
    sys.stderr,
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
)


# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    This context manager handles application startup and shutdown events.
    On startup, it creates all database tables.
    """
    logger.info("Application startup...")
    async with engine.begin() as conn:
        # This will create tables if they don't exist.
        # For production, Alembic is the recommended way to manage migrations.
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Application shutdown...")


# --- FastAPI Application Instance ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global handler for unexpected errors.
    Logs the error and returns a generic 500 response.
    """
    logger.error(f"Unhandled exception for request {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )


# --- API Router ---
app.include_router(api_router, prefix=settings.API_V1_STR)


# --- Root Endpoint ---
@app.get("/", tags=["Health Check"])
async def read_root():
    """
    Health check endpoint.
    Returns the application name and a welcome message.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
