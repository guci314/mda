"""Instances Management REST API"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel

from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


class CreateInstanceRequest(BaseModel):
    """Request to create a new instance"""
    model_name: str
    instance_id: Optional[str] = None
    port: Optional[int] = None
    config: Optional[dict] = {}


class InstanceResponse(BaseModel):
    """Instance information response"""
    id: str
    model: str
    port: int
    status: str
    created_at: str
    database: str
    pid: Optional[int] = None
    uptime: str


class InstancesListResponse(BaseModel):
    """List of instances response"""
    instances: List[InstanceResponse]
    total: int


@router.get("", response_model=InstancesListResponse)
async def list_instances(request: Request, model: Optional[str] = Query(None)):
    """List all running instances"""
    try:
        instance_manager = request.app.state.instance_manager
        instances = instance_manager.list_instances(model_name=model)
        
        return InstancesListResponse(
            instances=[InstanceResponse(**instance.to_dict()) for instance in instances],
            total=len(instances)
        )
    except Exception as e:
        logger.error(f"Error listing instances: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=InstanceResponse)
async def create_instance(request: Request, body: CreateInstanceRequest):
    """Create and start a new instance"""
    try:
        instance_manager = request.app.state.instance_manager
        
        instance_info = await instance_manager.create_instance(
            model_name=body.model_name,
            instance_id=body.instance_id,
            port=body.port,
            config=body.config
        )
        
        logger.info(f"Instance '{instance_info.id}' created successfully")
        return InstanceResponse(**instance_info.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating instance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{instance_id}", response_model=InstanceResponse)
async def get_instance(request: Request, instance_id: str):
    """Get details of a specific instance"""
    try:
        instance_manager = request.app.state.instance_manager
        instance_info = instance_manager.get_instance(instance_id)
        
        if not instance_info:
            raise HTTPException(status_code=404, detail=f"Instance '{instance_id}' not found")
        
        # Check health
        await instance_manager.check_instance_health(instance_id)
        
        return InstanceResponse(**instance_info.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting instance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{instance_id}")
async def stop_instance(request: Request, instance_id: str):
    """Stop and remove an instance"""
    try:
        instance_manager = request.app.state.instance_manager
        
        # Check if instance exists
        if not instance_manager.get_instance(instance_id):
            raise HTTPException(status_code=404, detail=f"Instance '{instance_id}' not found")
        
        await instance_manager.stop_instance(instance_id)
        
        return {
            "message": f"Instance '{instance_id}' stopped successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping instance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{instance_id}/health")
async def check_instance_health(request: Request, instance_id: str):
    """Check if an instance is healthy"""
    try:
        instance_manager = request.app.state.instance_manager
        instance_info = instance_manager.get_instance(instance_id)
        
        if not instance_info:
            raise HTTPException(status_code=404, detail=f"Instance '{instance_id}' not found")
        
        is_healthy = await instance_manager.check_instance_health(instance_id)
        
        return {
            "instance_id": instance_id,
            "healthy": is_healthy,
            "status": instance_info.status,
            "port": instance_info.port
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking instance health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))