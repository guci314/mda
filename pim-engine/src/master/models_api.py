"""Models Management REST API"""

import os
import tempfile
from typing import List
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel

from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


class LoadModelRequest(BaseModel):
    """Request to load a model"""
    model_name: str


class ModelResponse(BaseModel):
    """Model information response"""
    name: str
    version: str
    loaded_at: str
    source_file: str
    description: str = None
    entities: List[str]
    services: List[str]


class ModelsListResponse(BaseModel):
    """List of models response"""
    models: List[ModelResponse]
    total: int


@router.get("", response_model=ModelsListResponse)
async def list_models(request: Request):
    """List all loaded models"""
    try:
        model_manager = request.app.state.model_manager
        models = model_manager.list_models()
        
        return ModelsListResponse(
            models=[ModelResponse(**model.to_dict()) for model in models],
            total=len(models)
        )
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load", response_model=ModelResponse)
async def load_model(request: Request, body: LoadModelRequest):
    """Load a new model from file"""
    try:
        model_manager = request.app.state.model_manager
        model_info = await model_manager.load_model(body.model_name)
        
        logger.info(f"Model '{body.model_name}' loaded successfully")
        return ModelResponse(**model_info.to_dict())
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_name}", response_model=ModelResponse)
async def get_model(request: Request, model_name: str):
    """Get details of a specific model"""
    try:
        model_manager = request.app.state.model_manager
        model_info = model_manager.get_model(model_name)
        
        if not model_info:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
        return ModelResponse(**model_info.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{model_name}")
async def unload_model(request: Request, model_name: str, hard: bool = False):
    """Unload a model (will stop all related instances)
    
    Args:
        model_name: Name of the model to unload
        hard: If true, also delete all files and directories (hard unload)
    """
    try:
        model_manager = request.app.state.model_manager
        instance_manager = request.app.state.instance_manager
        
        # Check if model exists
        if not model_manager.is_model_loaded(model_name):
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
        # Get model info before unloading
        model_info = model_manager.get_model(model_name)
        
        # Stop all instances of this model
        instances = instance_manager.list_instances(model_name=model_name)
        for instance in instances:
            logger.info(f"Stopping instance '{instance.id}' before unloading model")
            await instance_manager.stop_instance(instance.id, hard=hard)
        
        # Unload model (with hard delete if requested)
        model_manager.unload_model(model_name, hard=hard)
        
        return {
            "message": f"Model '{model_name}' {'hard' if hard else ''} unloaded successfully",
            "instances_stopped": len(instances),
            "hard_delete": hard
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unloading model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=ModelResponse)
async def upload_model(request: Request, file: UploadFile = File(...)):
    """Upload and load a model from file"""
    try:
        # Validate file extension
        valid_extensions = ['.md', '.yaml', '.yml']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in valid_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Supported types: {', '.join(valid_extensions)}"
            )
        
        # Save uploaded file to models directory
        models_path = Path("models")
        models_path.mkdir(exist_ok=True)
        
        # Extract model name from filename (remove extension)
        model_name = Path(file.filename).stem
        
        # Save file with original name
        file_path = models_path / file.filename
        
        # Check if file already exists
        if file_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Model file '{file.filename}' already exists. Please rename the file or delete the existing one."
            )
        
        # Save uploaded file
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved uploaded file: {file_path}")
        
        # Load the model
        model_manager = request.app.state.model_manager
        model_info = await model_manager.load_model(model_name)
        
        logger.info(f"Model '{model_name}' uploaded and loaded successfully")
        return ModelResponse(**model_info.to_dict())
        
    except HTTPException:
        # Clean up uploaded file if loading failed
        if 'file_path' in locals() and file_path.exists():
            os.unlink(file_path)
        raise
    except Exception as e:
        # Clean up uploaded file if loading failed
        if 'file_path' in locals() and file_path.exists():
            os.unlink(file_path)
        logger.error(f"Error uploading model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))