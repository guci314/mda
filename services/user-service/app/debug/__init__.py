# MDA-GENERATED-START: debug-init
"""Debug module for flow visualization and debugging"""
from app.debug.flow_debugger import ServiceDebugger, ExecutionMode

# Initialize the global debugger instance
debugger = ServiceDebugger("user-service")

__all__ = ["debugger", "ExecutionMode"]
# MDA-GENERATED-END: debug-init