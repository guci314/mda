"""Generator implementations"""

from .gemini_cli_generator import GeminiCLIGenerator
from .react_agent_generator import ReactAgentGenerator
from .function_call_agent_generator import FunctionCallAgentGenerator
from .simple_function_call_generator import SimpleFunctionCallGenerator

# Autogen 是可选依赖
try:
    from .autogen_generator import AutogenGenerator
    AUTOGEN_AVAILABLE = True
except ImportError:
    AutogenGenerator = None
    AUTOGEN_AVAILABLE = False

__all__ = [
    'GeminiCLIGenerator',
    'ReactAgentGenerator',
    'FunctionCallAgentGenerator',
    'SimpleFunctionCallGenerator',
    'AutogenGenerator',
    'AUTOGEN_AVAILABLE'
]