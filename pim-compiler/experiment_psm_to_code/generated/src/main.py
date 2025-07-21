import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.v1 import users
from src.core.config import settings
from src.core.database import Base, engine

# --- Logger Configuration ---
# Remove default handler
logger.remove()
# Add a new handler for stdout
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
# Add a file handler
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    level="INFO",
    format="{time} {level} {message}"
)

# --- Database Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    logger.info("Application startup...")
    async with engine.begin() as conn:
        # For development, you might want to drop and recreate tables
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created.")
    yield
    # On shutdown
    logger.info("Application shutdown...")


# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# --- API Routers ---
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    """A simple health check endpoint."""
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# --- Exception Handlers ---
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for request {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."},
    )
