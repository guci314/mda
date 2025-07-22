"""Dynamic OpenAPI schema management"""

from typing import Dict, Any, Optional
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import logging

logger = logging.getLogger(__name__)


class OpenAPIManager:
    """Manages dynamic OpenAPI schema generation"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.loaded_models: set = set()
        self._original_openapi = None
        
    def model_loaded(self, model_name: str):
        """Mark a model as loaded"""
        self.loaded_models.add(model_name.lower().replace(' ', '-'))
        self._clear_openapi_cache()
        logger.info(f"Model {model_name} marked as loaded in OpenAPI")
        
    def model_unloaded(self, model_name: str):
        """Mark a model as unloaded"""
        normalized_name = model_name.lower().replace(' ', '-')
        if normalized_name in self.loaded_models:
            self.loaded_models.remove(normalized_name)
            self._clear_openapi_cache()
            logger.info(f"Model {model_name} marked as unloaded in OpenAPI")
    
    def _clear_openapi_cache(self):
        """Clear the cached OpenAPI schema"""
        self.app.openapi_schema = None
        logger.info("Cleared OpenAPI schema cache")
    
    def custom_openapi(self):
        """Generate custom OpenAPI schema excluding unloaded models"""
        # Always regenerate for dynamic routes
        # if self.app.openapi_schema:
        #     return self.app.openapi_schema
            
        # Get the full schema - force regeneration
        openapi_schema = get_openapi(
            title=self.app.title,
            version=self.app.version,
            description=self.app.description,
            routes=self.app.routes,
        )
        
        # Filter out paths for unloaded models
        filtered_paths = {}
        for path, path_item in openapi_schema.get("paths", {}).items():
            # Always include non-API paths (health, engine, debug, etc.)
            if not path.startswith("/api/v1/"):
                filtered_paths[path] = path_item
                continue
            
            # For API paths, check if the model is loaded
            # Extract the model name from the path
            path_parts = path.split("/")
            if len(path_parts) > 3:  # /api/v1/model-name/...
                model_in_path = path_parts[3]
                
                # Check if this model is loaded
                if model_in_path in self.loaded_models:
                    filtered_paths[path] = path_item
                # else: skip this path as the model is not loaded
        
        openapi_schema["paths"] = filtered_paths
        
        # Update tags to only include loaded models
        if "tags" in openapi_schema:
            filtered_tags = []
            for tag in openapi_schema["tags"]:
                # Normalize tag name for comparison
                tag_normalized = tag["name"].lower().replace(' ', '-')
                
                # Include if it's a loaded model or a system tag
                if tag_normalized in self.loaded_models or tag["name"] in ["default", "Debug"]:
                    filtered_tags.append(tag)
            openapi_schema["tags"] = filtered_tags
        
        self.app.openapi_schema = openapi_schema
        return self.app.openapi_schema