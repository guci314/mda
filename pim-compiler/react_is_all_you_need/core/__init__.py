"""
React Agent核心模块 - 极简版本

这里包含了React Agent系统的极简实现：
- react_agent_minimal: 极简Agent实现，使用自然衰减记忆
- memory_with_natural_decay: 基于压缩的自然记忆衰减系统
- tools: 工具系统，定义Agent的计算边界
"""

# 导入极简版本
from .react_agent_minimal import ReactAgentMinimal
from .memory_with_natural_decay import MemoryWithNaturalDecay, CompressedMemory
from .tools import create_tools

__all__ = [
    'ReactAgentMinimal',           # 极简React Agent
    'MemoryWithNaturalDecay',      # 自然衰减记忆系统
    'CompressedMemory',            # 压缩记忆单元
    'create_tools',                # 工具创建函数
]