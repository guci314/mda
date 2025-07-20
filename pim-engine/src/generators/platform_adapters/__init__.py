"""Platform-specific code adapters"""

from .base import PlatformAdapter
from .fastapi_adapter import FastAPIAdapter
# from .spring_adapter import SpringBootAdapter  # Future implementation


def get_platform_adapter(platform: str) -> PlatformAdapter:
    """Get adapter for specific platform"""
    adapters = {
        "fastapi": FastAPIAdapter(),
        # "spring": SpringBootAdapter(),
    }
    
    adapter = adapters.get(platform)
    if not adapter:
        raise ValueError(f"Unsupported platform: {platform}")
        
    return adapter


__all__ = [
    "PlatformAdapter",
    "FastAPIAdapter", 
    "get_platform_adapter"
]