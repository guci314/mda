"""
React Agent核心模块

这里包含了React Agent系统的核心实现：
- react_agent: 主Agent实现，自然语言虚拟机
- tools: 工具系统，定义Agent的计算边界
- langchain_agent_tool: Agent as Tool机制，实现多Agent协作
- debug_tools: 调试专用工具集
"""

# GenericReactAgent是另一个模块的
try:
    from .generic_react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
except ImportError:
    GenericReactAgent = None
    ReactAgentConfig = None
    MemoryLevel = None
# 暂时注释掉有问题的导入
# from .tools import create_tools
# from .langchain_agent_tool import AgentToolWrapper, create_langchain_tool
create_tools = None
AgentToolWrapper = None
create_langchain_tool = None
from .debug_tools import (
    compress_debug_notes,
    check_and_compress_debug_notes,
    create_debug_tools,
    create_init_debug_notes_tool,
    create_fix_python_syntax_errors_tool
)

# 导入Kimi专用Agent
try:
    from .kimi_react_agent import KimiReactAgent
except ImportError:
    # 如果导入失败，创建占位符
    KimiReactAgent = None

# 导入通用ReactAgent和记忆系统
try:
    from .react_agent import ReactAgent
    from .memory_manager import MemoryManager, MemoryMode
    # 为向后兼容保留QwenReactAgent别名
    QwenReactAgent = ReactAgent
except ImportError:
    ReactAgent = None
    QwenReactAgent = None
    MemoryManager = None
    MemoryMode = None

__all__ = [
    'GenericReactAgent',
    'ReactAgentConfig', 
    'MemoryLevel',
    'create_tools',
    'AgentToolWrapper',
    'create_langchain_tool',
    'compress_debug_notes',
    'check_and_compress_debug_notes',
    'create_debug_tools',
    'create_init_debug_notes_tool',
    'create_fix_python_syntax_errors_tool',
    'KimiReactAgent',  # Kimi专用Agent
    'ReactAgent',      # 通用React Agent
    'QwenReactAgent',  # 向后兼容别名
    'MemoryManager',   # 记忆管理器
    'MemoryMode'       # 记忆模式
]