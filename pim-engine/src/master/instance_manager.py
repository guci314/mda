"""Instance Manager - Manages model instances"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid

from .model_manager import ModelManager
from .port_manager import PortManager
from .process_manager import ProcessManager, ProcessInfo
from utils.logger import setup_logger

logger = setup_logger(__name__)


class InstanceInfo:
    """Information about a model instance"""
    def __init__(self, instance_id: str, model_name: str, port: int, 
                 process_info: Optional[ProcessInfo] = None):
        self.id = instance_id
        self.model_name = model_name
        self.port = port
        self.status = "starting"
        self.created_at = datetime.now()
        self.process_info = process_info
        self.config = {}
        
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "model": self.model_name,
            "port": self.port,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "database": f"instances/{self.id}/database.db",
            "pid": self.process_info.pid if self.process_info else None,
            "uptime": self._get_uptime()
        }
    
    def _get_uptime(self) -> str:
        """Get instance uptime"""
        if self.status != "running":
            return "0s"
        
        delta = datetime.now() - self.created_at
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class InstanceManager:
    """Manages model instances"""
    
    def __init__(self, model_manager: ModelManager, port_manager: PortManager, 
                 process_manager: ProcessManager):
        self.model_manager = model_manager
        self.port_manager = port_manager
        self.process_manager = process_manager
        self.instances: Dict[str, InstanceInfo] = {}
        
    async def create_instance(self, model_name: str, instance_id: Optional[str] = None,
                            port: Optional[int] = None, config: Optional[dict] = None) -> InstanceInfo:
        """Create and start a new instance"""
        # Check if model is loaded
        if not self.model_manager.is_model_loaded(model_name):
            raise ValueError(f"Model '{model_name}' not loaded")
        
        # Generate instance ID if not provided
        if not instance_id:
            instance_id = f"{model_name}_{uuid.uuid4().hex[:8]}"
        
        # Check if instance ID already exists
        if instance_id in self.instances:
            raise ValueError(f"Instance '{instance_id}' already exists")
        
        # Allocate port
        try:
            allocated_port = self.port_manager.allocate_port(port)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to allocate port: {str(e)}")
        
        try:
            # Create instance info
            instance_info = InstanceInfo(
                instance_id=instance_id,
                model_name=model_name,
                port=allocated_port
            )
            instance_info.config = config or {}
            
            # Start process
            process_info = await self.process_manager.start_process(
                instance_id=instance_id,
                model_name=model_name,
                port=allocated_port,
                config=config
            )
            
            instance_info.process_info = process_info
            
            # Wait for instance to be ready
            import asyncio
            for _ in range(30):  # 30 seconds timeout
                if await self.process_manager.check_health(instance_id):
                    instance_info.status = "running"
                    break
                await asyncio.sleep(1)
            else:
                raise RuntimeError("Instance failed to start within timeout")
            
            # Store instance
            self.instances[instance_id] = instance_info
            
            logger.info(f"Instance '{instance_id}' created successfully on port {allocated_port}")
            return instance_info
            
        except Exception as e:
            # Cleanup on failure
            self.port_manager.release_port(allocated_port)
            try:
                await self.process_manager.stop_process(instance_id)
            except:
                pass
            raise RuntimeError(f"Failed to create instance: {str(e)}")
    
    async def stop_instance(self, instance_id: str):
        """Stop and remove an instance"""
        if instance_id not in self.instances:
            raise ValueError(f"Instance '{instance_id}' not found")
        
        instance_info = self.instances[instance_id]
        
        # Update status
        instance_info.status = "stopping"
        
        try:
            # Stop process
            await self.process_manager.stop_process(instance_id)
            
            # Release port
            self.port_manager.release_port(instance_info.port)
            
            # Remove instance
            del self.instances[instance_id]
            
            logger.info(f"Instance '{instance_id}' stopped successfully")
            
        except Exception as e:
            instance_info.status = "error"
            raise RuntimeError(f"Failed to stop instance: {str(e)}")
    
    def get_instance(self, instance_id: str) -> Optional[InstanceInfo]:
        """Get instance information"""
        return self.instances.get(instance_id)
    
    def list_instances(self, model_name: Optional[str] = None) -> List[InstanceInfo]:
        """List all instances, optionally filtered by model"""
        instances = list(self.instances.values())
        
        if model_name:
            instances = [i for i in instances if i.model_name == model_name]
        
        return instances
    
    async def stop_all_instances(self):
        """Stop all running instances"""
        logger.info("Stopping all instances...")
        instance_ids = list(self.instances.keys())
        
        for instance_id in instance_ids:
            try:
                await self.stop_instance(instance_id)
            except Exception as e:
                logger.error(f"Error stopping instance '{instance_id}': {str(e)}")
    
    async def check_instance_health(self, instance_id: str) -> bool:
        """Check if an instance is healthy"""
        if instance_id not in self.instances:
            return False
        
        instance_info = self.instances[instance_id]
        is_healthy = await self.process_manager.check_health(instance_id)
        
        # Update status based on health
        if is_healthy and instance_info.status != "running":
            instance_info.status = "running"
        elif not is_healthy and instance_info.status == "running":
            instance_info.status = "unhealthy"
        
        return is_healthy