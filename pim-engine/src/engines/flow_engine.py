"""Flow engine for executing business processes"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import asyncio
import uuid

from core.models import Flow
from engines.rule_engine import RuleEngine
from utils.logger import setup_logger


class StepType(str, Enum):
    """Types of flow steps"""
    START = "start"
    END = "end"
    PROCESS = "process"
    DECISION = "decision"
    VALIDATION = "validation"
    ACTION = "action"


class StepStatus(str, Enum):
    """Status of step execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class FlowStep:
    """Represents a step in a flow"""
    
    def __init__(
        self,
        id: str,
        name: str,
        step_type: StepType,
        next_steps: List[str] = None
    ):
        self.id = id
        self.name = name
        self.step_type = step_type
        self.next_steps = next_steps or []
        self.status = StepStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None


class FlowSession:
    """Represents a flow execution session"""
    
    def __init__(self, flow_name: str, session_id: str = None):
        self.id = session_id or str(uuid.uuid4())
        self.flow_name = flow_name
        self.status = "initialized"
        self.context: Dict[str, Any] = {}
        self.steps_executed: List[str] = []
        self.current_step: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None


class FlowEngine:
    """Execute business flows defined in PIM models"""
    
    def __init__(self, rule_engine: RuleEngine):
        self.logger = setup_logger(__name__)
        self.rule_engine = rule_engine
        self.flows: Dict[str, Flow] = {}
        self.sessions: Dict[str, FlowSession] = {}
        self.step_definitions: Dict[str, Dict[str, FlowStep]] = {}
        
        # Callbacks for debugging
        self.debug_callbacks: Dict[str, Any] = {}
    
    async def load_flows(self, flows: Dict[str, Flow]):
        """Load flows into the engine"""
        self.flows = flows
        
        # Parse flow steps
        for flow_name, flow in flows.items():
            steps = self._parse_flow_steps(flow)
            self.step_definitions[flow_name] = steps
        
        self.logger.info(f"Loaded {len(flows)} flows")
    
    async def execute_flow(
        self,
        flow_name: str,
        input_data: Dict[str, Any],
        session_id: Optional[str] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        """Execute a flow"""
        if flow_name not in self.flows:
            raise ValueError(f"Flow '{flow_name}' not found")
        
        # Create session
        session = FlowSession(flow_name, session_id)
        session.context = {"input": input_data, "output": {}}
        session.status = "running"
        
        self.sessions[session.id] = session
        
        try:
            # Get flow definition
            flow = self.flows[flow_name]
            steps = self.step_definitions[flow_name]
            
            # Find start step
            start_step = self._find_start_step(steps)
            if not start_step:
                raise ValueError("No start step found in flow")
            
            # Execute flow
            await self._execute_step_recursive(
                session,
                start_step,
                steps,
                debug
            )
            
            # Mark session as completed
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            
            return {
                "success": True,
                "session_id": session.id,
                "output": session.context.get("output", {}),
                "steps_executed": session.steps_executed
            }
            
        except Exception as e:
            # Mark session as failed
            session.status = "failed"
            session.error = str(e)
            session.completed_at = datetime.utcnow()
            
            self.logger.error(f"Flow execution failed: {e}")
            
            return {
                "success": False,
                "session_id": session.id,
                "error": str(e),
                "steps_executed": session.steps_executed
            }
    
    async def _execute_step_recursive(
        self,
        session: FlowSession,
        step: FlowStep,
        all_steps: Dict[str, FlowStep],
        debug: bool
    ):
        """Recursively execute flow steps"""
        # Mark step as current
        session.current_step = step.id
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()
        
        # Notify debug callback if set
        if debug:
            await self._notify_debug_callback(
                session.id,
                "step_started",
                {
                    "step_id": step.id,
                    "step_name": step.name,
                    "step_type": step.step_type
                }
            )
        
        try:
            # Execute step based on type
            if step.step_type == StepType.START:
                result = True
            elif step.step_type == StepType.END:
                result = True
            elif step.step_type == StepType.VALIDATION:
                result = await self._execute_validation_step(step, session)
            elif step.step_type == StepType.ACTION:
                result = await self._execute_action_step(step, session)
            elif step.step_type == StepType.DECISION:
                result = await self._execute_decision_step(step, session)
            else:
                result = await self._execute_process_step(step, session)
            
            # Update step status
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            step.result = result
            
            # Add to executed steps
            session.steps_executed.append(step.id)
            
            # Notify debug callback
            if debug:
                await self._notify_debug_callback(
                    session.id,
                    "step_completed",
                    {
                        "step_id": step.id,
                        "result": result,
                        "duration_ms": (
                            step.completed_at - step.started_at
                        ).total_seconds() * 1000
                    }
                )
            
            # Determine next steps
            next_step_ids = self._determine_next_steps(step, result)
            
            # Execute next steps
            for next_step_id in next_step_ids:
                if next_step_id in all_steps:
                    next_step = all_steps[next_step_id]
                    await self._execute_step_recursive(
                        session,
                        next_step,
                        all_steps,
                        debug
                    )
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.utcnow()
            
            if debug:
                await self._notify_debug_callback(
                    session.id,
                    "step_failed",
                    {
                        "step_id": step.id,
                        "error": str(e)
                    }
                )
            
            raise e
    
    async def _execute_validation_step(
        self,
        step: FlowStep,
        session: FlowSession
    ) -> bool:
        """Execute a validation step"""
        # Extract validation rules from step name
        if "验证" in step.name or "validate" in step.name.lower():
            # Common validations
            if "邮箱" in step.name or "email" in step.name.lower():
                email = session.context.get("input", {}).get("email", "")
                return "@" in email
            elif "必填" in step.name or "required" in step.name.lower():
                # Check required fields
                input_data = session.context.get("input", {})
                return all(input_data.get(field) for field in ["name", "email"])
        
        return True
    
    async def _execute_action_step(
        self,
        step: FlowStep,
        session: FlowSession
    ) -> Any:
        """Execute an action step"""
        # Simulate actions based on step name
        if "创建" in step.name or "create" in step.name.lower():
            # Create record
            record = {
                "id": str(uuid.uuid4()),
                **session.context.get("input", {}),
                "created_at": datetime.utcnow().isoformat()
            }
            session.context["output"]["created_record"] = record
            return record
        elif "发送" in step.name or "send" in step.name.lower():
            # Send notification
            return {"sent": True, "timestamp": datetime.utcnow().isoformat()}
        
        return {"action_executed": step.name}
    
    async def _execute_decision_step(
        self,
        step: FlowStep,
        session: FlowSession
    ) -> bool:
        """Execute a decision step"""
        # Extract condition from step name
        if "检查" in step.name or "check" in step.name.lower():
            # Common checks
            if "唯一性" in step.name or "unique" in step.name.lower():
                # Simulate uniqueness check
                return True  # Assume unique for demo
            elif "权限" in step.name or "permission" in step.name.lower():
                # Check permissions
                user = session.context.get("user", {})
                return user.get("role") in ["admin", "manager"]
        
        # Use rule engine for complex decisions
        if step.name in self.rule_engine.rules:
            return await self.rule_engine.execute_rule(
                step.name,
                session.context
            )
        
        return True
    
    async def _execute_process_step(
        self,
        step: FlowStep,
        session: FlowSession
    ) -> Any:
        """Execute a generic process step"""
        # Add step execution to context
        session.context[f"step_{step.id}_executed"] = True
        
        # Simulate processing
        await asyncio.sleep(0.1)  # Simulate work
        
        return {"processed": True}
    
    def _parse_flow_steps(self, flow: Flow) -> Dict[str, FlowStep]:
        """Parse flow steps from flow definition"""
        steps = {}
        
        # Parse steps from diagram or step list
        for step_data in flow.steps:
            step_id = step_data.get("id", str(uuid.uuid4()))
            step_name = step_data.get("label", step_data.get("name", "Unknown"))
            step_type_str = step_data.get("type", "process")
            
            # Map step type
            step_type = StepType.PROCESS
            if step_id.lower() == "start" or "开始" in step_name:
                step_type = StepType.START
            elif step_id.lower() == "end" or "结束" in step_name:
                step_type = StepType.END
            elif step_type_str == "decision" or "?" in step_name:
                step_type = StepType.DECISION
            elif "验证" in step_name or "validate" in step_name.lower():
                step_type = StepType.VALIDATION
            elif "执行" in step_name or "action" in step_type_str:
                step_type = StepType.ACTION
            
            # Get next steps (simplified - would parse from diagram edges)
            next_steps = step_data.get("next", [])
            if isinstance(next_steps, str):
                next_steps = [next_steps]
            
            steps[step_id] = FlowStep(
                id=step_id,
                name=step_name,
                step_type=step_type,
                next_steps=next_steps
            )
        
        # If no explicit steps, create a simple flow
        if not steps:
            steps = {
                "start": FlowStep("start", "Start", StepType.START, ["process"]),
                "process": FlowStep("process", "Process", StepType.PROCESS, ["end"]),
                "end": FlowStep("end", "End", StepType.END)
            }
        
        return steps
    
    def _find_start_step(self, steps: Dict[str, FlowStep]) -> Optional[FlowStep]:
        """Find the start step in a flow"""
        # Look for explicit start step
        for step in steps.values():
            if step.step_type == StepType.START:
                return step
        
        # If no explicit start, use first step
        if steps:
            return list(steps.values())[0]
        
        return None
    
    def _determine_next_steps(
        self,
        step: FlowStep,
        result: Any
    ) -> List[str]:
        """Determine next steps based on current step and result"""
        if step.step_type == StepType.END:
            return []  # No next steps after end
        
        if step.step_type == StepType.DECISION:
            # For decision steps, result determines path
            if isinstance(result, bool):
                # Binary decision
                if len(step.next_steps) >= 2:
                    return [step.next_steps[0] if result else step.next_steps[1]]
            elif isinstance(result, str) and result in step.next_steps:
                # Named path
                return [result]
        
        # Default: follow all next steps
        return step.next_steps
    
    async def _notify_debug_callback(
        self,
        session_id: str,
        event_type: str,
        data: Dict[str, Any]
    ):
        """Notify debug callback if registered"""
        callback = self.debug_callbacks.get(session_id)
        if callback:
            try:
                await callback(event_type, data)
            except Exception as e:
                self.logger.error(f"Debug callback error: {e}")
    
    def set_debug_callback(self, session_id: str, callback):
        """Set debug callback for a session"""
        self.debug_callbacks[session_id] = callback
    
    def get_session(self, session_id: str) -> Optional[FlowSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)