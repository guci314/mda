#!/usr/bin/env python3
"""
Simple Memory Manager - 纯滑动窗口实现
只负责消息缓冲，不做任何认知处理
"""

from collections import deque
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    """消息结构"""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: str = None
    tool_calls: Optional[List[Dict]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于API调用）"""
        result = {
            "role": self.role,
            "content": self.content
        }
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result


class SimpleMemoryManager:
    """
    简化版内存管理器 - 纯滑动窗口
    
    设计原则：
    1. 只做消息缓冲，不做智能处理
    2. 固定窗口大小，自动丢弃旧消息
    3. 提供原始消息流给认知系统
    4. 保持API兼容性
    """
    
    def __init__(self, window_size: int = 50, system_prompt: Optional[str] = None):
        """
        初始化滑动窗口
        
        Args:
            window_size: 窗口大小（保留的消息数）
            system_prompt: 系统提示（始终保留在上下文开头）
        """
        self.window_size = window_size
        self.system_prompt = system_prompt
        
        # 使用deque实现高效的滑动窗口
        self.messages = deque(maxlen=window_size)
        
        # 统计信息
        self.total_messages = 0
        self.dropped_messages = 0
        
    def add_message(self, role: str, content: str, 
                   tool_calls: Optional[List[Dict]] = None) -> None:
        """
        添加消息到窗口
        
        Args:
            role: 消息角色
            content: 消息内容
            tool_calls: 工具调用信息（可选）
        """
        message = Message(role=role, content=content, tool_calls=tool_calls)
        
        # 检查是否会丢弃消息
        if len(self.messages) == self.window_size:
            self.dropped_messages += 1
            
        self.messages.append(message)
        self.total_messages += 1
    
    def get_context(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """
        获取当前上下文（用于LLM调用）
        
        Args:
            include_system: 是否包含系统提示
            
        Returns:
            消息列表（字典格式）
        """
        context = []
        
        # 添加系统提示（如果有）
        if include_system and self.system_prompt:
            context.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # 添加窗口中的消息
        for message in self.messages:
            context.append(message.to_dict())
            
        return context
    
    def get_messages(self) -> List[Message]:
        """
        获取原始消息对象（供认知系统分析）
        
        Returns:
            Message对象列表
        """
        return list(self.messages)
    
    def get_recent_messages(self, n: int) -> List[Message]:
        """
        获取最近n条消息
        
        Args:
            n: 消息数量
            
        Returns:
            最近的Message对象列表
        """
        if n >= len(self.messages):
            return list(self.messages)
        return list(self.messages)[-n:]
    
    def clear(self) -> None:
        """清空消息窗口"""
        self.messages.clear()
        self.dropped_messages = 0
        
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "window_size": self.window_size,
            "current_messages": len(self.messages),
            "total_messages": self.total_messages,
            "dropped_messages": self.dropped_messages,
            "drop_rate": self.dropped_messages / max(1, self.total_messages)
        }
    
    def get_message_summary(self) -> Dict[str, int]:
        """
        获取消息类型统计
        
        Returns:
            各类型消息的数量
        """
        summary = {"user": 0, "assistant": 0, "system": 0, "tool": 0}
        for message in self.messages:
            if message.role in summary:
                summary[message.role] += 1
        return summary
    
    def find_last_user_message(self) -> Optional[Message]:
        """
        找到最后一条用户消息
        
        Returns:
            最后的用户消息，如果没有则返回None
        """
        for message in reversed(self.messages):
            if message.role == "user":
                return message
        return None
    
    def find_last_assistant_message(self) -> Optional[Message]:
        """
        找到最后一条助手消息
        
        Returns:
            最后的助手消息，如果没有则返回None
        """
        for message in reversed(self.messages):
            if message.role == "assistant":
                return message
        return None
    
    def estimate_tokens(self) -> int:
        """
        估算当前上下文的token数
        
        Returns:
            估算的token数（粗略计算：字符数/4）
        """
        total_chars = 0
        if self.system_prompt:
            total_chars += len(self.system_prompt)
        
        for message in self.messages:
            total_chars += len(message.content)
            if message.tool_calls:
                total_chars += len(str(message.tool_calls))
                
        # 粗略估算：平均4个字符一个token
        return total_chars // 4
    
    def is_near_limit(self, threshold: float = 0.9) -> bool:
        """
        检查是否接近窗口限制
        
        Args:
            threshold: 阈值（0-1）
            
        Returns:
            是否接近限制
        """
        return len(self.messages) >= self.window_size * threshold
    
    def __len__(self) -> int:
        """返回当前消息数量"""
        return len(self.messages)
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (f"SimpleMemoryManager(window={self.window_size}, "
                f"messages={len(self.messages)}, "
                f"dropped={self.dropped_messages})")


# 兼容性适配器（保持与旧MemoryManager的接口兼容）
class MemoryManagerAdapter(SimpleMemoryManager):
    """
    适配器类，提供与旧MemoryManager兼容的接口
    将认知功能委托给NLPLMemorySystem
    """
    
    def __init__(self, work_dir: str = ".", mode: str = "BASIC", 
                 max_context_tokens: int = 100000, **kwargs):
        """兼容旧接口的初始化"""
        # 根据token限制计算窗口大小（假设平均每条消息500 tokens）
        window_size = max_context_tokens // 500
        super().__init__(window_size=window_size)
        
        # 保存参数（供需要的地方使用）
        self.work_dir = work_dir
        self.mode = mode
        self.max_context_tokens = max_context_tokens
        
    def add(self, message: Dict[str, Any]) -> None:
        """兼容旧的add方法"""
        self.add_message(
            role=message.get("role", "user"),
            content=message.get("content", ""),
            tool_calls=message.get("tool_calls")
        )
    
    def add_message(self, role_or_message, content=None, **kwargs):
        """
        重写add_message以兼容两种调用方式：
        1. add_message(role, content) - 原始方式
        2. add_message(message_dict) - 字典方式
        """
        if isinstance(role_or_message, dict):
            # 字典方式调用
            message = role_or_message
            super().add_message(
                role=message.get("role", "user"),
                content=message.get("content", ""),
                tool_calls=message.get("tool_calls")
            )
        else:
            # 原始方式调用
            super().add_message(role_or_message, content, **kwargs)
    
    def get_memory_context(self, extra_tokens: int = 0) -> str:
        """兼容旧的get_memory_context方法"""
        # 返回简单的统计信息（认知功能已转移到NLPLMemorySystem）
        stats = self.get_stats()
        return f"消息窗口：{stats['current_messages']}/{stats['window_size']}"
    
    def optimize_message_history(self, messages: List[Dict]) -> List[Dict]:
        """兼容旧的optimize方法 - 现在只做简单裁剪"""
        # 如果消息太多，只保留最近的
        if len(messages) > self.window_size:
            return messages[-self.window_size:]
        return messages
    
    def search(self, query: str) -> List[Dict]:
        """兼容旧的search方法 - 委托给NLPLMemorySystem"""
        # 这个功能应该由NLPLMemorySystem处理
        # 这里只返回空列表表示不支持
        return []
    
    def save_episode(self, event: str, data: Dict) -> None:
        """兼容旧的save_episode方法 - 委托给NLPLMemorySystem"""
        # 这个功能应该由NLPLMemorySystem处理
        pass
    
    def save_state(self, state_name: str, state_data: Dict) -> None:
        """兼容旧的save_state方法 - 委托给NLPLMemorySystem"""
        # 这个功能应该由NLPLMemorySystem处理
        pass
    
    def open_file(self, file_path: str, content: str) -> None:
        """兼容旧的open_file方法 - 委托给NLPLMemorySystem"""
        # 这个功能应该由NLPLMemorySystem处理
        pass
    
    def should_optimize(self, round_num: int, message_count: int) -> bool:
        """兼容旧的should_optimize方法"""
        # 简单策略：接近窗口限制时返回True
        return self.is_near_limit(0.9)
    
    def cleanup(self) -> None:
        """兼容旧的cleanup方法"""
        self.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """兼容旧的get_status方法"""
        return self.get_stats()


# 使用示例
if __name__ == "__main__":
    # 创建简单内存管理器
    memory = SimpleMemoryManager(window_size=10)
    
    # 添加一些消息
    memory.add_message("user", "创建一个计算器")
    memory.add_message("assistant", "我来创建计算器模块")
    memory.add_message("tool", "文件创建成功")
    
    # 获取上下文
    context = memory.get_context()
    print(f"当前上下文：{len(context)}条消息")
    
    # 获取统计
    stats = memory.get_stats()
    print(f"统计信息：{stats}")
    
    # 测试滑动窗口
    for i in range(20):
        memory.add_message("user", f"消息{i}")
    
    print(f"添加20条消息后：{memory}")
    print(f"丢弃的消息数：{memory.dropped_messages}")