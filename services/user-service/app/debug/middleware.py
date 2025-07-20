# MDA-GENERATED-START: debug-middleware
"""
Debug middleware for flow execution tracking
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.debug import debugger, ExecutionMode


class DebugMiddleware(BaseHTTPMiddleware):
    """Middleware to enable debug mode based on request headers"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Check for debug header
        debug_mode = request.headers.get("X-Debug-Mode", "").lower()
        
        # Set debugger mode based on header
        if debug_mode == "debug":
            debugger.mode = ExecutionMode.DEBUG
        elif debug_mode == "step":
            debugger.mode = ExecutionMode.STEP
        else:
            debugger.mode = ExecutionMode.NORMAL
        
        # Process request
        response = await call_next(request)
        
        # Reset to normal mode after request
        debugger.mode = ExecutionMode.NORMAL
        
        return response
# MDA-GENERATED-END: debug-middleware