"""Instance Manager - Manages model instances"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid
from pathlib import Path

from .model_manager import ModelManager
from .port_manager import PortManager
from .process_manager import ProcessManager, ProcessInfo
from .persistence_manager import PersistenceManager
from database.models import InstanceStatus as DBInstanceStatus
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
                 process_manager: ProcessManager, persistence_manager: Optional[PersistenceManager] = None):
        self.model_manager = model_manager
        self.port_manager = port_manager
        self.process_manager = process_manager
        self.persistence_manager = persistence_manager
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
            
            # Save to persistence
            if self.persistence_manager:
                try:
                    self.persistence_manager.save_instance(
                        instance_id=instance_id,
                        model_name=model_name,
                        port=allocated_port,
                        config=config
                    )
                except Exception as e:
                    logger.error(f"Failed to persist instance: {e}")
                    # Continue even if persistence fails
            
            # Start process
            process_info = await self.process_manager.start_process(
                instance_id=instance_id,
                model_name=model_name,
                port=allocated_port,
                config=config
            )
            
            instance_info.process_info = process_info
            
            # Update persistence with PID
            if self.persistence_manager and process_info:
                self.persistence_manager.update_instance_status(
                    instance_id, DBInstanceStatus.STARTING, 
                    pid=process_info.pid
                )
            
            # Wait for instance to be ready
            import asyncio
            for _ in range(30):  # 30 seconds timeout
                if await self.process_manager.check_health(instance_id):
                    instance_info.status = "running"
                    
                    # Update persistence status
                    if self.persistence_manager:
                        self.persistence_manager.update_instance_status(
                            instance_id, DBInstanceStatus.RUNNING
                        )
                    break
                await asyncio.sleep(1)
            else:
                if self.persistence_manager:
                    self.persistence_manager.update_instance_status(
                        instance_id, DBInstanceStatus.ERROR,
                        health_error="Instance failed to start within timeout"
                    )
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
    
    async def stop_instance(self, instance_id: str, hard: bool = False):
        """Stop and remove an instance
        
        Args:
            instance_id: ID of the instance to stop
            hard: If True, delete the instance directory
        """
        if instance_id not in self.instances:
            raise ValueError(f"Instance '{instance_id}' not found")
        
        instance_info = self.instances[instance_id]
        
        # Update status
        instance_info.status = "stopping"
        
        # Update persistence status
        if self.persistence_manager:
            self.persistence_manager.update_instance_status(instance_id, DBInstanceStatus.STOPPING)
        
        try:
            # Stop process
            await self.process_manager.stop_process(instance_id)
            
            # Release port
            self.port_manager.release_port(instance_info.port)
            
            # Delete instance directory if hard delete
            if hard:
                instance_dir = Path(f"instances/{instance_id}")
                if instance_dir.exists():
                    logger.info(f"Deleting instance directory: {instance_dir}")
                    import shutil
                    try:
                        shutil.rmtree(instance_dir)
                        logger.info(f"Instance directory deleted: {instance_dir}")
                    except Exception as e:
                        logger.error(f"Failed to delete instance directory: {e}")
            
            # Update persistence
            if self.persistence_manager:
                if hard:
                    # Delete from database for hard delete
                    self.persistence_manager.delete_instance(instance_id)
                else:
                    # Just update status for soft stop
                    self.persistence_manager.update_instance_status(instance_id, DBInstanceStatus.STOPPED)
            
            # Remove instance
            del self.instances[instance_id]
            
            logger.info(f"Instance '{instance_id}' {'hard' if hard else ''} stopped successfully")
            
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
        
        # Update persistence
        if self.persistence_manager:
            self.persistence_manager.update_instance_health(instance_id, is_healthy)
            if instance_info.status == "unhealthy":
                self.persistence_manager.update_instance_status(
                    instance_id, DBInstanceStatus.UNHEALTHY
                )
        
        return is_healthy
    
    async def restore_from_database(self):
        """Restore instances from database on startup"""
        if not self.persistence_manager:
            logger.info("No persistence manager, skipping instance restoration")
            return
        
        logger.info("Restoring instances from database...")
        try:
            # Get all instances from database
            db_instances = self.persistence_manager.get_all_instances()
            
            for instance_data in db_instances:
                try:
                    instance_id = instance_data.get('id')
                    model_name = instance_data.get('model')
                    
                    # Skip if instance already in memory
                    if instance_id and instance_id in self.instances:
                        continue
                    
                    # Only restore instances that were running
                    status = instance_data.get('status')
                    if status != 'running' and status != DBInstanceStatus.RUNNING.value:
                        logger.info(f"Skipping instance '{instance_id}' with status {status}")
                        continue
                    
                    # Check if model is loaded
                    if not self.model_manager.is_model_loaded(model_name):
                        logger.warning(f"Model '{model_name}' not loaded, skipping instance '{instance_id}'")
                        continue
                    
                    # Try to restart the instance
                    logger.info(f"Attempting to restart instance '{instance_id}'")
                    try:
                        # Allocate the same port if available
                        port = instance_data.get('port')
                        allocated_port = self.port_manager.allocate_port(port)
                        
                        # Create instance info
                        instance_info = InstanceInfo(
                            instance_id=instance_id,
                            model_name=model_name,
                            port=allocated_port
                        )
                        instance_info.config = instance_data.get('config') or {}
                        
                        # Start process
                        process_info = await self.process_manager.start_process(
                            instance_id=instance_id,
                            model_name=model_name,
                            port=allocated_port,
                            config=instance_data.get('config')
                        )
                        
                        instance_info.process_info = process_info
                        
                        # Update persistence with new PID
                        if process_info:
                            self.persistence_manager.update_instance_status(
                                instance_id, DBInstanceStatus.STARTING, 
                                pid=process_info.pid
                            )
                            self.persistence_manager.increment_restart_count(instance_id)
                        
                        # Wait for instance to be ready
                        import asyncio
                        for _ in range(30):  # 30 seconds timeout
                            if await self.process_manager.check_health(instance_id):
                                instance_info.status = "running"
                                self.persistence_manager.update_instance_status(
                                    instance_id, DBInstanceStatus.RUNNING
                                )
                                break
                            await asyncio.sleep(1)
                        else:
                            logger.error(f"Instance '{instance_id}' failed to restart")
                            self.persistence_manager.update_instance_status(
                                instance_id, DBInstanceStatus.ERROR,
                                health_error="Failed to restart after system restart"
                            )
                            continue
                        
                        # Store instance
                        self.instances[instance_id] = instance_info
                        logger.info(f"Successfully restarted instance '{instance_id}'")
                        
                    except Exception as e:
                        logger.error(f"Failed to restart instance '{instance_id}': {e}")
                        self.persistence_manager.update_instance_status(
                            instance_id, DBInstanceStatus.ERROR,
                            health_error=f"Failed to restart: {str(e)}"
                        )
                        
                except Exception as e:
                    logger.error(f"Error processing instance '{instance_id}': {e}")
                    
            logger.info(f"Restored {len(self.instances)} instances from database")
            
        except Exception as e:
            logger.error(f"Failed to restore instances from database: {e}")