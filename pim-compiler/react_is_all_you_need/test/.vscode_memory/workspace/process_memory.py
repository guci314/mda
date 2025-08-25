#!/usr/bin/env python3
"""
过程记忆管理 - 基于时间衰减的消息压缩

设计理念：
- 时间越久的记忆，清晰度越低
- 重要事件保持更高清晰度
- 自动压缩和衰减
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import hashlib

class MessageImportance(Enum):
    """消息重要性级别"""
    CRITICAL = 5    # 关键决策、错误修复
    HIGH = 4        # 重要工具调用、文件创建
    MEDIUM = 3      # 常规工具调用
    LOW = 2         # 查询、读取操作
    TRIVIAL = 1     # 思考过程、中间步骤

class TimeResolution(Enum):
    """时间分辨率 - 距离现在越远，分辨率越低"""
    IMMEDIATE = 5   # 最近10轮 - 完整保留
    RECENT = 4      # 最近50轮 - 轻度压缩
    NEAR = 3        # 最近100轮 - 中度压缩
    FAR = 2         # 最近200轮 - 重度压缩
    DISTANT = 1     # 200轮以前 - 仅保留摘要

class ProcessMemory:
    """过程记忆管理器"""
    
    def __init__(self, max_context_tokens: int = 262144):
        """
        初始化过程记忆
        
        Args:
            max_context_tokens: 最大上下文tokens
        """
        self.max_tokens = max_context_tokens
        
        # 时间衰减配置
        self.time_thresholds = {
            TimeResolution.IMMEDIATE: 10,    # 最近10轮
            TimeResolution.RECENT: 50,       # 最近50轮
            TimeResolution.NEAR: 100,        # 最近100轮
            TimeResolution.FAR: 200,         # 最近200轮
            TimeResolution.DISTANT: float('inf')  # 更早
        }
        
        # 分辨率对应的信息清晰度
        self.clarity_levels = {
            TimeResolution.IMMEDIATE: 1.0,    # 100%清晰度
            TimeResolution.RECENT: 0.7,       # 70%清晰度
            TimeResolution.NEAR: 0.4,         # 40%清晰度
            TimeResolution.FAR: 0.2,          # 20%清晰度
            TimeResolution.DISTANT: 0.05      # 5%清晰度（仅摘要）
        }
        
        # 重要性对清晰度的调整系数
        self.importance_modifiers = {
            MessageImportance.CRITICAL: 2.0,   # 双倍清晰度
            MessageImportance.HIGH: 1.5,       # 1.5倍清晰度
            MessageImportance.MEDIUM: 1.0,     # 标准清晰度
            MessageImportance.LOW: 0.7,        # 降低清晰度
            MessageImportance.TRIVIAL: 0.3     # 最低清晰度
        }
        
        # 压缩历史
        self.compression_history = []
    
    def classify_message_importance(self, message: Dict) -> MessageImportance:
        """
        判断消息重要性
        
        Args:
            message: 消息字典
            
        Returns:
            重要性级别
        """
        role = message.get("role", "")
        content = message.get("content", "")
        
        # 工具调用的重要性分析
        if role == "assistant" and "tool_calls" in message:
            tool_calls = message["tool_calls"]
            for call in tool_calls:
                tool_name = call["function"]["name"]
                
                # 关键操作
                if tool_name in ["write_file", "execute_python", "execute_command"]:
                    return MessageImportance.HIGH
                
                # 读取操作
                elif tool_name in ["read_file", "list_directory"]:
                    return MessageImportance.LOW
                
                # 文件追加
                elif tool_name == "append_file":
                    return MessageImportance.MEDIUM
        
        # 工具结果的重要性
        elif role == "tool":
            # 错误结果更重要
            if "错误" in content or "error" in content.lower() or "失败" in content:
                return MessageImportance.CRITICAL
            
            # 成功的写入操作
            elif "成功" in content and ("写入" in content or "创建" in content):
                return MessageImportance.HIGH
            
            # 普通结果
            else:
                return MessageImportance.MEDIUM
        
        # 用户消息
        elif role == "user":
            # 任务描述通常很重要
            if len(content) > 200:  # 长任务描述
                return MessageImportance.HIGH
            else:
                return MessageImportance.MEDIUM
        
        # 系统消息
        elif role == "system":
            return MessageImportance.HIGH
        
        # 助手思考过程
        else:
            if len(content) < 100:
                return MessageImportance.TRIVIAL
            else:
                return MessageImportance.LOW
    
    def get_time_resolution(self, round_index: int, current_round: int) -> TimeResolution:
        """
        根据时间距离确定分辨率
        
        Args:
            round_index: 消息所在轮次
            current_round: 当前轮次
            
        Returns:
            时间分辨率级别
        """
        distance = current_round - round_index
        
        for resolution in TimeResolution:
            if distance <= self.time_thresholds[resolution]:
                return resolution
        
        return TimeResolution.DISTANT
    
    def compress_message(self, 
                        message: Dict, 
                        importance: MessageImportance,
                        resolution: TimeResolution) -> Optional[Dict]:
        """
        根据信息清晰度压缩消息
        
        Args:
            message: 原始消息
            importance: 重要性级别
            resolution: 时间分辨率
            
        Returns:
            压缩后的消息或None（完全模糊）
        """
        # 计算信息清晰度
        base_clarity = self.clarity_levels[resolution]
        importance_modifier = self.importance_modifiers[importance]
        info_clarity = min(1.0, base_clarity * importance_modifier)
        
        # 系统消息和初始用户消息始终保持完全清晰
        if message.get("role") == "system" or \
           (message.get("role") == "user" and message.get("is_initial")):
            return message
        
        # 根据信息清晰度决定呈现方式
        if info_clarity >= 0.9:
            # 高清晰度 - 完整信息
            return message
        
        elif info_clarity >= 0.5:
            # 中等清晰度 - 保留关键信息，模糊细节
            compressed = {"role": message["role"]}
            
            if message.get("content"):
                content = message["content"]
                # 保留核心内容，模糊边缘细节
                if len(content) > 500:
                    compressed["content"] = content[:200] + "\n...[细节已模糊]...\n" + content[-100:]
                else:
                    compressed["content"] = content
            
            # 工具调用只保留概要
            if "tool_calls" in message:
                compressed["tool_summary"] = f"调用了{len(message['tool_calls'])}个工具"
            
            return compressed
        
        elif info_clarity >= 0.2:
            # 低清晰度 - 仅保留要点
            return {
                "role": message["role"],
                "summary": self._generate_summary(message)
            }
        
        elif info_clarity >= 0.05:
            # 极低清晰度 - 单行印象
            if importance.value >= MessageImportance.HIGH.value:
                return {
                    "role": "summary",
                    "content": f"[{message['role']}] {self._generate_oneline_summary(message)}"
                }
        
        # 完全模糊 - 遗忘
        return None
    
    def _generate_summary(self, message: Dict) -> str:
        """生成消息摘要"""
        role = message.get("role", "")
        
        if role == "assistant" and "tool_calls" in message:
            tools = [call["function"]["name"] for call in message["tool_calls"]]
            return f"调用工具: {', '.join(tools)}"
        
        elif role == "tool":
            content = message.get("content", "")[:100]
            return f"工具结果: {content}..."
        
        elif message.get("content"):
            content = message["content"]
            if len(content) > 100:
                return content[:100] + "..."
            return content
        
        return "[空消息]"
    
    def _generate_oneline_summary(self, message: Dict) -> str:
        """生成单行摘要"""
        summary = self._generate_summary(message)
        # 去除换行，限制长度
        return summary.replace('\n', ' ')[:50]
    
    def compress_messages(self, messages: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        压缩消息列表
        
        Args:
            messages: 原始消息列表
            
        Returns:
            (压缩后的消息列表, 压缩统计)
        """
        if not messages:
            return [], {}
        
        compressed = []
        stats = {
            "original_count": len(messages),
            "compressed_count": 0,
            "dropped_count": 0,
            "original_tokens": 0,
            "compressed_tokens": 0,
            "compression_ratio": 0
        }
        
        # 识别轮次
        current_round = sum(1 for msg in messages if msg.get("role") == "assistant")
        
        # 处理每条消息
        for i, message in enumerate(messages):
            # 估算轮次
            round_index = sum(1 for msg in messages[:i] if msg.get("role") == "assistant")
            
            # 判断重要性和分辨率
            importance = self.classify_message_importance(message)
            resolution = self.get_time_resolution(round_index, current_round)
            
            # 压缩消息
            compressed_msg = self.compress_message(message, importance, resolution)
            
            if compressed_msg:
                compressed.append(compressed_msg)
                stats["compressed_count"] += 1
            else:
                stats["dropped_count"] += 1
            
            # 统计tokens（简化估算）
            if message.get("content"):
                stats["original_tokens"] += len(message["content"]) // 4
            if compressed_msg and compressed_msg.get("content"):
                stats["compressed_tokens"] += len(compressed_msg["content"]) // 4
        
        # 计算压缩率
        if stats["original_tokens"] > 0:
            stats["compression_ratio"] = 1 - (stats["compressed_tokens"] / stats["original_tokens"])
        
        # 记录压缩历史
        self.compression_history.append({
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        })
        
        return compressed, stats
    
    def batch_compress_by_time(self, messages: List[Dict]) -> List[Dict]:
        """
        批量压缩历史消息 - 按时间段分组压缩
        
        Args:
            messages: 原始消息列表
            
        Returns:
            压缩后的消息列表
        """
        if len(messages) < 20:  # 消息太少不压缩
            return messages
        
        result = []
        current_round = sum(1 for msg in messages if msg.get("role") == "assistant")
        
        # 分段处理
        segments = {
            TimeResolution.IMMEDIATE: [],
            TimeResolution.RECENT: [],
            TimeResolution.NEAR: [],
            TimeResolution.FAR: [],
            TimeResolution.DISTANT: []
        }
        
        # 将消息分配到不同时间段
        for i, message in enumerate(messages):
            round_index = sum(1 for msg in messages[:i] if msg.get("role") == "assistant")
            resolution = self.get_time_resolution(round_index, current_round)
            segments[resolution].append((i, message))
        
        # 分段压缩
        for resolution, segment_messages in segments.items():
            if not segment_messages:
                continue
            
            if resolution == TimeResolution.IMMEDIATE:
                # 最近的消息完整保留
                result.extend([msg for _, msg in segment_messages])
            
            elif resolution == TimeResolution.DISTANT:
                # 最远的消息合并为摘要
                if len(segment_messages) > 5:
                    summary = self._merge_distant_messages(segment_messages)
                    if summary:
                        result.append(summary)
                else:
                    for _, msg in segment_messages:
                        importance = self.classify_message_importance(msg)
                        compressed = self.compress_message(msg, importance, resolution)
                        if compressed:
                            result.append(compressed)
            
            else:
                # 中间段落正常压缩
                for _, msg in segment_messages:
                    importance = self.classify_message_importance(msg)
                    compressed = self.compress_message(msg, importance, resolution)
                    if compressed:
                        result.append(compressed)
        
        return result
    
    def _merge_distant_messages(self, messages: List[Tuple[int, Dict]]) -> Optional[Dict]:
        """
        合并远期消息为单个摘要
        
        Args:
            messages: (索引, 消息)列表
            
        Returns:
            合并后的摘要消息
        """
        if not messages:
            return None
        
        # 统计信息
        tool_calls = []
        important_results = []
        errors = []
        
        for _, msg in messages:
            if msg.get("role") == "assistant" and "tool_calls" in msg:
                for call in msg["tool_calls"]:
                    tool_calls.append(call["function"]["name"])
            
            elif msg.get("role") == "tool":
                content = msg.get("content", "")
                if "错误" in content or "error" in content.lower():
                    errors.append(content[:50])
                elif "成功" in content and "写入" in content:
                    important_results.append(content[:50])
        
        # 生成摘要
        summary_parts = []
        
        if tool_calls:
            tool_summary = {}
            for tool in tool_calls:
                tool_summary[tool] = tool_summary.get(tool, 0) + 1
            summary_parts.append(f"工具调用: {', '.join(f'{k}({v}次)' for k, v in tool_summary.items())}")
        
        if important_results:
            summary_parts.append(f"重要操作: {len(important_results)}个文件操作")
        
        if errors:
            summary_parts.append(f"错误记录: {len(errors)}个错误")
        
        if summary_parts:
            return {
                "role": "system",
                "content": f"[历史摘要 - {len(messages)}条消息]\n" + "\n".join(summary_parts)
            }
        
        return None
    
    def adaptive_compress(self, 
                         messages: List[Dict], 
                         target_tokens: int = 200000) -> List[Dict]:
        """
        自适应压缩 - 根据目标token数动态调整压缩强度
        
        Args:
            messages: 原始消息列表
            target_tokens: 目标token数
            
        Returns:
            压缩后的消息列表
        """
        # 先尝试标准压缩
        compressed = self.batch_compress_by_time(messages)
        
        # 估算tokens
        estimated_tokens = sum(
            len(msg.get("content", msg.get("summary", ""))) // 4 
            for msg in compressed
        )
        
        # 如果还是太大，增加压缩强度
        if estimated_tokens > target_tokens:
            # 调整分辨率阈值，更激进地压缩
            self.time_thresholds[TimeResolution.IMMEDIATE] = 5
            self.time_thresholds[TimeResolution.RECENT] = 20
            self.time_thresholds[TimeResolution.NEAR] = 50
            
            compressed = self.batch_compress_by_time(messages)
            
            # 恢复默认阈值
            self.time_thresholds[TimeResolution.IMMEDIATE] = 10
            self.time_thresholds[TimeResolution.RECENT] = 50
            self.time_thresholds[TimeResolution.NEAR] = 100
        
        return compressed