#!/usr/bin/env python3
"""
统一的记忆管理器
自动配置和管理状态记忆与过程记忆
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

from .vscode_memory import VSCodeMemory, Resolution
from .vscode_memory_async import AsyncVSCodeMemory
from .process_memory import ProcessMemory, MessageImportance
from .async_memory_processor import AsyncMemoryProcessor, ClarityLevel

class MemoryMode(Enum):
    """记忆模式"""
    DISABLED = "disabled"           # 禁用记忆
    BASIC = "basic"                 # 基础模式（传统压缩）
    HYBRID = "hybrid"               # 混合模式（部分预计算）
    FULL_ASYNC = "full_async"       # 完整异步（全部预计算）
    AUTO = "auto"                   # 自动选择

class MemoryManager:
    """统一的记忆管理器"""
    
    def __init__(self,
                 work_dir: str,
                 mode: MemoryMode = MemoryMode.AUTO,
                 max_context_tokens: int = 262144,
                 enable_cache: bool = True):
        """
        初始化记忆管理器
        
        Args:
            work_dir: 工作目录
            mode: 记忆模式
            max_context_tokens: 最大上下文tokens
            enable_cache: 是否启用缓存
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_context_tokens = max_context_tokens
        self.enable_cache = enable_cache
        
        # 根据模式自动配置
        if mode == MemoryMode.AUTO:
            self.mode = self._auto_select_mode()
        else:
            self.mode = mode
        
        # 初始化记忆组件
        self._initialize_components()
        
        # 显示配置信息
        self._show_configuration()
    
    def _auto_select_mode(self) -> MemoryMode:
        """自动选择最佳记忆模式"""
        # 检查系统资源
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        
        # 检查上下文大小
        if self.max_context_tokens >= 200000:
            # 大上下文，需要高性能
            if cpu_count >= 4:
                return MemoryMode.FULL_ASYNC
            else:
                return MemoryMode.HYBRID
        elif self.max_context_tokens >= 50000:
            # 中等上下文
            return MemoryMode.HYBRID
        else:
            # 小上下文
            return MemoryMode.BASIC
    
    def _initialize_components(self):
        """初始化记忆组件"""
        self.state_memory = None
        self.process_memory = None
        self.async_processor = None
        
        if self.mode == MemoryMode.DISABLED:
            return
        
        # 状态记忆配置
        if self.mode == MemoryMode.FULL_ASYNC:
            # 完整异步模式
            self.state_memory = AsyncVSCodeMemory(
                self.work_dir,
                max_context_tokens=self.max_context_tokens
            )
            self.async_processor = AsyncMemoryProcessor(
                cache_dir=self.work_dir / ".message_views",
                max_workers=4
            )
        
        elif self.mode == MemoryMode.HYBRID:
            # 混合模式 - 过程记忆用异步，状态记忆用传统
            self.state_memory = VSCodeMemory(
                self.work_dir,
                max_context_tokens=self.max_context_tokens
            )
            self.async_processor = AsyncMemoryProcessor(
                cache_dir=self.work_dir / ".message_views",
                max_workers=2
            )
        
        elif self.mode == MemoryMode.BASIC:
            # 基础模式 - 全部用传统压缩
            self.state_memory = VSCodeMemory(
                self.work_dir,
                max_context_tokens=self.max_context_tokens
            )
            self.process_memory = ProcessMemory(
                max_context_tokens=self.max_context_tokens
            )
    
    def _show_configuration(self):
        """显示配置信息"""
        if self.mode == MemoryMode.DISABLED:
            print("ℹ️ 记忆系统已禁用")
            return
        
        mode_names = {
            MemoryMode.BASIC: "基础模式",
            MemoryMode.HYBRID: "混合模式",
            MemoryMode.FULL_ASYNC: "完整异步模式"
        }
        
        icons = {
            MemoryMode.BASIC: "✅",
            MemoryMode.HYBRID: "⚡",
            MemoryMode.FULL_ASYNC: "🚀"
        }
        
        print(f"{icons[self.mode]} 记忆系统已启用 - {mode_names[self.mode]}")
        
        # 显示详细配置
        if self.state_memory:
            state_type = "异步VSCode" if isinstance(self.state_memory, AsyncVSCodeMemory) else "VSCode"
            print(f"  - 状态记忆: {state_type}（潜意识/显意识）")
        
        if self.async_processor:
            print(f"  - 过程记忆: 异步多视图（5级清晰度）")
        elif self.process_memory:
            print(f"  - 过程记忆: 时间衰减压缩")
        
        if self.enable_cache and self.async_processor:
            print(f"  - 视图缓存: {self.work_dir}/.message_views")
        
        print(f"  - 上下文限制: {self.max_context_tokens:,} tokens")
    
    # ========== 状态记忆接口 ==========
    
    def open_file(self, file_path: str, content: str):
        """打开文件到记忆"""
        if self.state_memory:
            self.state_memory.open_file(file_path, content)
    
    def close_file(self, file_path: str):
        """关闭文件"""
        if self.state_memory:
            self.state_memory.close_file(file_path)
    
    def search(self, query: str) -> List[Dict]:
        """搜索记忆"""
        if self.state_memory:
            return self.state_memory.search(query)
        return []
    
    def save_episode(self, event: str, data: Dict):
        """保存事件"""
        if self.state_memory:
            self.state_memory.save_episode(event, data)
    
    def save_state(self, state_name: str, state_data: Dict):
        """保存状态快照"""
        if self.state_memory:
            self.state_memory.save_state(state_name, state_data)
    
    # ========== 过程记忆接口 ==========
    
    def add_message(self, message: Dict, importance: Optional[str] = None):
        """添加消息到过程记忆"""
        if self.async_processor:
            # 使用异步处理器
            return self.async_processor.add_message(message, importance)
        # ProcessMemory不存储消息，只在压缩时处理
    
    def compress_messages(self, messages: List[Dict]) -> Tuple[List[Dict], Dict]:
        """压缩消息历史"""
        if self.async_processor:
            # 使用异步处理器的优化历史
            optimized = self.async_processor.get_optimized_history(
                max_tokens=int(self.max_context_tokens * 0.8),
                time_decay=True
            )
            stats = self.async_processor.get_statistics()
            return optimized, {
                "original_count": len(messages),
                "compressed_count": len(optimized),
                "compression_ratio": 1 - len(optimized) / max(len(messages), 1)
            }
        elif self.process_memory:
            # 使用传统压缩
            return self.process_memory.compress_messages(messages)
        else:
            # 无压缩
            return messages, {"original_count": len(messages), "compressed_count": len(messages)}
    
    # ========== 统一接口 ==========
    
    def get_memory_context(self, extra_tokens: int = 0) -> str:
        """获取记忆上下文（用于系统提示词）"""
        if not self.state_memory:
            return ""
        
        # 根据记忆类型选择压缩方法
        if isinstance(self.state_memory, AsyncVSCodeMemory):
            # 使用优化压缩
            return self.state_memory.compress_for_llm_optimized(
                extra_tokens=extra_tokens,
                target_resolution={
                    "detail_view": Resolution.FULL,
                    "working_set": Resolution.PREVIEW,
                    "resource_outline": Resolution.OUTLINE,
                    "action_history": Resolution.PREVIEW,
                    "findings": Resolution.PREVIEW,
                    "overview": Resolution.FULL
                }
            )
        else:
            # 使用传统压缩
            return self.state_memory.compress_for_llm(extra_tokens=extra_tokens)
    
    def optimize_message_history(self, messages: List[Dict], protected_count: int = 2) -> List[Dict]:
        """优化消息历史"""
        if len(messages) <= protected_count:
            return messages
        
        # 保护前N条消息
        protected = messages[:protected_count]
        optimizable = messages[protected_count:]
        
        # 优化可优化部分
        if self.async_processor:
            # 确保消息都在处理器中
            for msg in optimizable:
                if msg not in self.async_processor.messages:
                    self.async_processor.add_message(msg)
            
            # 获取优化历史
            optimized = self.async_processor.get_optimized_history(
                max_tokens=int(self.max_context_tokens * 0.7),
                time_decay=True
            )
        else:
            # 使用传统压缩或不压缩
            optimized = optimizable
        
        # 重组消息
        result = protected + optimized
        
        # 插入当前状态记忆
        memory_context = self.get_memory_context(10000)
        if memory_context:
            result.insert(protected_count, {
                "role": "system",
                "content": f"[当前状态记忆]\n{memory_context}"
            })
        
        return result
    
    def should_optimize(self, round_num: int, message_count: int) -> bool:
        """判断是否需要优化"""
        if self.mode == MemoryMode.DISABLED:
            return False
        
        # 根据模式调整优化频率
        if self.mode == MemoryMode.FULL_ASYNC:
            # 异步模式效率高，可以降低频率
            return round_num % 50 == 0 and round_num > 0
        elif self.mode == MemoryMode.HYBRID:
            # 混合模式
            return round_num % 30 == 0 and round_num > 0
        else:
            # 基础模式，需要更频繁
            return round_num % 20 == 0 and round_num > 0
    
    def get_status(self) -> Dict:
        """获取记忆系统状态"""
        status = {
            "mode": self.mode.value,
            "enabled": self.mode != MemoryMode.DISABLED
        }
        
        if self.state_memory:
            session = self.state_memory.export_session()
            status["state_memory"] = {
                "type": type(self.state_memory).__name__,
                "working_set": len(self.state_memory.consciousness.get("working_set", [])),
                "current_focus": self.state_memory.attention.get("focus"),
                "episodes": len(self.state_memory.index.get("episodes", [])),
                "states": len(self.state_memory.index.get("states", []))
            }
        
        if self.async_processor:
            stats = self.async_processor.get_statistics()
            status["async_processor"] = {
                "enabled": True,
                "messages": stats["total_messages"],
                "views_generated": stats["completed_views"],
                "completion_rate": f"{stats['completion_rate']:.1%}",
                "cache_enabled": stats["cache_enabled"]
            }
        elif self.process_memory:
            status["process_memory"] = {
                "enabled": True,
                "messages": len(getattr(self.process_memory, 'messages', []))
            }
        
        return status
    
    def cleanup(self):
        """清理资源"""
        if self.async_processor:
            self.async_processor.cleanup()
        
        if self.state_memory:
            if isinstance(self.state_memory, AsyncVSCodeMemory):
                self.state_memory.cleanup()
            else:
                self.state_memory.garbage_collect()