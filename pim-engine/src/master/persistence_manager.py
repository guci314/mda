"""Persistence Manager - Handles database operations for models and instances"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import sys
from pathlib import Path
# Add src to path for proper imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db, ModelRecord, InstanceRecord, SystemEvent
from database.models import ModelStatus, InstanceStatus
from utils.logger import setup_logger
from core.models import PIMModel

logger = setup_logger(__name__)


class PersistenceManager:
    """Manages persistence of models and instances to database"""
    
    def __init__(self):
        """Initialize persistence manager"""
        logger.info("Persistence manager initialized")
    
    # Model operations
    
    def save_model(self, name: str, model: PIMModel, source_file: str, 
                   content: str, format: str = "yaml") -> ModelRecord:
        """Save or update model in database"""
        with get_db() as db:
            try:
                # Check if model already exists
                model_record = db.query(ModelRecord).filter_by(name=name).first()
                
                if model_record:
                    # Update existing model
                    model_record.version = model.version
                    model_record.description = model.description
                    model_record.source_file = source_file
                    model_record.format = format
                    model_record.status = ModelStatus.LOADED
                    model_record.error_message = None
                    model_record.entities_count = len(model.entities) if model.entities else 0
                    model_record.services_count = len(model.services) if model.services else 0
                    model_record.flows_count = len(model.flows) if model.flows else 0
                    model_record.rules_count = len(model.rules) if model.rules else 0
                    model_record.model_content = content
                    model_record.compiled_model = model.model_dump() if hasattr(model, 'model_dump') else None
                    model_record.compiled_at = datetime.utcnow()
                    
                    logger.info(f"Updated model '{name}' in database")
                else:
                    # Create new model
                    model_record = ModelRecord(
                        name=name,
                        version=model.version,
                        description=model.description,
                        source_file=source_file,
                        format=format,
                        status=ModelStatus.LOADED,
                        entities_count=len(model.entities) if model.entities else 0,
                        services_count=len(model.services) if model.services else 0,
                        flows_count=len(model.flows) if model.flows else 0,
                        rules_count=len(model.rules) if model.rules else 0,
                        model_content=content,
                        compiled_model=model.model_dump() if hasattr(model, 'model_dump') else None,
                        compiled_at=datetime.utcnow()
                    )
                    db.add(model_record)
                    logger.info(f"Created new model '{name}' in database")
                
                # Log event
                event = SystemEvent(
                    event_type="model_saved",
                    entity_type="model",
                    entity_id=name,
                    description=f"Model '{name}' saved to database"
                )
                db.add(event)
                
                db.commit()
                return model_record
                
            except Exception as e:
                logger.error(f"Failed to save model '{name}': {str(e)}")
                db.rollback()
                raise
    
    def update_model_status(self, name: str, status: ModelStatus, 
                           error_message: Optional[str] = None):
        """Update model status"""
        with get_db() as db:
            try:
                model_record = db.query(ModelRecord).filter_by(name=name).first()
                if model_record:
                    model_record.status = status
                    model_record.error_message = error_message
                    
                    # Log event
                    event = SystemEvent(
                        event_type="model_status_changed",
                        entity_type="model",
                        entity_id=name,
                        description=f"Model '{name}' status changed to {status.value}",
                        details={"error": error_message} if error_message else None,
                        severity="error" if status == ModelStatus.ERROR else "info"
                    )
                    db.add(event)
                    
                    db.commit()
                    logger.info(f"Updated model '{name}' status to {status.value}")
            except Exception as e:
                logger.error(f"Failed to update model status: {str(e)}")
                db.rollback()
    
    def delete_model(self, name: str):
        """Delete model from database"""
        with get_db() as db:
            try:
                model_record = db.query(ModelRecord).filter_by(name=name).first()
                if model_record:
                    db.delete(model_record)
                    
                    # Log event
                    event = SystemEvent(
                        event_type="model_deleted",
                        entity_type="model",
                        entity_id=name,
                        description=f"Model '{name}' deleted from database"
                    )
                    db.add(event)
                    
                    db.commit()
                    logger.info(f"Deleted model '{name}' from database")
            except Exception as e:
                logger.error(f"Failed to delete model: {str(e)}")
                db.rollback()
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """Get all models from database"""
        with get_db() as db:
            models = db.query(ModelRecord).all()
            # Convert to dicts to avoid session issues
            return [model.to_dict() for model in models]
    
    def get_model(self, name: str) -> Optional[ModelRecord]:
        """Get specific model from database"""
        with get_db() as db:
            return db.query(ModelRecord).filter_by(name=name).first()
    
    # Instance operations
    
    def save_instance(self, instance_id: str, model_name: str, port: int,
                     config: Optional[Dict[str, Any]] = None) -> InstanceRecord:
        """Save instance to database"""
        with get_db() as db:
            try:
                # Check if instance already exists
                instance_record = db.query(InstanceRecord).filter_by(id=instance_id).first()
                
                if instance_record:
                    # Update existing instance
                    instance_record.model_name = model_name
                    instance_record.port = port
                    instance_record.status = InstanceStatus.STARTING
                    instance_record.config = config or {}
                    instance_record.database_path = f"instances/{instance_id}/database.db"
                    
                    logger.info(f"Updated instance '{instance_id}' in database")
                else:
                    # Create new instance
                    instance_record = InstanceRecord(
                        id=instance_id,
                        model_name=model_name,
                        port=port,
                        status=InstanceStatus.STARTING,
                        config=config or {},
                        database_path=f"instances/{instance_id}/database.db"
                    )
                    db.add(instance_record)
                    logger.info(f"Created new instance '{instance_id}' in database")
                
                # Log event
                event = SystemEvent(
                    event_type="instance_created",
                    entity_type="instance",
                    entity_id=instance_id,
                    description=f"Instance '{instance_id}' created for model '{model_name}'",
                    details={"port": port, "config": config}
                )
                db.add(event)
                
                db.commit()
                return instance_record
                
            except IntegrityError as e:
                logger.error(f"Instance or port already exists: {str(e)}")
                db.rollback()
                raise ValueError("Instance ID or port already in use")
            except Exception as e:
                logger.error(f"Failed to save instance: {str(e)}")
                db.rollback()
                raise
    
    def update_instance_status(self, instance_id: str, status: InstanceStatus,
                              pid: Optional[int] = None, 
                              health_error: Optional[str] = None):
        """Update instance status"""
        with get_db() as db:
            try:
                instance_record = db.query(InstanceRecord).filter_by(id=instance_id).first()
                if instance_record:
                    instance_record.status = status
                    
                    if pid is not None:
                        instance_record.pid = pid
                    
                    if status == InstanceStatus.RUNNING and not instance_record.started_at:
                        instance_record.started_at = datetime.utcnow()
                    elif status in [InstanceStatus.STOPPED, InstanceStatus.ERROR]:
                        instance_record.stopped_at = datetime.utcnow()
                    
                    if health_error:
                        instance_record.health_error = health_error
                        instance_record.is_healthy = False
                    else:
                        instance_record.is_healthy = (status == InstanceStatus.RUNNING)
                    
                    instance_record.last_health_check = datetime.utcnow()
                    
                    # Log event
                    event = SystemEvent(
                        event_type="instance_status_changed",
                        entity_type="instance",
                        entity_id=instance_id,
                        description=f"Instance '{instance_id}' status changed to {status.value}",
                        details={"pid": pid, "error": health_error} if health_error else {"pid": pid},
                        severity="error" if status == InstanceStatus.ERROR else "info"
                    )
                    db.add(event)
                    
                    db.commit()
                    logger.info(f"Updated instance '{instance_id}' status to {status.value}")
            except Exception as e:
                logger.error(f"Failed to update instance status: {str(e)}")
                db.rollback()
    
    def delete_instance(self, instance_id: str):
        """Delete instance from database"""
        with get_db() as db:
            try:
                instance_record = db.query(InstanceRecord).filter_by(id=instance_id).first()
                if instance_record:
                    db.delete(instance_record)
                    
                    # Log event
                    event = SystemEvent(
                        event_type="instance_deleted",
                        entity_type="instance",
                        entity_id=instance_id,
                        description=f"Instance '{instance_id}' deleted from database"
                    )
                    db.add(event)
                    
                    db.commit()
                    logger.info(f"Deleted instance '{instance_id}' from database")
            except Exception as e:
                logger.error(f"Failed to delete instance: {str(e)}")
                db.rollback()
    
    def get_all_instances(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all instances from database"""
        with get_db() as db:
            query = db.query(InstanceRecord)
            if model_name:
                query = query.filter_by(model_name=model_name)
            instances = query.all()
            # Convert to dicts to avoid session issues
            return [instance.to_dict() for instance in instances]
    
    def get_instance(self, instance_id: str) -> Optional[InstanceRecord]:
        """Get specific instance from database"""
        with get_db() as db:
            return db.query(InstanceRecord).filter_by(id=instance_id).first()
    
    def update_instance_health(self, instance_id: str, is_healthy: bool,
                              error: Optional[str] = None):
        """Update instance health status"""
        with get_db() as db:
            try:
                instance_record = db.query(InstanceRecord).filter_by(id=instance_id).first()
                if instance_record:
                    instance_record.is_healthy = is_healthy
                    instance_record.health_error = error
                    instance_record.last_health_check = datetime.utcnow()
                    
                    if not is_healthy and instance_record.status == InstanceStatus.RUNNING:
                        instance_record.status = InstanceStatus.UNHEALTHY
                    
                    db.commit()
            except Exception as e:
                logger.error(f"Failed to update instance health: {str(e)}")
                db.rollback()
    
    def increment_restart_count(self, instance_id: str):
        """Increment instance restart count"""
        with get_db() as db:
            try:
                instance_record = db.query(InstanceRecord).filter_by(id=instance_id).first()
                if instance_record:
                    instance_record.restart_count += 1
                    db.commit()
            except Exception as e:
                logger.error(f"Failed to increment restart count: {str(e)}")
                db.rollback()
    
    # System operations
    
    def get_recent_events(self, limit: int = 100, 
                         entity_type: Optional[str] = None,
                         severity: Optional[str] = None) -> List[SystemEvent]:
        """Get recent system events"""
        with get_db() as db:
            query = db.query(SystemEvent)
            
            if entity_type:
                query = query.filter_by(entity_type=entity_type)
            if severity:
                query = query.filter_by(severity=severity)
            
            return query.order_by(SystemEvent.timestamp.desc()).limit(limit).all()
    
    def cleanup_old_events(self, days: int = 30):
        """Delete events older than specified days"""
        with get_db() as db:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                deleted = db.query(SystemEvent).filter(
                    SystemEvent.timestamp < cutoff_date
                ).delete()
                db.commit()
                logger.info(f"Deleted {deleted} old events")
            except Exception as e:
                logger.error(f"Failed to cleanup old events: {str(e)}")
                db.rollback()