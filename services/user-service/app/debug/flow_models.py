# MDA-GENERATED-START: flow-models
"""
Flow model definitions for debugging
"""
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Types of flow steps"""
    VALIDATION = "validation"
    ACTION = "action"
    DECISION = "decision"
    INTEGRATION = "integration"


class FlowStep(BaseModel):
    """A single step in a business flow"""
    id: str
    name: str
    step_type: StepType
    description: Optional[str] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    next_steps: List[str] = Field(default_factory=list)


class BusinessFlow(BaseModel):
    """Business flow definition"""
    name: str
    description: str
    start_step: str
    steps: List[FlowStep]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionRecord(BaseModel):
    """Record of a step execution"""
    timestamp: datetime
    step_id: str
    step_name: str
    success: bool
    duration_ms: float
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DebugSession(BaseModel):
    """Debug session state"""
    id: str
    flow_name: str
    status: str = "idle"
    created_at: datetime
    current_step: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    breakpoints: List[str] = Field(default_factory=list)
    history: List[ExecutionRecord] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
# MDA-GENERATED-END: flow-models