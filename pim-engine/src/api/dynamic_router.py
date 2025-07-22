"""Dynamic router management for FastAPI"""

from typing import Dict, Set, Optional
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class DynamicRouter:
    """Manages dynamic routes with enable/disable capability"""
    
    def __init__(self):
        self.routers: Dict[str, APIRouter] = {}
        self.enabled_models: Set[str] = set()
        self.model_prefixes: Dict[str, str] = {}
    
    def register_model_router(self, model_name: str, router: APIRouter, prefix: str):
        """Register a router for a model"""
        self.routers[model_name] = router
        self.model_prefixes[model_name] = prefix
        self.enabled_models.add(model_name)
        logger.info(f"Registered router for model: {model_name}")
    
    def enable_model(self, model_name: str):
        """Enable routes for a model"""
        if model_name in self.routers:
            self.enabled_models.add(model_name)
            logger.info(f"Enabled routes for model: {model_name}")
    
    def disable_model(self, model_name: str):
        """Disable routes for a model without removing them"""
        if model_name in self.enabled_models:
            self.enabled_models.remove(model_name)
            logger.info(f"Disabled routes for model: {model_name}")
    
    def is_model_enabled(self, model_name: str) -> bool:
        """Check if a model's routes are enabled"""
        return model_name in self.enabled_models
    
    def get_model_from_path(self, path: str) -> Optional[str]:
        """Extract model name from request path"""
        # Remove /api/v1 prefix if present
        if path.startswith("/api/v1/"):
            path = path[8:]
        
        # Check each model's prefix
        for model_name, prefix in self.model_prefixes.items():
            clean_prefix = prefix.strip("/")
            if path.startswith(clean_prefix):
                return model_name
        
        return None


class DynamicRouterMiddleware:
    """Middleware to check if routes are enabled"""
    
    def __init__(self, app, dynamic_router: DynamicRouter):
        self.app = app
        self.dynamic_router = dynamic_router
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            
            # Check if this is a model-specific API path
            if path.startswith("/api/v1/") and not path.startswith("/api/v1/models/"):
                model_name = self.dynamic_router.get_model_from_path(path)
                
                if model_name and not self.dynamic_router.is_model_enabled(model_name):
                    # Return 404 for disabled model routes
                    response = JSONResponse(
                        status_code=404,
                        content={"detail": f"Model '{model_name}' is not loaded"}
                    )
                    await response(scope, receive, send)
                    return
        
        await self.app(scope, receive, send)