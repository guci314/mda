"""PIM Execution Engine Core"""

import asyncio
from typing import Dict, Optional, List
from datetime import datetime
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.models import PIMModel, ModelLoadResult
from loaders import ModelLoader
from engines import DataEngine, RuleEngine, FlowEngine
from api import APIGenerator
from utils.logger import setup_logger
from debug import FlowDebugger
from debug.debug_routes import create_debug_routes

# Global engine instance
engine = None


class PIMEngine:
    """Main PIM Execution Engine class"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance of PIMEngine"""
        global engine
        if engine is None:
            engine = cls()
            cls._instance = engine
        return engine
    
    def __init__(self):
        """Initialize the PIM Engine"""
        self.app = FastAPI(
            title=settings.app_name,
            version=settings.app_version,
            docs_url=settings.docs_url,
            redoc_url=settings.redoc_url,
            openapi_url=settings.openapi_url
        )
        
        # Setup logging
        self.logger = setup_logger(__name__)
        
        # Core components
        self.models: Dict[str, PIMModel] = {}
        self.model_loader = ModelLoader()
        self.data_engine = DataEngine(settings.database_url)
        self.rule_engine = RuleEngine()
        self.flow_engine = FlowEngine(self.rule_engine)
        self.api_generator = APIGenerator(self)
        self.flow_debugger = FlowDebugger()
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup core routes
        self._setup_core_routes()
        
        # Setup debug routes
        debug_router = create_debug_routes(self.flow_debugger)
        self.app.include_router(debug_router)
        
        # Setup model management routes
        from api.models import router as models_router
        self.app.include_router(models_router)
        
        # Setup code generation routes
        from api.codegen import router as codegen_router
        self.app.include_router(codegen_router)
        
        # Mount static files if directory exists
        static_path = Path("/app/static")
        if static_path.exists():
            self.app.mount("/static", StaticFiles(directory="/app/static"), name="static")
            
        # Add route for models management UI
        @self.app.get("/models", response_class=HTMLResponse)
        async def models_ui():
            """Serve models management UI"""
            models_html_path = static_path / "models.html"
            if models_html_path.exists():
                with open(models_html_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return "Models management UI not found"
        
        # Hot reload will be started when the event loop is running
        self._hot_reload_enabled = settings.hot_reload
        
        self.logger.info(f"{settings.app_name} initialized")
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure properly in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request logging
        @self.app.middleware("http")
        async def log_requests(request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            self.logger.info(
                f"{request.method} {request.url.path} - "
                f"{response.status_code} - {process_time:.3f}s"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
    
    def _setup_core_routes(self):
        """Setup core engine management routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Run startup tasks"""
            if self._hot_reload_enabled:
                asyncio.create_task(self._hot_reload_loop())
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": settings.app_version,
                "models_loaded": len(self.models)
            }
        
        @self.app.get("/engine/status")
        async def engine_status():
            """Get engine status"""
            loaded_models = []
            for name, model in self.models.items():
                loaded_models.append({
                    "name": name,
                    "version": model.version,
                    "description": model.description,
                    "entities": [e.name for e in model.entities],
                    "services": [s.name for s in model.services]
                })
            
            return {
                "status": "running",
                "loaded_models": loaded_models,
                "version": settings.app_version,
                "configuration": {
                    "hot_reload": settings.hot_reload,
                    "database": bool(settings.database_url),
                    "cache": bool(settings.redis_url),
                    "llm": bool(settings.llm_api_key)
                }
            }
        
        @self.app.post("/engine/models/load")
        async def load_model(model_name: str, force: bool = False):
            """Load a PIM model"""
            if model_name in self.models and not force:
                return {
                    "status": "already_loaded",
                    "model": model_name,
                    "message": "Model already loaded. Use force=true to reload."
                }
            
            result = await self.load_model(model_name)
            
            if not result.success:
                raise HTTPException(
                    status_code=400,
                    detail={"errors": result.errors}
                )
            
            return {
                "status": "loaded",
                "model": model_name,
                "load_time_ms": result.load_time_ms,
                "entities": len(result.model.entities),
                "services": len(result.model.services)
            }
        
        @self.app.delete("/engine/models/{model_name}")
        async def unload_model(model_name: str):
            """Unload a model"""
            if model_name not in self.models:
                raise HTTPException(
                    status_code=404,
                    detail=f"Model '{model_name}' not found"
                )
            
            await self.unload_model(model_name)
            
            return {
                "status": "unloaded",
                "model": model_name
            }
        
        @self.app.get("/engine/models")
        async def list_models():
            """List loaded models"""
            models_info = []
            for name, model in self.models.items():
                models_info.append({
                    "name": name,
                    "domain": model.domain,
                    "version": model.version,
                    "entities": [e.name for e in model.entities],
                    "services": [s.name for s in model.services],
                    "loaded_at": model.loaded_at.isoformat()
                })
            
            return {"models": models_info, "total": len(models_info)}
        
        @self.app.get("/engine/models/{model_name}")
        async def get_model_details(model_name: str):
            """Get detailed model information"""
            if model_name not in self.models:
                raise HTTPException(
                    status_code=404,
                    detail=f"Model '{model_name}' not found"
                )
            
            model = self.models[model_name]
            return {
                "model": model.model_dump(),
                "statistics": {
                    "entities": len(model.entities),
                    "total_attributes": sum(len(e.attributes) for e in model.entities),
                    "services": len(model.services),
                    "total_methods": sum(len(s.methods) for s in model.services),
                    "flows": len(model.flows),
                    "rules": len(model.rules)
                }
            }
    
    async def load_model(self, model_name: str) -> ModelLoadResult:
        """Load a PIM model"""
        start_time = time.time()
        
        try:
            # Load model from file
            model_path = Path(settings.models_path) / f"{model_name}.yaml"
            if not model_path.exists():
                model_path = Path(settings.models_path) / f"{model_name}.md"
            
            if not model_path.exists():
                return ModelLoadResult(
                    success=False,
                    errors=[f"Model file not found: {model_name}"]
                )
            
            # Parse model
            result = await self.model_loader.load_model(str(model_path))
            
            if not result.success:
                return result
            
            # Store model
            self.models[model_name] = result.model
            
            # Setup database tables
            await self.data_engine.setup_model(result.model)
            
            # Register API routes
            await self.api_generator.register_model_routes(result.model)
            
            # Initialize rule engine
            await self.rule_engine.load_rules(result.model.rules)
            
            # Load flows
            await self.flow_engine.load_flows(result.model.flows)
            
            # Calculate load time
            load_time_ms = (time.time() - start_time) * 1000
            result.load_time_ms = load_time_ms
            
            self.logger.info(
                f"Model '{model_name}' loaded successfully in {load_time_ms:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error loading model '{model_name}': {str(e)}")
            return ModelLoadResult(
                success=False,
                errors=[f"Failed to load model: {str(e)}"]
            )
    
    async def unload_model(self, model_name: str):
        """Unload a model"""
        if model_name in self.models:
            # Remove API routes
            await self.api_generator.unregister_model_routes(self.models[model_name])
            
            # Remove from models
            del self.models[model_name]
            
            self.logger.info(f"Model '{model_name}' unloaded")
    
    async def reload_model(self, model_name: str):
        """Reload a model"""
        await self.unload_model(model_name)
        return await self.load_model(model_name)
    
    async def _hot_reload_loop(self):
        """Background task for hot reloading models"""
        while True:
            await asyncio.sleep(settings.reload_interval)
            
            # Check for model changes
            models_path = Path(settings.models_path)
            if not models_path.exists():
                continue
            
            for model_file in models_path.glob("*.yaml"):
                model_name = model_file.stem
                
                # Check if file has been modified
                if model_name in self.models:
                    model_mtime = model_file.stat().st_mtime
                    loaded_time = self.models[model_name].loaded_at.timestamp()
                    
                    if model_mtime > loaded_time:
                        self.logger.info(f"Model '{model_name}' changed, reloading...")
                        await self.reload_model(model_name)
    
    @property
    def loaded_models(self) -> Dict[str, PIMModel]:
        """Get loaded models"""
        return self.models
    
    def run(self):
        """Run the engine"""
        import uvicorn
        
        self.logger.info(f"Starting {settings.app_name} on {settings.host}:{settings.port}")
        
        uvicorn.run(
            self.app,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.lower()
        )