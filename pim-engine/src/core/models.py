"""Core data models for PIM Engine"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# Re-export instance models
from .instance_models import (
    Instance, InstanceStatus, InstanceConfig, 
    ProcessInfo, InstanceMetrics
)


class AttributeType(str, Enum):
    """Supported attribute types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    JSON = "json"
    REFERENCE = "reference"
    ENUM = "enum"


class Attribute(BaseModel):
    """Entity attribute definition"""
    name: str
    type: AttributeType
    required: bool = True
    unique: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)
    reference_entity: Optional[str] = None  # For reference types
    enum_values: Optional[List[str]] = None  # For enum types


class Entity(BaseModel):
    """PIM Entity definition"""
    name: str
    description: Optional[str] = None
    attributes: List[Attribute]
    constraints: List[str] = Field(default_factory=list)
    indexes: List[str] = Field(default_factory=list)
    
    def get_attribute(self, name: str) -> Optional[Attribute]:
        """Get attribute by name"""
        return next((attr for attr in self.attributes if attr.name == name), None)


class Method(BaseModel):
    """Service method definition"""
    name: str
    description: Optional[str] = None
    parameters: Dict[str, str] = Field(default_factory=dict)
    return_type: Optional[str] = None
    flow: Optional[str] = None  # Flow name if has flow diagram
    rules: List[str] = Field(default_factory=list)
    is_debuggable: bool = False  # Auto-detected from flow


class Service(BaseModel):
    """PIM Service definition"""
    name: str
    description: Optional[str] = None
    methods: List[Method]
    
    def get_method(self, name: str) -> Optional[Method]:
        """Get method by name"""
        return next((method for method in self.methods if method.name == name), None)


class Flow(BaseModel):
    """Business flow definition"""
    name: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]  # Flow steps from mermaid diagram
    diagram: str  # Original mermaid diagram


class Rule(BaseModel):
    """Business rule definition"""
    name: str
    description: Optional[str] = None
    condition: str  # Natural language condition
    action: str  # Natural language action
    priority: int = 0


class PIMModel(BaseModel):
    """Complete PIM model"""
    domain: str
    version: str = "1.0.0"
    description: Optional[str] = None
    entities: List[Entity] = Field(default_factory=list)
    services: List[Service] = Field(default_factory=list)
    flows: Dict[str, Flow] = Field(default_factory=dict)
    rules: Dict[str, Rule] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Runtime info
    loaded_at: datetime = Field(default_factory=datetime.now)
    
    def get_entity(self, name: str) -> Optional[Entity]:
        """Get entity by name"""
        return next((entity for entity in self.entities if entity.name == name), None)
    
    def get_service(self, name: str) -> Optional[Service]:
        """Get service by name"""
        return next((service for service in self.services if service.name == name), None)


class ModelLoadResult(BaseModel):
    """Result of model loading operation"""
    success: bool
    model: Optional[PIMModel] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    load_time_ms: float = 0.0