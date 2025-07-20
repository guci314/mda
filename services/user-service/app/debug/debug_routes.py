# MDA-GENERATED-START: debug-routes
"""
Debug API routes for flow visualization and control
"""
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

from app.debug import debugger
from app.debug.flow_models import DebugSession


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


async def send_json_with_datetime(websocket: WebSocket, data: dict):
    """Helper to send JSON with datetime serialization"""
    json_str = json.dumps(data, cls=DateTimeEncoder)
    await websocket.send_text(json_str)


router = APIRouter()


@router.get("/")
async def debug_home():
    """Debug interface home page"""
    return {
        "service": debugger.service_name,
        "flows": list(debugger.flows.keys()),
        "active_sessions": len(debugger.sessions),
        "ui_url": "/debug/ui"
    }


@router.get("/flows")
async def list_flows():
    """List all debuggable flows"""
    return {"flows": debugger.list_flows()}


@router.get("/flows/{flow_name}")
async def get_flow_detail(flow_name: str):
    """Get detailed flow information"""
    try:
        detail = debugger.get_flow_detail(flow_name)
        return detail
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions")
async def create_debug_session(request: Dict[str, Any]):
    """Create a new debug session"""
    flow_name = request.get("flow_name")
    initial_context = request.get("initial_context", {})
    
    if not flow_name:
        raise HTTPException(status_code=400, detail="flow_name is required")
    
    try:
        session_id = await debugger.create_session(flow_name)
        session = debugger.get_session(session_id)
        session.context = initial_context
        
        return {
            "session_id": session_id,
            "flow_name": flow_name,
            "status": "created",
            "websocket_url": f"/debug/sessions/{session_id}/ws"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    session = debugger.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.model_dump(mode='json')


@router.websocket("/sessions/{session_id}/ws")
async def debug_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for debug session control"""
    session = debugger.get_session(session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    executor = debugger.get_executor(session_id)
    if not executor:
        await websocket.close(code=4004, reason="Executor not found")
        return
    
    await websocket.accept()
    
    # Set up callback for executor state changes
    async def on_state_change(event_type: str, data: dict):
        """Handle state changes from executor"""
        await send_json_with_datetime(websocket, {
            "type": event_type,
            "data": data,
            "session": session.model_dump(mode='json')
        })
    
    debugger.set_executor_callback(session_id, on_state_change)
    
    try:
        while True:
            # Receive command
            data = await websocket.receive_json()
            command = data.get("command")
            
            if command == "start":
                # Start execution
                import asyncio
                
                async def execute_and_update():
                    """Execute flow and send updates"""
                    try:
                        # Update status
                        session.status = "running"
                        await send_json_with_datetime(websocket, {
                            "type": "execution_started",
                            "session_id": session_id
                        })
                        
                        # Execute the flow
                        await executor.execute(session.context)
                        
                        # Execution completed
                        session.status = "completed"
                        await send_json_with_datetime(websocket, {
                            "type": "execution_completed",
                            "session_id": session_id
                        })
                    except Exception as e:
                        session.status = "error"
                        await send_json_with_datetime(websocket, {
                            "type": "execution_error",
                            "error": str(e)
                        })
                
                asyncio.create_task(execute_and_update())
                
            elif command == "continue":
                # Continue execution
                executor.resume()
                
            elif command == "step":
                # Step over
                executor.resume()
                # In step mode, we'd pause at the next step
                
            elif command == "stop":
                # Stop execution
                executor.stop()
                break
                
            elif command == "add_breakpoint":
                # Add breakpoint
                step_id = data.get("step_id")
                if step_id and step_id not in session.breakpoints:
                    session.breakpoints.append(step_id)
                    
            elif command == "remove_breakpoint":
                # Remove breakpoint
                step_id = data.get("step_id")
                if step_id and step_id in session.breakpoints:
                    session.breakpoints.remove(step_id)
                    
            elif command == "inspect":
                # Inspect context
                path = data.get("path", "")
                value = session.context
                for key in path.split(".") if path else []:
                    value = value.get(key, None)
                    if value is None:
                        break
                
                await send_json_with_datetime(websocket, {
                    "type": "inspection",
                    "path": path,
                    "value": value
                })
            
            # Send state update
            await send_json_with_datetime(websocket, {
                "type": "state_update",
                "session": session.model_dump(mode='json'),
                "current_step": session.current_step,
                "context": session.context,
                "status": session.status,
                "history": [h.model_dump(mode='json') for h in session.history[-10:]]
            })
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await send_json_with_datetime(websocket, {
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()


@router.get("/ui", response_class=HTMLResponse)
async def debug_ui():
    """Serve the debug UI"""
    import os
    from pathlib import Path
    
    # Get the absolute path to the static file
    current_dir = Path(__file__).parent
    html_path = current_dir / "static" / "index.html"
    
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Return a simple UI if the file doesn't exist yet
        return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Flow Debugger</title>
</head>
<body>
    <h1>User Service Flow Debugger</h1>
    <p>Debug UI is being set up...</p>
    <p>Available endpoints:</p>
    <ul>
        <li><a href="/debug/">Debug API Home</a></li>
        <li><a href="/debug/flows">List Flows</a></li>
        <li><a href="/docs">API Documentation</a></li>
    </ul>
</body>
</html>
        """)
# MDA-GENERATED-END: debug-routes