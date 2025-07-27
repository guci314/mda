#!/usr/bin/env python3
"""ReactAgent 三级记忆配置方案"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

class MemoryLevel(Enum):
    """记忆级别枚举"""
    NONE = "none"              # 无记忆 - 快速简单
    BUFFER = "summary_buffer"  # 内存记忆 - 平衡方案
    PERSIST = "sqlite"         # 持久记忆 - 专业项目

@dataclass
class MemoryConfig:
    """记忆配置"""
    level: MemoryLevel
    session_id: Optional[str] = None
    max_token_limit: int = 3000
    db_path: str = "./memory.db"
    
    @classmethod
    def no_memory(cls):
        """无记忆配置"""
        return cls(level=MemoryLevel.NONE)
    
    @classmethod
    def balanced(cls, session_id: Optional[str] = None):
        """平衡配置 - Summary Buffer"""
        return cls(
            level=MemoryLevel.BUFFER,
            session_id=session_id,
            max_token_limit=3000  # 约10-15轮对话
        )
    
    @classmethod
    def professional(cls, session_id: str, db_path: str = "./projects.db"):
        """专业配置 - SQLite"""
        return cls(
            level=MemoryLevel.PERSIST,
            session_id=session_id,
            db_path=db_path
        )


class ReactAgentGenerator:
    """支持三级记忆的生成器"""
    
    def __init__(self, memory_config: MemoryConfig):
        self.memory_config = memory_config
        self.memory = self._create_memory()
    
    def _create_memory(self):
        """根据配置创建记忆"""
        if self.memory_config.level == MemoryLevel.NONE:
            return None
            
        elif self.memory_config.level == MemoryLevel.BUFFER:
            from langchain.memory import ConversationSummaryBufferMemory
            return ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=self.memory_config.max_token_limit,
                memory_key="chat_history",
                return_messages=True
            )
            
        elif self.memory_config.level == MemoryLevel.PERSIST:
            from langchain.memory import ConversationBufferMemory
            from langchain.memory.chat_message_histories import SQLChatMessageHistory
            
            message_history = SQLChatMessageHistory(
                session_id=self.memory_config.session_id,
                connection_string=f"sqlite:///{self.memory_config.db_path}"
            )
            return ConversationBufferMemory(
                memory_key="chat_history",
                chat_memory=message_history,
                return_messages=True
            )


# ===== 使用示例 =====

# 1. 无记忆 - 一次性任务
generator_simple = ReactAgentGenerator(
    memory_config=MemoryConfig.no_memory()
)

# 2. 内存记忆 - 中等复杂度任务
generator_balanced = ReactAgentGenerator(
    memory_config=MemoryConfig.balanced(
        session_id="feature_development"
    )
)

# 3. 持久记忆 - 长期项目
generator_pro = ReactAgentGenerator(
    memory_config=MemoryConfig.professional(
        session_id="project_123",
        db_path="./project_memories.db"
    )
)

# ===== 决策指南 =====

def select_memory_level(
    task_complexity: str,
    need_persistence: bool,
    expected_iterations: int
) -> MemoryConfig:
    """
    根据任务特征选择记忆级别
    
    Args:
        task_complexity: "simple" | "medium" | "complex"
        need_persistence: 是否需要持久化
        expected_iterations: 预期迭代次数
    
    Returns:
        推荐的记忆配置
    """
    # 简单任务或一次性生成
    if task_complexity == "simple" or expected_iterations <= 1:
        return MemoryConfig.no_memory()
    
    # 需要持久化或长期项目
    if need_persistence or expected_iterations > 20:
        return MemoryConfig.professional(
            session_id=f"task_{int(time.time())}"
        )
    
    # 默认使用平衡方案
    return MemoryConfig.balanced()


# ===== 用户友好的接口 =====

class MemoryMode:
    """用户友好的记忆模式"""
    
    FAST = MemoryConfig.no_memory()      # 快速模式
    SMART = MemoryConfig.balanced()       # 智能模式
    PRO = MemoryConfig.professional       # 专业模式（需要session_id）

# 使用方式
# generator = ReactAgentGenerator(memory_config=MemoryMode.SMART)