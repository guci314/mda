"""Model management API endpoints"""

import os
from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import PlainTextResponse
import yaml
import logging

from core.config import settings
from loaders.model_loader import ModelLoader
from core.engine import PIMEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/models", tags=["Model Management"])


@router.get("/files", response_model=List[Dict[str, Any]])
async def list_model_files():
    """List all available model files in the models directory"""
    models_path = Path(settings.models_path)
    model_files = []
    
    if not models_path.exists():
        return []
    
    # Scan for .yaml, .yml, and .md files
    for ext in ["*.yaml", "*.yml", "*.md"]:
        for file_path in models_path.glob(ext):
            try:
                # Try to extract basic info
                name = file_path.stem
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract metadata if YAML
                version = "1.0.0"
                description = "PIM Model"
                
                if file_path.suffix in ['.yaml', '.yml']:
                    try:
                        data = yaml.safe_load(content)
                        version = data.get('version', version)
                        description = data.get('description', description)
                    except:
                        pass
                
                model_files.append({
                    "name": name,
                    "path": str(file_path.relative_to(models_path)),
                    "version": version,
                    "description": description,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
            except Exception as e:
                logger.error(f"Error reading model file {file_path}: {e}")
                
    return model_files


@router.post("/upload")
async def upload_model(file: UploadFile = File(...)):
    """Upload a new model file"""
    # Validate file extension
    if not file.filename.endswith(('.yaml', '.yml', '.md')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .yaml, .yml, and .md files are supported"
        )
    
    # Ensure models directory exists
    models_path = Path(settings.models_path)
    models_path.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = models_path / file.filename
    
    # Check if file already exists
    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"Model file {file.filename} already exists"
        )
    
    try:
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
            
        logger.info(f"Model file {file.filename} uploaded successfully")
        
        return {
            "message": "Model uploaded successfully",
            "filename": file.filename,
            "size": len(contents)
        }
    except Exception as e:
        logger.error(f"Error uploading model file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload model: {str(e)}"
        )


@router.get("/{model_name}/content", response_class=PlainTextResponse)
async def get_model_content(model_name: str):
    """Get the raw content of a model file"""
    models_path = Path(settings.models_path)
    
    # Try different extensions
    for ext in ['.yaml', '.yml', '.md']:
        file_path = models_path / f"{model_name}{ext}"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading model file {file_path}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to read model file: {str(e)}"
                )
    
    raise HTTPException(
        status_code=404,
        detail=f"Model file {model_name} not found"
    )


@router.delete("/{model_name}/file")
async def delete_model_file(model_name: str):
    """Delete a model file (only if not loaded)"""
    # Check if model is loaded
    engine = PIMEngine.get_instance()
    if model_name in engine.models:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a loaded model. Please unload it first"
        )
    
    models_path = Path(settings.models_path)
    
    # Try different extensions
    for ext in ['.yaml', '.yml', '.md']:
        file_path = models_path / f"{model_name}{ext}"
        if file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Model file {model_name} deleted")
                return {"message": f"Model file {model_name} deleted successfully"}
            except Exception as e:
                logger.error(f"Error deleting model file: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete model file: {str(e)}"
                )
    
    raise HTTPException(
        status_code=404,
        detail=f"Model file {model_name} not found"
    )


@router.post("/{model_name}/reload")
async def reload_model(model_name: str):
    """Reload a model (unload and load again)"""
    engine = PIMEngine.get_instance()
    
    try:
        # First unload if loaded
        if model_name in engine.loaded_models:
            engine.unload_model(model_name)
            
        # Then load again
        loader = ModelLoader()
        model = await loader.load_model(model_name)
        engine.load_model(model)
        
        return {
            "message": f"Model {model_name} reloaded successfully",
            "model": {
                "name": model.name,
                "version": model.version,
                "entities": len(model.entities),
                "services": len(model.services)
            }
        }
    except Exception as e:
        logger.error(f"Error reloading model {model_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload model: {str(e)}"
        )