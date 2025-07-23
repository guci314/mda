"""Database models for persistent storage"""

from sqlalchemy import Column, String, DateTime, JSON, Integer, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class ModelStatus(str, enum.Enum):
    """Model loading status"""
    LOADING = "loading"
    LOADED = "loaded"
    COMPILING = "compiling"
    COMPILED = "compiled"
    ERROR = "error"
    UNLOADING = "unloading"


class InstanceStatus(str, enum.Enum):
    """Instance status"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    UNHEALTHY = "unhealthy"
    ERROR = "error"


class ModelRecord(Base):
    """Persistent storage for loaded models"""
    __tablename__ = "models"
    
    # Primary key
    name = Column(String(255), primary_key=True)
    
    # Model information
    version = Column(String(50))
    description = Column(Text)
    source_file = Column(String(500))
    format = Column(String(20))  # yaml, markdown
    
    # Status
    status = Column(SQLEnum(ModelStatus), default=ModelStatus.LOADING)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    entities_count = Column(Integer, default=0)
    services_count = Column(Integer, default=0)
    flows_count = Column(Integer, default=0)
    rules_count = Column(Integer, default=0)
    
    # Timestamps
    loaded_at = Column(DateTime, default=datetime.utcnow)
    compiled_at = Column(DateTime, nullable=True)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Model content (for recovery)
    model_content = Column(Text)  # Store the original model file content
    compiled_model = Column(JSON, nullable=True)  # Store compiled model structure
    
    # Configuration
    config = Column(JSON, default=dict)
    
    # Relationships
    instances = relationship("InstanceRecord", back_populates="model", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "source_file": self.source_file,
            "format": self.format,
            "status": self.status.value if self.status else None,
            "error_message": self.error_message,
            "entities": self.entities_count,
            "services": self.services_count,
            "flows": self.flows_count,
            "rules": self.rules_count,
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "compiled_at": self.compiled_at.isoformat() if self.compiled_at else None,
            "instances_count": len(self.instances) if self.instances else 0,
            "config": self.config or {}
        }


class InstanceRecord(Base):
    """Persistent storage for model instances"""
    __tablename__ = "instances"
    
    # Primary key
    id = Column(String(255), primary_key=True)
    
    # Model reference
    model_name = Column(String(255), ForeignKey("models.name", ondelete="CASCADE"))
    model = relationship("ModelRecord", back_populates="instances")
    
    # Instance information
    port = Column(Integer, unique=True)
    pid = Column(Integer, nullable=True)
    status = Column(SQLEnum(InstanceStatus), default=InstanceStatus.STARTING)
    
    # Configuration
    config = Column(JSON, default=dict)
    database_path = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    last_health_check = Column(DateTime, nullable=True)
    
    # Health information
    is_healthy = Column(Boolean, default=False)
    health_error = Column(Text, nullable=True)
    restart_count = Column(Integer, default=0)
    
    # Resource usage (optional)
    memory_usage = Column(Integer, nullable=True)  # in MB
    cpu_usage = Column(Integer, nullable=True)  # percentage
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "model": self.model_name,
            "port": self.port,
            "pid": self.pid,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "database": self.database_path,
            "uptime": self._get_uptime(),
            "is_healthy": self.is_healthy,
            "restart_count": self.restart_count,
            "config": self.config or {}
        }
    
    def _get_uptime(self) -> str:
        """Calculate uptime"""
        if self.status != InstanceStatus.RUNNING or not self.started_at:
            return "0s"
        
        end_time = self.stopped_at or datetime.utcnow()
        delta = end_time - self.started_at
        
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class SystemEvent(Base):
    """System events for audit and debugging"""
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(50))  # model_loaded, instance_created, etc.
    entity_type = Column(String(50))  # model, instance
    entity_id = Column(String(255))
    description = Column(Text)
    details = Column(JSON, nullable=True)
    severity = Column(String(20), default="info")  # info, warning, error
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "description": self.description,
            "details": self.details,
            "severity": self.severity
        }