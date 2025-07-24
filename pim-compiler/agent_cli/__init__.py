"""
Agent CLI - 通用的 LLM Agent 命令行工具

支持任何兼容 OpenAI API 的 LLM 服务：
- OpenAI (GPT-4, GPT-3.5)
- DeepSeek
- 通义千问 (Qwen)
- 智谱 (ChatGLM)
- 月之暗面 (Moonshot)
- 其他兼容服务
"""

from .core import (
    AgentCLI,
    Action,
    ActionType,
    Task,
    Step,
    StepStatus,
    TaskStatus,
    Tool,
    FileReader,
    FileWriter,
    FileLister,
    LLMConfig
)

__version__ = "2.0.0"
__author__ = "PIM Compiler Team"
__all__ = [
    "AgentCLI",
    "Action",
    "ActionType",
    "Task",
    "Step",
    "StepStatus",
    "TaskStatus",
    "Tool",
    "FileReader",
    "FileWriter",
    "FileLister",
    "LLMConfig"
]