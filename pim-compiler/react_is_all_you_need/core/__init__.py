"""
React Agent核心模块 - 极致简化版本

这里包含了React Agent系统的极简实现：
- react_agent_minimal: 极简Agent，自己做笔记
- tool_base: Function基础类，统一的函数抽象

核心理念：
- Agent本身就是智能压缩器
- 做笔记 = 智能压缩
- 最简单的方案就是最好的
"""

# 导入核心组件
from .react_agent_minimal import ReactAgentMinimal
from .tool_base import Function

__all__ = [
    'ReactAgentMinimal',           # 极简React Agent（自己做笔记）
    'Function',                    # 函数基类
]