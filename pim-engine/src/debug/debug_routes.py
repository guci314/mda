"""Debug API routes"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Any

from debug.flow_debugger import FlowDebugger


def create_debug_routes(flow_debugger: FlowDebugger) -> APIRouter:
    """Create debug API routes"""
    router = APIRouter(prefix="/debug", tags=["Debug"])
    
    @router.post("/session/create")
    async def create_debug_session(flow_name: str):
        """Create a new debug session for a flow"""
        session_id = await flow_debugger.create_session(flow_name)
        return {"session_id": session_id}
    
    @router.get("/session/{session_id}")
    async def get_session(session_id: str):
        """Get debug session details"""
        session = flow_debugger.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session.model_dump(mode='json')
    
    @router.get("/sessions")
    async def list_sessions():
        """List all debug sessions"""
        return {"sessions": flow_debugger.list_sessions()}
    
    @router.post("/session/{session_id}/start")
    async def start_debug_flow(session_id: str, input_data: Dict[str, Any]):
        """Start flow execution in debug mode"""
        result = await flow_debugger.start_flow(session_id, input_data)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    
    @router.websocket("/session/{session_id}/ws")
    async def debug_websocket(websocket: WebSocket, session_id: str):
        """WebSocket for real-time debug updates"""
        await flow_debugger.connect_websocket(session_id, websocket)
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            await flow_debugger.disconnect_websocket(session_id)
    
    @router.get("/ui")
    async def debug_ui():
        """Serve debug UI"""
        from fastapi.responses import HTMLResponse
        from pathlib import Path
        
        # Try to read the debug.html file
        debug_html_path = Path("/app/static/debug.html")
        if debug_html_path.exists():
            with open(debug_html_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        
        # Fallback response
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PIM Flow Debugger</title>
        </head>
        <body>
            <h1>PIM Flow Debugger</h1>
            <p>Debug UI not found. Please ensure debug.html is in the static directory.</p>
            <p>WebSocket URL: /debug/session/{session_id}/ws</p>
            <p>Create Session URL: /debug/session/create</p>
        </body>
        </html>
        """)
    
    return router