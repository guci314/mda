"""
Agent CLI v2 - 动态执行架构版本

支持动态执行架构的 LLM Agent 命令行工具：
- 双决策器模型（动作决策器 + 步骤决策器）
- 支持一个步骤执行多个动作
- 动态计划调整能力

兼容所有 OpenAI API 的 LLM 服务。
"""

# 从核心模块导入基础类型
from .core import (
    LLMConfig,
    ActionType,
    # 保留这些用于兼容性，虽然 v2 使用不同的实现
    StepStatus as LegacyStepStatus,
    TaskStatus as LegacyTaskStatus,
)

# 从新架构导入
from .core_v2_new import (
    AgentCLI_V2,
    Step,
    Action,
    StepStatus,
)

# 为了向后兼容，创建别名
AgentCLI = AgentCLI_V2

# 工具相关
from .tools import (
    get_all_tools,
    get_tool_by_name,
    get_tools_description,
    AVAILABLE_TOOLS,
)

# 执行器
from .executors import (
    LangChainToolExecutor,
    ToolExecutionResult,
)

__version__ = "2.1.0"
__author__ = "PIM Compiler Team"
__all__ = [
    # 主要类
    "AgentCLI",
    "AgentCLI_V2",
    "LLMConfig",
    
    # 数据类型
    "Step",
    "Action", 
    "StepStatus",
    "ActionType",
    
    # 工具相关
    "get_all_tools",
    "get_tool_by_name",
    "get_tools_description",
    "AVAILABLE_TOOLS",
    
    # 执行器
    "LangChainToolExecutor",
    "ToolExecutionResult",
]