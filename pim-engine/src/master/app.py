"""Master Controller FastAPI Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .models_api import router as models_router
from .instances_api import router as instances_router
from .events_api import router as events_router
from .model_manager import ModelManager
from .instance_manager import InstanceManager
from .process_manager import ProcessManager
from .port_manager import PortManager
from .persistence_manager import PersistenceManager
from database import init_database
from core.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the master controller FastAPI app"""
    app = FastAPI(
        title="PIM Engine Master Controller",
        version="2.0.0",
        description="Master controller for managing PIM models and instances",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize persistence manager
    app.state.persistence_manager = PersistenceManager()
    
    # Initialize managers with persistence
    app.state.model_manager = ModelManager(
        persistence_manager=app.state.persistence_manager
    )
    app.state.port_manager = PortManager(start_port=8001, end_port=8999)
    app.state.process_manager = ProcessManager()
    app.state.instance_manager = InstanceManager(
        model_manager=app.state.model_manager,
        port_manager=app.state.port_manager,
        process_manager=app.state.process_manager,
        persistence_manager=app.state.persistence_manager
    )
    
    # Include API routers
    app.include_router(models_router, prefix="/models", tags=["Models"])
    app.include_router(instances_router, prefix="/instances", tags=["Instances"])
    app.include_router(events_router, prefix="/events", tags=["Events"])
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "pim-engine-master",
            "version": "2.0.0"
        }
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize on startup"""
        logger.info("PIM Engine Master Controller starting up...")
        
        # Create necessary directories
        import os
        os.makedirs("instances", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Initialize database
        try:
            init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            # Continue without persistence
        
        # Restore state from database
        try:
            # Restore models first
            await app.state.model_manager.restore_from_database()
            logger.info("Models restored from database")
            
            # Then restore instances
            await app.state.instance_manager.restore_from_database()
            logger.info("Instances restored from database")
        except Exception as e:
            logger.error(f"Failed to restore state from database: {e}")
            # Continue without restored state
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        logger.info("PIM Engine Master Controller shutting down...")
        # Stop all running instances
        await app.state.instance_manager.stop_all_instances()
    
    return app