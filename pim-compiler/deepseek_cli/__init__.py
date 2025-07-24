"""
DeepSeek CLI - Gemini CLI 的中国友好替代方案

使用 DeepSeek API 实现类似 Gemini CLI 的功能，
专门为中国用户优化，解决网络访问问题。
"""

from .core import (
    DeepSeekCLI,
    DeepSeekLLM,
    ExecutionPlan,
    Action,
    ActionType,
    Tool,
    FileReader,
    FileWriter,
    FileLister
)

__version__ = "1.0.0"
__author__ = "PIM Compiler Team"
__all__ = [
    "DeepSeekCLI",
    "DeepSeekLLM",
    "ExecutionPlan",
    "Action",
    "ActionType",
    "Tool",
    "FileReader",
    "FileWriter",
    "FileLister"
]