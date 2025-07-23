"""Runtime instance models for PIM Engine"""

from typing import Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class InstanceStatus(str, Enum):
    """Instance status enumeration"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    UNHEALTHY = "unhealthy"
    ERROR = "error"


class ProcessInfo(BaseModel):
    """Process information for running instance"""
    pid: int
    command: str
    args: list[str] = Field(default_factory=list)
    working_dir: str
    start_time: datetime = Field(default_factory=datetime.now)


class InstanceConfig(BaseModel):
    """Instance configuration"""
    database_type: str = "sqlite"
    database_url: Optional[str] = None
    cache_enabled: bool = False
    cache_ttl: int = 300
    max_workers: int = 4
    debug_mode: bool = False
    env_vars: Dict[str, str] = Field(default_factory=dict)
    extra_config: Dict[str, Any] = Field(default_factory=dict)


class Instance(BaseModel):
    """Model instance definition"""
    id: str
    model_name: str
    model_version: str = "1.0.0"
    port: int
    status: InstanceStatus = InstanceStatus.STARTING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    process_info: Optional[ProcessInfo] = None
    config: InstanceConfig = Field(default_factory=InstanceConfig)
    
    # Runtime statistics
    request_count: int = 0
    error_count: int = 0
    last_health_check: Optional[datetime] = None
    
    # Paths
    instance_dir: str = ""
    database_path: str = ""
    log_file: str = ""
    
    def get_uptime(self) -> str:
        """Calculate instance uptime"""
        if self.status != InstanceStatus.RUNNING:
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
    
    def to_api_response(self) -> dict:
        """Convert to API response format"""
        return {
            "id": self.id,
            "model": self.model_name,
            "port": self.port,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "database": self.database_path,
            "pid": self.process_info.pid if self.process_info else None,
            "uptime": self.get_uptime()
        }


class InstanceMetrics(BaseModel):
    """Instance runtime metrics"""
    instance_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Performance metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    
    # Database metrics
    active_connections: int = 0
    query_count: int = 0
    
    # Health status
    is_healthy: bool = True
    health_message: str = "OK"