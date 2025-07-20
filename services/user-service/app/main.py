# MDA-GENERATED-START: main-app
"""
FastAPI application entry point for User Service
Generated from PSM model: 用户管理_psm.md
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.api import users
from app.core.config import settings
from app.core.database import engine, Base
from app.debug import debug_routes
from app.debug.middleware import DebugMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"Starting {settings.PROJECT_NAME}...")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print(f"Shutting down {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add debug middleware
app.add_middleware(DebugMiddleware)

# Include API routers
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

# Include debug routes
app.include_router(debug_routes.router, prefix="/debug", tags=["debug"])

# Mount debug UI static files
app.mount("/debug-ui", StaticFiles(directory="app/debug/static"), name="debug-ui")


@app.get("/")
async def root():
    """Service information endpoint"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "endpoints": {
            "api_docs": "/docs",
            "redoc": "/redoc",
            "debug": "/debug",
            "health": "/health",
            "api": settings.API_V1_STR
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
# MDA-GENERATED-END: main-app