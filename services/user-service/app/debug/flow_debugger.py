# MDA-GENERATED-START: flow-debugger
"""
Service-level flow debugger implementation
"""
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import asyncio
import uuid
from enum import Enum
import time
import json

from app.debug.flow_models import (
    BusinessFlow, FlowStep, StepType, ExecutionRecord, DebugSession
)


class ExecutionMode(Enum):
    """Execution modes for the debugger"""
    NORMAL = "normal"      # Normal execution without debugging
    DEBUG = "debug"        # Debug mode with automatic breakpoints
    STEP = "step"          # Single-step execution


class FlowExecutor:
    """Executes a flow with debugging capabilities"""
    
    def __init__(self, session: DebugSession, flow: BusinessFlow, on_state_change=None):
        self.session = session
        self.flow = flow
        self.current_step_index = 0
        self.execution_paused = False
        self.stop_requested = False
        self.on_state_change = on_state_change
    
    async def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the flow"""
        self.session.context = context
        self.session.status = "running"
        
        try:
            # Start from the first step
            current_step_id = self.flow.start_step
            
            while current_step_id and not self.stop_requested:
                step = self._get_step_by_id(current_step_id)
                if not step:
                    raise ValueError(f"Step {current_step_id} not found")
                
                # Check for breakpoint
                if current_step_id in self.session.breakpoints:
                    self.session.status = "paused"
                    self.execution_paused = True
                    # Wait for continue signal
                    while self.execution_paused and not self.stop_requested:
                        await asyncio.sleep(0.1)
                
                if self.stop_requested:
                    break
                
                # Execute the step
                self.session.current_step = current_step_id
                
                # Notify state change
                if self.on_state_change:
                    await self.on_state_change('step_started', {
                        'step_id': current_step_id,
                        'step_name': step.name
                    })
                
                start_time = time.time()
                
                try:
                    # Execute step (in real implementation, this would call the actual function)
                    result = await self._execute_step(step, self.session.context)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Record execution
                    record = ExecutionRecord(
                        timestamp=datetime.now(),
                        step_id=step.id,
                        step_name=step.name,
                        success=True,
                        duration_ms=duration_ms,
                        inputs=step.inputs,
                        outputs=result or {},
                        error=None
                    )
                    self.session.history.append(record)
                    
                    # Notify step completed
                    if self.on_state_change:
                        await self.on_state_change('step_completed', {
                            'step_id': current_step_id,
                            'step_name': step.name,
                            'success': True
                        })
                    
                    # Update context with outputs
                    if result:
                        self.session.context.update(result)
                    
                    # Move to next step
                    if step.next_steps:
                        current_step_id = step.next_steps[0]
                    else:
                        current_step_id = None
                        
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    record = ExecutionRecord(
                        timestamp=datetime.now(),
                        step_id=step.id,
                        step_name=step.name,
                        success=False,
                        duration_ms=duration_ms,
                        inputs=step.inputs,
                        outputs={},
                        error=str(e)
                    )
                    self.session.history.append(record)
                    raise
            
            self.session.status = "completed"
            return self.session.context
            
        except Exception as e:
            self.session.status = "error"
            raise
    
    def _get_step_by_id(self, step_id: str) -> Optional[FlowStep]:
        """Get a step by its ID"""
        for step in self.flow.steps:
            if step.id == step_id:
                return step
        return None
    
    async def _execute_step(self, step: FlowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step (placeholder for actual execution)"""
        # In real implementation, this would execute the actual step function
        # For now, we'll simulate execution
        await asyncio.sleep(0.1)  # Simulate work
        
        # Return simulated outputs based on step type
        if step.step_type == StepType.VALIDATION:
            return {"validated": True}
        elif step.step_type == StepType.ACTION:
            return {"action_completed": True}
        else:
            return {}
    
    def pause(self):
        """Pause execution"""
        self.execution_paused = True
        self.session.status = "paused"
    
    def resume(self):
        """Resume execution"""
        self.execution_paused = False
        self.session.status = "running"
    
    def stop(self):
        """Stop execution"""
        self.stop_requested = True
        self.session.status = "stopped"


class ServiceDebugger:
    """Service-level flow debugger"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.flows: Dict[str, BusinessFlow] = {}
        self.sessions: Dict[str, DebugSession] = {}
        self.executors: Dict[str, FlowExecutor] = {}
        self.mode = ExecutionMode.NORMAL
    
    def register_flow(self, flow: BusinessFlow):
        """Register a business flow for debugging"""
        self.flows[flow.name] = flow
    
    async def create_session(self, flow_name: str) -> str:
        """Create a new debug session"""
        if flow_name not in self.flows:
            raise ValueError(f"Flow {flow_name} not found")
        
        session_id = str(uuid.uuid4())
        session = DebugSession(
            id=session_id,
            flow_name=flow_name,
            created_at=datetime.now()
        )
        self.sessions[session_id] = session
        
        # Create executor for the session with callback
        executor = FlowExecutor(session, self.flows[flow_name], None)
        self.executors[session_id] = executor
        
        return session_id
    
    async def execute_with_debug(
        self,
        flow_name: str,
        context: Dict[str, Any],
        mode: ExecutionMode = ExecutionMode.NORMAL
    ) -> Any:
        """Execute a flow with debugging capabilities"""
        session_id = await self.create_session(flow_name)
        session = self.sessions[session_id]
        executor = self.executors[session_id]
        
        # Set breakpoints based on mode
        if mode == ExecutionMode.DEBUG:
            # Add breakpoints to all steps
            flow = self.flows[flow_name]
            for step in flow.steps:
                session.breakpoints.append(step.id)
        
        # Execute the flow
        result = await executor.execute(context)
        
        return result
    
    def get_session(self, session_id: str) -> Optional[DebugSession]:
        """Get a debug session by ID"""
        return self.sessions.get(session_id)
    
    def get_executor(self, session_id: str) -> Optional[FlowExecutor]:
        """Get a flow executor by session ID"""
        return self.executors.get(session_id)
    
    def set_executor_callback(self, session_id: str, callback):
        """Set the state change callback for an executor"""
        executor = self.executors.get(session_id)
        if executor:
            executor.on_state_change = callback
    
    def list_flows(self) -> List[Dict[str, Any]]:
        """List all registered flows"""
        flows = []
        for name, flow in self.flows.items():
            flows.append({
                "name": flow.name,
                "description": flow.description,
                "steps": len(flow.steps),
                "start_step": flow.start_step
            })
        return flows
    
    def get_flow_detail(self, flow_name: str) -> Dict[str, Any]:
        """Get detailed information about a flow"""
        if flow_name not in self.flows:
            raise ValueError(f"Flow {flow_name} not found")
        
        flow = self.flows[flow_name]
        return {
            "name": flow.name,
            "description": flow.description,
            "steps": [step.model_dump() for step in flow.steps],
            "diagram": self.generate_mermaid_diagram(flow)
        }
    
    def generate_mermaid_diagram(self, flow: BusinessFlow) -> str:
        """Generate a Mermaid diagram for a flow"""
        lines = ["flowchart TD"]
        
        # Add start node
        lines.append('    Start([开始])')
        
        # Add nodes
        for step in flow.steps:
            if step.step_type == StepType.ACTION:
                shape = f'{step.id}["{step.name}"]'
            elif step.step_type == StepType.VALIDATION:
                shape = f'{step.id}{{{step.name}}}'
            else:
                shape = f'{step.id}("{step.name}")'
            lines.append(f'    {shape}')
        
        # Add end node
        lines.append('    End([结束])')
        
        # Add edges
        lines.append(f"    Start --> {flow.start_step}")
        
        for step in flow.steps:
            if step.next_steps:
                for next_step in step.next_steps:
                    lines.append(f"    {step.id} --> {next_step}")
            else:
                # If no next steps, connect to End
                lines.append(f"    {step.id} --> End")
        
        return "\n".join(lines)
# MDA-GENERATED-END: flow-debugger