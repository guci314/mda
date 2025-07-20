"""Flow debugger for PIM engine"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from utils.logger import setup_logger


class FlowDebugSession(BaseModel):
    """Debug session for a flow execution"""
    session_id: str
    flow_name: str
    start_time: datetime
    current_step: Optional[str] = None
    executed_steps: List[Dict[str, Any]] = []
    variables: Dict[str, Any] = {}
    status: str = "waiting"  # waiting, running, completed, error
    

class FlowDebugger:
    """Debug and visualize flow execution"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.sessions: Dict[str, FlowDebugSession] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
    
    async def create_session(self, flow_name: str) -> str:
        """Create a new debug session"""
        session_id = str(uuid4())
        session = FlowDebugSession(
            session_id=session_id,
            flow_name=flow_name,
            start_time=datetime.now()
        )
        self.sessions[session_id] = session
        self.logger.info(f"Created debug session {session_id} for flow {flow_name}")
        return session_id
    
    async def connect_websocket(self, session_id: str, websocket: WebSocket):
        """Connect a websocket for real-time updates"""
        await websocket.accept()
        self.websocket_connections[session_id] = websocket
        
        # Send initial state
        if session_id in self.sessions:
            await self._send_update(session_id, {
                "type": "session_state",
                "session": self.sessions[session_id].model_dump(mode='json')
            })
    
    async def disconnect_websocket(self, session_id: str):
        """Disconnect websocket"""
        if session_id in self.websocket_connections:
            del self.websocket_connections[session_id]
    
    async def start_flow(self, session_id: str, input_data: Dict[str, Any]):
        """Start flow execution in debug mode"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        session.status = "running"
        session.variables = {"input": input_data}
        
        await self._send_update(session_id, {
            "type": "flow_started",
            "input": input_data
        })
        
        return {"status": "started"}
    
    async def step_executed(
        self, 
        session_id: str, 
        step_id: str, 
        step_type: str,
        label: str,
        result: Any,
        variables: Optional[Dict[str, Any]] = None
    ):
        """Record step execution"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.current_step = step_id
        
        step_info = {
            "step_id": step_id,
            "type": step_type,
            "label": label,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "variables": variables or {}
        }
        
        session.executed_steps.append(step_info)
        
        if variables:
            session.variables.update(variables)
        
        await self._send_update(session_id, {
            "type": "step_executed",
            "step": step_info,
            "current_variables": session.variables
        })
    
    async def flow_completed(self, session_id: str, result: Any):
        """Mark flow as completed"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.status = "completed"
        
        await self._send_update(session_id, {
            "type": "flow_completed",
            "result": result,
            "total_steps": len(session.executed_steps)
        })
    
    async def flow_error(self, session_id: str, error: str):
        """Mark flow as errored"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.status = "error"
        
        await self._send_update(session_id, {
            "type": "flow_error",
            "error": error
        })
    
    async def _send_update(self, session_id: str, data: Dict[str, Any]):
        """Send update via websocket"""
        if session_id in self.websocket_connections:
            try:
                websocket = self.websocket_connections[session_id]
                await websocket.send_json(data)
            except Exception as e:
                self.logger.error(f"Error sending websocket update: {str(e)}")
                await self.disconnect_websocket(session_id)
    
    def get_session(self, session_id: str) -> Optional[FlowDebugSession]:
        """Get session details"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all debug sessions"""
        return [
            {
                "session_id": s.session_id,
                "flow_name": s.flow_name,
                "status": s.status,
                "start_time": s.start_time.isoformat(),
                "steps_executed": len(s.executed_steps)
            }
            for s in self.sessions.values()
        ]