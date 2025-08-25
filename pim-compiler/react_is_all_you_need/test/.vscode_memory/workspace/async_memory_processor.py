#!/usr/bin/env python3
"""
异步记忆处理器 - 预计算多清晰度视图

设计理念：
- 每条消息预先生成多个清晰度级别的视图
- 使用时直接选择合适的视图，无需实时压缩
- 后台异步更新，不阻塞主流程
"""

import json
import hashlib
import asyncio
import threading
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

class ClarityLevel(Enum):
    """预定义的清晰度级别"""
    FULL = 1.0      # 完整视图
    HIGH = 0.7      # 高清晰度视图
    MEDIUM = 0.5    # 中等清晰度视图
    LOW = 0.3       # 低清晰度视图
    MINIMAL = 0.1   # 最小视图

@dataclass
class MessageView:
    """消息的某个清晰度视图"""
    clarity: ClarityLevel
    content: Dict
    tokens: int
    generated_at: datetime
    
class MultiViewMessage:
    """具有多个预计算视图的消息"""
    
    def __init__(self, original_message: Dict, message_id: str = None):
        """
        初始化多视图消息
        
        Args:
            original_message: 原始消息
            message_id: 消息ID（可选）
        """
        self.id = message_id or self._generate_id(original_message)
        self.original = original_message
        self.timestamp = datetime.now()
        self.views: Dict[ClarityLevel, MessageView] = {}
        self.metadata = {
            "role": original_message.get("role"),
            "round": None,  # 将在添加到历史时设置
            "importance": None  # 将在分析时设置
        }
    
    def _generate_id(self, message: Dict) -> str:
        """生成消息ID"""
        content = json.dumps(message, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def get_view(self, clarity: ClarityLevel) -> Optional[MessageView]:
        """获取指定清晰度的视图"""
        return self.views.get(clarity)
    
    def get_best_view(self, max_tokens: int) -> Optional[MessageView]:
        """获取不超过token限制的最佳视图"""
        # 从高到低尝试
        for clarity in [ClarityLevel.FULL, ClarityLevel.HIGH, 
                       ClarityLevel.MEDIUM, ClarityLevel.LOW, ClarityLevel.MINIMAL]:
            view = self.views.get(clarity)
            if view and view.tokens <= max_tokens:
                return view
        return self.views.get(ClarityLevel.MINIMAL)  # 返回最小视图

class AsyncMemoryProcessor:
    """异步记忆处理器"""
    
    def __init__(self, cache_dir: Optional[Path] = None, max_workers: int = 4):
        """
        初始化异步处理器
        
        Args:
            cache_dir: 缓存目录（用于持久化视图）
            max_workers: 最大工作线程数
        """
        self.cache_dir = cache_dir
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
            
        # 线程池执行器
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 消息存储
        self.messages: List[MultiViewMessage] = []
        self.message_index: Dict[str, MultiViewMessage] = {}
        
        # 预计算队列
        self.precompute_queue = asyncio.Queue() if asyncio.get_event_loop().is_running() else None
        
        # 视图生成策略
        self.view_generators = {
            ClarityLevel.FULL: self._generate_full_view,
            ClarityLevel.HIGH: self._generate_high_clarity_view,
            ClarityLevel.MEDIUM: self._generate_medium_clarity_view,
            ClarityLevel.LOW: self._generate_low_clarity_view,
            ClarityLevel.MINIMAL: self._generate_minimal_view
        }
    
    def add_message(self, message: Dict, importance: str = "MEDIUM") -> MultiViewMessage:
        """
        添加消息并触发异步预计算
        
        Args:
            message: 原始消息
            importance: 重要性级别
            
        Returns:
            多视图消息对象
        """
        # 创建多视图消息
        multi_view_msg = MultiViewMessage(message)
        multi_view_msg.metadata["importance"] = importance
        multi_view_msg.metadata["round"] = len(self.messages)
        
        # 添加到存储
        self.messages.append(multi_view_msg)
        self.message_index[multi_view_msg.id] = multi_view_msg
        
        # 立即生成FULL和MINIMAL视图（同步）
        multi_view_msg.views[ClarityLevel.FULL] = self._generate_full_view(message)
        multi_view_msg.views[ClarityLevel.MINIMAL] = self._generate_minimal_view(message)
        
        # 异步生成其他视图
        self.executor.submit(self._precompute_views_async, multi_view_msg)
        
        return multi_view_msg
    
    def _precompute_views_async(self, multi_view_msg: MultiViewMessage):
        """异步预计算所有视图"""
        try:
            # 生成中间清晰度的视图
            for clarity in [ClarityLevel.HIGH, ClarityLevel.MEDIUM, ClarityLevel.LOW]:
                if clarity not in multi_view_msg.views:
                    generator = self.view_generators[clarity]
                    view = generator(multi_view_msg.original)
                    multi_view_msg.views[clarity] = view
            
            # 如果有缓存目录，持久化视图
            if self.cache_dir:
                self._cache_views(multi_view_msg)
                
        except Exception as e:
            print(f"预计算视图失败: {e}")
    
    def _generate_full_view(self, message: Dict) -> MessageView:
        """生成完整视图"""
        return MessageView(
            clarity=ClarityLevel.FULL,
            content=message,
            tokens=self._estimate_tokens(json.dumps(message)),
            generated_at=datetime.now()
        )
    
    def _generate_high_clarity_view(self, message: Dict) -> MessageView:
        """生成高清晰度视图（70%）"""
        view_content = {"role": message.get("role")}
        
        if message.get("content"):
            content = message["content"]
            if len(content) > 1000:
                # 保留前600字符和后200字符
                view_content["content"] = content[:600] + "\n...[部分内容省略]...\n" + content[-200:]
            else:
                view_content["content"] = content
        
        # 工具调用保留主要信息
        if "tool_calls" in message:
            view_content["tool_calls_summary"] = [
                {"name": call["function"]["name"], 
                 "args_preview": str(call["function"].get("arguments", ""))[:50]}
                for call in message["tool_calls"]
            ]
        
        return MessageView(
            clarity=ClarityLevel.HIGH,
            content=view_content,
            tokens=self._estimate_tokens(json.dumps(view_content)),
            generated_at=datetime.now()
        )
    
    def _generate_medium_clarity_view(self, message: Dict) -> MessageView:
        """生成中等清晰度视图（50%）"""
        view_content = {"role": message.get("role")}
        
        if message.get("content"):
            content = message["content"]
            # 只保留前300字符
            view_content["content_preview"] = content[:300] + ("..." if len(content) > 300 else "")
        
        # 工具调用只保留名称
        if "tool_calls" in message:
            view_content["tools_used"] = [
                call["function"]["name"] for call in message["tool_calls"]
            ]
        
        return MessageView(
            clarity=ClarityLevel.MEDIUM,
            content=view_content,
            tokens=self._estimate_tokens(json.dumps(view_content)),
            generated_at=datetime.now()
        )
    
    def _generate_low_clarity_view(self, message: Dict) -> MessageView:
        """生成低清晰度视图（30%）"""
        # 生成一句话摘要
        summary = self._generate_summary(message)
        
        view_content = {
            "role": message.get("role"),
            "summary": summary
        }
        
        return MessageView(
            clarity=ClarityLevel.LOW,
            content=view_content,
            tokens=self._estimate_tokens(json.dumps(view_content)),
            generated_at=datetime.now()
        )
    
    def _generate_minimal_view(self, message: Dict) -> MessageView:
        """生成最小视图（10%）"""
        # 极简标记
        role = message.get("role", "")
        
        if role == "assistant" and "tool_calls" in message:
            marker = f"[{role}:tools]"
        elif role == "tool":
            marker = f"[{role}:result]"
        else:
            marker = f"[{role}]"
        
        view_content = {"marker": marker}
        
        return MessageView(
            clarity=ClarityLevel.MINIMAL,
            content=view_content,
            tokens=5,  # 固定的极小token数
            generated_at=datetime.now()
        )
    
    def _generate_summary(self, message: Dict) -> str:
        """生成消息摘要"""
        role = message.get("role", "")
        
        if role == "assistant" and "tool_calls" in message:
            tools = [call["function"]["name"] for call in message["tool_calls"]]
            return f"调用了{len(tools)}个工具: {', '.join(tools[:3])}"
        
        elif role == "tool":
            content = message.get("content", "")
            if "error" in content.lower():
                return "工具执行出错"
            elif "success" in content.lower() or "成功" in content:
                return "工具执行成功"
            else:
                return "工具返回结果"
        
        elif message.get("content"):
            content = message["content"]
            return content[:100] + ("..." if len(content) > 100 else "")
        
        return f"{role}消息"
    
    def _estimate_tokens(self, text: str) -> int:
        """估算token数"""
        return len(text) // 4
    
    def _cache_views(self, multi_view_msg: MultiViewMessage):
        """缓存视图到磁盘"""
        if not self.cache_dir:
            return
        
        cache_file = self.cache_dir / f"{multi_view_msg.id}.json"
        cache_data = {
            "id": multi_view_msg.id,
            "timestamp": multi_view_msg.timestamp.isoformat(),
            "metadata": multi_view_msg.metadata,
            "views": {
                clarity.name: {
                    "content": view.content,
                    "tokens": view.tokens,
                    "generated_at": view.generated_at.isoformat()
                }
                for clarity, view in multi_view_msg.views.items()
            }
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def load_cached_views(self, message_id: str) -> Optional[MultiViewMessage]:
        """从缓存加载视图"""
        if not self.cache_dir:
            return None
        
        cache_file = self.cache_dir / f"{message_id}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 重建MultiViewMessage
            # 这里简化处理，实际需要完整恢复
            return None  # TODO: 实现缓存恢复
            
        except Exception as e:
            print(f"加载缓存失败: {e}")
            return None
    
    def get_optimized_history(self, 
                             max_tokens: int = 200000,
                             time_decay: bool = True) -> List[Dict]:
        """
        获取优化后的历史消息
        
        Args:
            max_tokens: 最大token限制
            time_decay: 是否应用时间衰减
            
        Returns:
            优化后的消息列表
        """
        optimized = []
        used_tokens = 0
        
        # 从最新到最旧遍历
        for i, multi_msg in enumerate(reversed(self.messages)):
            # 计算该消息的目标清晰度
            if time_decay:
                # 根据距离计算清晰度
                distance = i
                if distance < 10:
                    target_clarity = ClarityLevel.FULL
                elif distance < 50:
                    target_clarity = ClarityLevel.HIGH
                elif distance < 100:
                    target_clarity = ClarityLevel.MEDIUM
                elif distance < 200:
                    target_clarity = ClarityLevel.LOW
                else:
                    target_clarity = ClarityLevel.MINIMAL
            else:
                target_clarity = ClarityLevel.FULL
            
            # 获取合适的视图
            view = multi_msg.get_view(target_clarity)
            if not view:
                # 如果目标视图还未生成，降级到可用视图
                view = multi_msg.get_best_view(max_tokens - used_tokens)
            
            if view and used_tokens + view.tokens <= max_tokens:
                optimized.insert(0, view.content)  # 插入到开头保持时间顺序
                used_tokens += view.tokens
            elif view:
                # 尝试使用更小的视图
                minimal_view = multi_msg.get_view(ClarityLevel.MINIMAL)
                if minimal_view and used_tokens + minimal_view.tokens <= max_tokens:
                    optimized.insert(0, minimal_view.content)
                    used_tokens += minimal_view.tokens
                else:
                    break  # 无法再添加更多消息
        
        return optimized
    
    def get_statistics(self) -> Dict:
        """获取处理统计"""
        total_views = 0
        completed_views = 0
        
        for msg in self.messages:
            total_views += len(ClarityLevel)
            completed_views += len(msg.views)
        
        return {
            "total_messages": len(self.messages),
            "total_views": total_views,
            "completed_views": completed_views,
            "completion_rate": completed_views / total_views if total_views > 0 else 0,
            "cache_enabled": self.cache_dir is not None
        }
    
    def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=True)
        
        # 清理过期缓存
        if self.cache_dir:
            # TODO: 实现缓存过期策略
            pass