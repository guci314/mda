#!/usr/bin/env python3
"""
MemoryWithNaturalDecay - 极简记忆系统
模仿Claude Code的自然压缩机制
这是唯一需要的记忆类！
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CompressedMemory:
    """压缩后的记忆单元"""
    timestamp: str
    summary: str
    message_count: int
    key_points: List[str]
    task_results: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


class MemoryWithNaturalDecay:
    """
    极简记忆系统 - 自然压缩与衰减
    
    核心理念：
    1. 压缩就是记忆衰减
    2. 压力触发自动压缩
    3. 压缩历史自然分层
    """
    
    def __init__(self, 
                 pressure_threshold: int = 50,
                 work_dir: str = ".memory",
                 enable_persistence: bool = True):
        """
        初始化记忆系统
        
        Args:
            pressure_threshold: 触发压缩的消息数阈值
            work_dir: 持久化目录
            enable_persistence: 是否启用持久化
        """
        self.messages: List[Dict[str, Any]] = []
        self.compressed_history: List[CompressedMemory] = []
        self.pressure_threshold = pressure_threshold
        self.work_dir = Path(work_dir)
        self.enable_persistence = enable_persistence
        
        # 统计信息
        self.stats = {
            "total_messages": 0,
            "compressions": 0,
            "current_pressure": 0
        }
        
        # 初始化持久化
        if self.enable_persistence:
            self.work_dir.mkdir(parents=True, exist_ok=True)
            self._load_history()
    
    def add_message(self, role: str, content: str, **metadata) -> None:
        """
        添加消息并检查是否需要压缩
        
        Args:
            role: 消息角色 (user/assistant/tool)
            content: 消息内容
            metadata: 额外元数据
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **metadata
        }
        
        self.messages.append(message)
        self.stats["total_messages"] += 1
        self.stats["current_pressure"] = len(self.messages)
        
        # 压力检查 - 自动触发压缩
        if self.should_compact():
            self.compact()
    
    def should_compact(self) -> bool:
        """
        检查是否需要压缩
        模仿Claude Code的压力触发机制
        """
        return len(self.messages) > self.pressure_threshold
    
    def compact(self) -> CompressedMemory:
        """
        执行自然压缩 - 核心算法
        将当前消息窗口压缩为摘要
        """
        if not self.messages:
            return None
        
        # 1. 提取关键信息
        summary = self._extract_summary()
        key_points = self._extract_key_points()
        task_results = self._extract_task_results()
        
        # 2. 创建压缩记忆
        compressed = CompressedMemory(
            timestamp=datetime.now().isoformat(),
            summary=summary,
            message_count=len(self.messages),
            key_points=key_points,
            task_results=task_results
        )
        
        # 3. 保存到历史
        self.compressed_history.append(compressed)
        self.stats["compressions"] += 1
        
        # 4. 清理窗口，保留上下文
        context_summary = self._create_context_summary(compressed)
        self.messages = [{
            "role": "system",
            "content": f"[Previous Context]\n{context_summary}",
            "timestamp": datetime.now().isoformat()
        }]
        
        # 5. 持久化
        if self.enable_persistence:
            self._save_compression(compressed)
        
        print(f"🗜️ 记忆压缩完成：{len(self.messages)} → 1 (保留上下文)")
        
        return compressed
    
    def _extract_summary(self) -> str:
        """
        提取对话摘要
        模拟LLM的摘要能力，但用简单规则实现
        """
        # 统计消息类型
        user_msgs = [m for m in self.messages if m["role"] == "user"]
        tool_calls = [m for m in self.messages if m["role"] == "tool"]
        
        # 提取任务描述（第一个用户消息）
        task = user_msgs[0]["content"][:100] if user_msgs else "未知任务"
        
        # 生成摘要
        summary = f"执行了{len(self.messages)}轮对话，"
        summary += f"包含{len(user_msgs)}个用户请求，"
        summary += f"{len(tool_calls)}次工具调用。"
        summary += f"主要任务：{task}"
        
        return summary
    
    def _extract_key_points(self) -> List[str]:
        """
        提取关键点
        识别重要的决策和发现
        """
        key_points = []
        
        for msg in self.messages:
            content = msg["content"]
            
            # 识别关键标记
            if any(marker in content for marker in ["成功", "完成", "创建", "实现"]):
                # 提取包含关键词的句子
                sentences = content.split("。")
                for sent in sentences[:3]:  # 最多3个
                    if len(sent) > 10 and len(sent) < 100:
                        key_points.append(sent.strip())
            
            # 识别错误和问题
            if any(marker in content for marker in ["错误", "失败", "问题"]):
                key_points.append(f"⚠️ {content[:50]}")
        
        return key_points[:5]  # 最多保留5个关键点
    
    def _extract_task_results(self) -> List[str]:
        """
        提取任务结果
        识别创建的文件、完成的功能等
        """
        results = []
        
        for msg in self.messages:
            if msg["role"] == "tool":
                content = msg["content"]
                
                # 识别文件操作
                if "文件" in content or "file" in content.lower():
                    results.append(content[:80])
                
                # 识别成功的执行
                if "成功" in content or "完成" in content:
                    results.append(content[:80])
        
        return results[:3]  # 最多3个结果
    
    def _create_context_summary(self, compressed: CompressedMemory) -> str:
        """
        创建上下文摘要
        用于保留在新消息窗口中
        """
        summary = f"已完成{compressed.message_count}轮对话。\n"
        summary += f"摘要：{compressed.summary}\n"
        
        if compressed.key_points:
            summary += "\n关键点：\n"
            for point in compressed.key_points[:3]:
                summary += f"- {point}\n"
        
        if compressed.task_results:
            summary += "\n已完成：\n"
            for result in compressed.task_results[:2]:
                summary += f"- {result}\n"
        
        return summary
    
    def get_context(self, max_history: int = 3) -> List[Dict[str, Any]]:
        """
        获取LLM上下文
        包含当前消息和压缩历史
        
        Args:
            max_history: 包含的压缩历史数量
        """
        context = []
        
        # 1. 添加最近的压缩历史
        if self.compressed_history:
            recent_history = self.compressed_history[-max_history:]
            history_summary = self._format_history(recent_history)
            
            context.append({
                "role": "system",
                "content": f"[Compressed History]\n{history_summary}"
            })
        
        # 2. 添加当前消息窗口
        context.extend(self.messages)
        
        return context
    
    def _format_history(self, history: List[CompressedMemory]) -> str:
        """
        格式化压缩历史
        """
        if not history:
            return "无历史记录"
        
        formatted = []
        for i, mem in enumerate(history, 1):
            formatted.append(f"[阶段{i}] {mem.summary}")
            if mem.key_points:
                formatted.append(f"  关键：{', '.join(mem.key_points[:2])}")
        
        return "\n".join(formatted)
    
    def search(self, query: str, limit: int = 5) -> List[Tuple[CompressedMemory, float]]:
        """
        搜索压缩历史
        
        Args:
            query: 搜索查询
            limit: 返回结果数量
        
        Returns:
            匹配的压缩记忆和相关度分数
        """
        results = []
        query_lower = query.lower()
        
        for mem in self.compressed_history:
            # 简单的关键词匹配评分
            score = 0.0
            
            # 检查摘要
            if query_lower in mem.summary.lower():
                score += 1.0
            
            # 检查关键点
            for point in mem.key_points:
                if query_lower in point.lower():
                    score += 0.5
            
            # 检查结果
            for result in mem.task_results:
                if query_lower in result.lower():
                    score += 0.3
            
            if score > 0:
                results.append((mem, score))
        
        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    # ========== 持久化支持 ==========
    
    def _save_compression(self, compressed: CompressedMemory) -> None:
        """
        保存压缩记忆到磁盘
        """
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_id = hashlib.md5(compressed.summary.encode()).hexdigest()[:8]
        filename = f"compressed_{timestamp}_{hash_id}.json"
        
        filepath = self.work_dir / "compressed" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(compressed.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_history(self) -> None:
        """
        从磁盘加载压缩历史
        """
        compressed_dir = self.work_dir / "compressed"
        if not compressed_dir.exists():
            return
        
        for filepath in sorted(compressed_dir.glob("compressed_*.json")):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.compressed_history.append(CompressedMemory.from_dict(data))
    
    def save_state(self) -> None:
        """
        保存完整状态
        """
        if not self.enable_persistence:
            return
        
        state = {
            "messages": self.messages,
            "stats": self.stats,
            "pressure_threshold": self.pressure_threshold
        }
        
        state_file = self.work_dir / "state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def load_state(self) -> None:
        """
        加载完整状态
        """
        state_file = self.work_dir / "state.json"
        if not state_file.exists():
            return
        
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
            self.messages = state.get("messages", [])
            self.stats = state.get("stats", self.stats)
    
    # ========== 统计和监控 ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        """
        return {
            **self.stats,
            "compressed_memories": len(self.compressed_history),
            "memory_pressure": f"{len(self.messages)}/{self.pressure_threshold}",
            "compression_rate": f"{self.stats['compressions']}次"
        }
    
    def get_memory_timeline(self) -> List[Dict[str, Any]]:
        """
        获取记忆时间线
        """
        timeline = []
        
        for mem in self.compressed_history:
            timeline.append({
                "time": mem.timestamp,
                "type": "compression",
                "summary": mem.summary[:100],
                "messages": mem.message_count
            })
        
        return timeline
    
    def clear(self) -> None:
        """
        清空所有记忆
        """
        self.messages.clear()
        self.compressed_history.clear()
        self.stats = {
            "total_messages": 0,
            "compressions": 0,
            "current_pressure": 0
        }


# 使用示例
if __name__ == "__main__":
    # 创建极简记忆系统
    memory = MemoryWithNaturalDecay(
        pressure_threshold=10,  # 低阈值用于演示
        work_dir="test_natural_decay"
    )
    
    # 模拟对话
    print("🧠 测试自然衰减记忆系统")
    print("=" * 50)
    
    # 添加一系列消息
    for i in range(25):
        if i % 3 == 0:
            memory.add_message("user", f"请求{i//3 + 1}：执行任务")
        elif i % 3 == 1:
            memory.add_message("assistant", f"正在处理任务{i//3 + 1}...")
        else:
            memory.add_message("tool", f"任务{i//3 + 1}完成")
    
    # 显示统计
    print("\n📊 记忆系统统计：")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 搜索测试
    print("\n🔍 搜索'任务'：")
    results = memory.search("任务", limit=3)
    for mem, score in results:
        print(f"  相关度{score:.1f}: {mem.summary[:50]}")
    
    # 显示时间线
    print("\n📅 记忆时间线：")
    timeline = memory.get_memory_timeline()
    for event in timeline:
        print(f"  {event['time'][:19]}: {event['summary'][:40]}...")