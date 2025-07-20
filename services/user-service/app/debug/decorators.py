# MDA-GENERATED-START: debug-decorators
"""
Flow debugging decorators
"""
from functools import wraps
import inspect
from typing import Callable, Dict, Any
import asyncio

from app.debug import debugger
from app.debug.flow_models import BusinessFlow, FlowStep, StepType
from app.debug.flow_debugger import ExecutionMode


def parse_function_to_flow(func: Callable, name: str, description: str) -> BusinessFlow:
    """Parse a function to extract flow information"""
    # Get function source code
    source = inspect.getsource(func)
    
    # Simple parsing to find @step decorated functions
    # In a real implementation, this would use AST parsing
    steps = []
    
    # For now, create a simple flow with predefined steps
    # This would be enhanced to actually parse the function
    steps = [
        FlowStep(
            id="validate_data",
            name="验证用户数据",
            step_type=StepType.VALIDATION,
            next_steps=["check_email"]
        ),
        FlowStep(
            id="check_email",
            name="检查邮箱唯一性",
            step_type=StepType.VALIDATION,
            next_steps=["create_record"]
        ),
        FlowStep(
            id="create_record",
            name="创建用户记录",
            step_type=StepType.ACTION,
            next_steps=["send_notification"]
        ),
        FlowStep(
            id="send_notification",
            name="发送欢迎通知",
            step_type=StepType.ACTION,
            next_steps=[]
        )
    ]
    
    return BusinessFlow(
        name=name,
        description=description,
        start_step="validate_data",
        steps=steps
    )


def extract_context(args: tuple, kwargs: dict, func: Callable) -> Dict[str, Any]:
    """Extract context from function arguments"""
    # Get function signature
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    # Convert to dictionary
    context = {}
    for param_name, param_value in bound_args.arguments.items():
        if hasattr(param_value, 'model_dump'):
            # Pydantic model
            context[param_name] = param_value.model_dump()
        elif hasattr(param_value, '__dict__'):
            # Regular object
            context[param_name] = vars(param_value)
        else:
            # Primitive type
            context[param_name] = param_value
    
    return context


def flow(name: str, description: str = ""):
    """Decorator to mark a function as a debuggable business flow"""
    def decorator(func: Callable):
        # Parse function to create flow model
        flow_model = parse_function_to_flow(func, name, description)
        debugger.register_flow(flow_model)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if we're in debug mode
            if debugger.mode == ExecutionMode.NORMAL:
                # Normal execution
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            else:
                # Debug execution
                context = extract_context(args, kwargs, func)
                result = await debugger.execute_with_debug(
                    name,
                    context,
                    debugger.mode
                )
                # Extract the return value from context
                # In a real implementation, this would be more sophisticated
                return result.get("user", result)
        
        # Store metadata
        wrapper._original = func
        wrapper._flow_name = name
        wrapper._is_flow = True
        
        return wrapper
    
    return decorator


def step(name: str, step_type: str = "action"):
    """Decorator to mark a step within a flow"""
    def decorator(func: Callable):
        # Store step metadata
        func._step_name = name
        func._step_type = step_type
        func._is_step = True
        return func
    
    return decorator
# MDA-GENERATED-END: debug-decorators