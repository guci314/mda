"""Dynamic route management for PIM Engine

This module provides a robust solution for dynamically loading and unloading
routes at runtime, ensuring proper cleanup of OpenAPI documentation.
"""

from typing import Dict, List, Set, Optional
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
import threading
from datetime import datetime

from core.models import PIMModel
from utils.logger import setup_logger


class DynamicRouteManager:
    """Manages dynamic loading and unloading of routes"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.logger = setup_logger(__name__)
        self.lock = threading.Lock()
        
        # Track loaded models and their routes
        self.loaded_models: Dict[str, Dict] = {}
        # model_name -> {
        #     "router": APIRouter,
        #     "routes": List[APIRoute],
        #     "prefix": str,
        #     "loaded_at": datetime
        # }
        
        # Track all route paths for each model
        self.model_route_paths: Dict[str, Set[str]] = {}
        
    def load_model_routes(self, model_name: str, router: APIRouter, prefix: str = "/api/v1") -> bool:
        """Load routes for a model"""
        with self.lock:
            if model_name in self.loaded_models:
                self.logger.warning(f"Model {model_name} already loaded")
                return False
            
            # Calculate full prefix
            full_prefix = f"{prefix}/{model_name.lower().replace(' ', '-')}"
            
            # Record all route paths before adding to app
            route_paths = set()
            for route in router.routes:
                if hasattr(route, 'path'):
                    # Store the full path including prefix
                    full_path = f"{full_prefix}{route.path}"
                    route_paths.add(full_path)
            
            # Add router to app
            self.app.include_router(router, prefix=full_prefix)
            
            # Store information
            self.loaded_models[model_name] = {
                "router": router,
                "routes": list(router.routes),
                "prefix": full_prefix,
                "loaded_at": datetime.now()
            }
            self.model_route_paths[model_name] = route_paths
            
            # Clear OpenAPI cache
            self._clear_openapi_cache()
            
            self.logger.info(f"Loaded {len(route_paths)} routes for model: {model_name}")
            return True
    
    def unload_model_routes(self, model_name: str) -> bool:
        """Unload routes for a model"""
        with self.lock:
            if model_name not in self.loaded_models:
                self.logger.warning(f"Model {model_name} not loaded")
                return False
            
            # Get routes to remove
            routes_to_remove = self.model_route_paths.get(model_name, set())
            
            # Filter out the routes from app.routes
            # We need to rebuild the routes list excluding the ones we want to remove
            new_routes = []
            removed_count = 0
            
            for route in self.app.routes:
                # Check if this route should be removed
                should_remove = False
                
                if hasattr(route, 'path'):
                    # For APIRoute objects, check the path
                    if route.path in routes_to_remove:
                        should_remove = True
                        removed_count += 1
                elif hasattr(route, 'path_regex'):
                    # For Mount objects or other route types
                    # Check if any of our paths match
                    for path in routes_to_remove:
                        if path.startswith(route.path):
                            should_remove = True
                            removed_count += 1
                            break
                
                if not should_remove:
                    new_routes.append(route)
            
            # Replace the routes - need to clear and re-add
            self.app.routes.clear()
            self.app.routes.extend(new_routes)
            
            # Clean up our tracking
            del self.loaded_models[model_name]
            del self.model_route_paths[model_name]
            
            # Clear OpenAPI cache
            self._clear_openapi_cache()
            
            self.logger.info(f"Unloaded {removed_count} routes for model: {model_name}")
            return True
    
    def get_loaded_models(self) -> List[Dict]:
        """Get information about loaded models"""
        with self.lock:
            return [
                {
                    "name": name,
                    "prefix": info["prefix"],
                    "routes_count": len(self.model_route_paths.get(name, [])),
                    "loaded_at": info["loaded_at"].isoformat()
                }
                for name, info in self.loaded_models.items()
            ]
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is loaded"""
        with self.lock:
            return model_name in self.loaded_models
    
    def get_model_routes(self, model_name: str) -> List[str]:
        """Get all routes for a model"""
        with self.lock:
            return list(self.model_route_paths.get(model_name, []))
    
    def _clear_openapi_cache(self):
        """Clear the OpenAPI schema cache"""
        self.app.openapi_schema = None
        self.logger.debug("Cleared OpenAPI schema cache")
    
    def reload_model_routes(self, model_name: str, router: APIRouter, prefix: str = "/api/v1") -> bool:
        """Reload routes for a model (unload then load)"""
        # First unload if exists
        if self.is_model_loaded(model_name):
            self.unload_model_routes(model_name)
        
        # Then load new routes
        return self.load_model_routes(model_name, router, prefix)