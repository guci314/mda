"""
Agent CLI v3 - 增强版，支持任务分类和自适应规划

支持智能任务处理的 LLM Agent 命令行工具：
- 任务分类系统（查询、创建、修改、调试、解释）
- 自适应规划（根据任务类型选择策略）
- 查询优化（避免过度规划）
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

# 从最新 v3 增强版导入
from .core_v3_enhanced import AgentCLI_V3_Enhanced

# 从 v2 版本导入（用于兼容性）
from .core_v2_improved import AgentCLI_V2_Improved

# 从 core_v2_new 导入数据类型（v3 也复用了这些）
from .core_v2_new import (
    Step,
    Action,
    StepStatus,
)

# 导入任务分类相关组件
from .task_classifier import TaskClassifier, TaskType
from .query_handler import QueryHandler

# 为了向后兼容，创建别名
AgentCLI = AgentCLI_V3_Enhanced  # 默认使用 v3
AgentCLI_V2 = AgentCLI_V2_Improved  # 保留 v2 访问
AgentCLI_V3 = AgentCLI_V3_Enhanced  # 明确的 v3 访问

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

__version__ = "3.0.0"  # 升级到 v3 增强版
__author__ = "PIM Compiler Team"
__all__ = [
    # 主要类
    "AgentCLI",
    "AgentCLI_V2",
    "AgentCLI_V3",
    "AgentCLI_V2_Improved",
    "AgentCLI_V3_Enhanced",
    "LLMConfig",
    
    # 数据类型
    "Step",
    "Action", 
    "StepStatus",
    "ActionType",
    
    # 任务分类相关
    "TaskClassifier",
    "TaskType",
    "QueryHandler",
    
    # 工具相关
    "get_all_tools",
    "get_tool_by_name",
    "get_tools_description",
    "AVAILABLE_TOOLS",
    
    # 执行器
    "LangChainToolExecutor",
    "ToolExecutionResult",
]