"""Master Controller FastAPI Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from .models_api import router as models_router
from .instances_api import router as instances_router
from .model_manager import ModelManager
from .instance_manager import InstanceManager
from .process_manager import ProcessManager
from .port_manager import PortManager
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
    
    # Initialize managers
    app.state.model_manager = ModelManager()
    app.state.port_manager = PortManager(start_port=8001, end_port=8999)
    app.state.process_manager = ProcessManager()
    app.state.instance_manager = InstanceManager(
        model_manager=app.state.model_manager,
        port_manager=app.state.port_manager,
        process_manager=app.state.process_manager
    )
    
    # Mount static files
    static_path = Path(__file__).parent.parent.parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        logger.info(f"Mounted static files from: {static_path}")
    
    # UI Routes - Define these BEFORE API routes to avoid conflicts
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Redirect to dashboard"""
        return HTMLResponse(content="""
            <html>
                <head>
                    <meta http-equiv="refresh" content="0; url=/ui/dashboard" />
                </head>
                <body>
                    <p>Redirecting to dashboard...</p>
                </body>
            </html>
        """)
    
    @app.get("/ui/models", response_class=HTMLResponse)
    async def models_ui():
        """Models management UI"""
        ui_file = static_path / "models_ui.html"
        if ui_file.exists():
            with open(ui_file, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Models UI not found</h1>", status_code=404)
    
    @app.get("/ui/instances", response_class=HTMLResponse)
    async def instances_ui():
        """Instances management UI"""
        ui_file = static_path / "instances_ui.html"
        if ui_file.exists():
            with open(ui_file, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Instances UI not found</h1>", status_code=404)
    
    @app.get("/ui/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """Dashboard UI"""
        ui_file = static_path / "dashboard.html"
        if ui_file.exists():
            with open(ui_file, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)
    
    # Include API routers - These come AFTER UI routes
    app.include_router(models_router, prefix="/models", tags=["Models"])
    app.include_router(instances_router, prefix="/instances", tags=["Instances"])
    
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
        # Create instances directory if not exists
        import os
        os.makedirs("instances", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        logger.info("PIM Engine Master Controller shutting down...")
        # Stop all running instances
        await app.state.instance_manager.stop_all_instances()
    
    return app