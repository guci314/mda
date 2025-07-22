"""Worker FastAPI Application"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import asyncio

from .config import WorkerConfig
from core.models import PIMModel
from loaders import ModelLoader
from engines import DataEngine, RuleEngine, FlowEngine
from api import APIGenerator
from debug import FlowDebugger
from debug.debug_routes import create_debug_routes
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def create_app(config: WorkerConfig) -> FastAPI:
    """Create and configure the worker FastAPI app"""
    
    # Create FastAPI app
    app = FastAPI(
        title=f"PIM Model Instance - {config.model_name}",
        version="1.0.0",
        description=f"Instance '{config.instance_id}' running model '{config.model_name}'",
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
    
    # Initialize components
    app.state.config = config
    app.state.model_loader = ModelLoader()
    app.state.data_engine = DataEngine(config.database_url)
    app.state.rule_engine = RuleEngine()
    app.state.flow_engine = FlowEngine(app.state.rule_engine)
    app.state.flow_debugger = FlowDebugger()
    
    # Create a mock engine object for APIGenerator
    class MockEngine:
        def __init__(self, app_state):
            self.data_engine = app_state.data_engine
            self.rule_engine = app_state.rule_engine
            self.flow_engine = app_state.flow_engine
            self.flow_debugger = app_state.flow_debugger
            self.models = {}
    
    mock_engine = MockEngine(app.state)
    app.state.api_generator = APIGenerator(mock_engine)
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "instance_id": config.instance_id,
            "model": config.model_name,
            "port": config.port
        }
    
    @app.get("/info")
    async def instance_info():
        """Get instance information"""
        return {
            "instance_id": config.instance_id,
            "model_name": config.model_name,
            "port": config.port,
            "database": config.database_url,
            "model_loaded": hasattr(app.state, 'model')
        }
    
    @app.on_event("startup")
    async def startup_event():
        """Load model on startup"""
        logger.info(f"Starting worker instance '{config.instance_id}' for model '{config.model_name}'")
        
        try:
            # Find and load model file
            models_path = config.get_models_path()
            model_file = None
            
            for ext in ['.yaml', '.yml', '.md']:
                path = models_path / f"{config.model_name}{ext}"
                if path.exists():
                    model_file = path
                    break
            
            if not model_file:
                raise FileNotFoundError(f"Model file not found for '{config.model_name}'")
            
            # Load model
            logger.info(f"Loading model from {model_file}")
            result = await app.state.model_loader.load_model(str(model_file))
            
            if not result.success:
                raise RuntimeError(f"Failed to load model: {', '.join(result.errors)}")
            
            app.state.model = result.model
            
            # Setup database
            await app.state.data_engine.setup_model(result.model)
            
            # Setup API routes
            mock_engine.models[config.model_name] = result.model
            await app.state.api_generator.register_model_routes(result.model)
            
            # Load rules and flows
            await app.state.rule_engine.load_rules(result.model.rules)
            await app.state.flow_engine.load_flows(result.model.flows)
            
            # Add debug routes
            debug_router = create_debug_routes(app.state.flow_debugger)
            app.include_router(debug_router)
            
            logger.info(f"Model '{config.model_name}' loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        logger.info(f"Shutting down worker instance '{config.instance_id}'")
    
    return app