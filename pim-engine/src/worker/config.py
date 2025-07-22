"""Worker Configuration"""

from typing import Optional
from pathlib import Path
import json

from pydantic import BaseModel


class WorkerConfig(BaseModel):
    """Worker instance configuration"""
    instance_id: str
    model_name: str
    port: int
    database_url: str
    log_file: str
    redis_url: Optional[str] = None
    debug: bool = False
    
    @classmethod
    def from_file(cls, config_file: str) -> "WorkerConfig":
        """Load configuration from JSON file"""
        with open(config_file, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def get_models_path(self) -> Path:
        """Get the models directory path"""
        # Assume models are in the standard location
        return Path(__file__).parent.parent.parent / "models"