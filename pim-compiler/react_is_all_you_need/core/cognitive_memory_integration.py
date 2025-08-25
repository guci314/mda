#!/usr/bin/env python3
"""
Cognitive Memory Integration Layer
连接SimpleMemoryManager（技术层）和NLPLMemorySystem（认知层）
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

from .simple_memory_manager import SimpleMemoryManager, Message
from .nlpl_memory_system import NLPLMemorySystem, MemoryEvent
from .react_agent import ReactAgent  # type: ignore


class CognitiveMemoryIntegration:
    """
    认知记忆集成层
    协调SimpleMemoryManager和NLPLMemorySystem的工作
    """
    
    def __init__(self, 
                 work_dir: str = ".",
                 window_size: int = 50,
                 memory_dir: str = ".memory"):
        """
        初始化集成层
        
        Args:
            work_dir: 工作目录
            window_size: 消息窗口大小
            memory_dir: 记忆系统目录
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # 技术层：消息管理
        self.message_manager = SimpleMemoryManager(window_size=window_size)
        
        # 认知层：记忆系统
        self.memory_system = NLPLMemorySystem(memory_dir=str(self.work_dir / memory_dir))
        
        # 4层Agent（懒加载）
        self._agents = {}
        self._init_counters()
        
    def _init_counters(self):
        """初始化计数器"""
        self.total_rounds = 0
        self.message_count = 0
        self.episode_count = 0
        
    # ========== 消息处理 ==========
    
    def add_message(self, role: str, content: str, 
                   tool_calls: Optional[List[Dict]] = None) -> None:
        """
        添加消息并触发认知处理
        
        Args:
            role: 消息角色
            content: 消息内容
            tool_calls: 工具调用
        """
        # 1. 添加到消息窗口
        self.message_manager.add_message(role, content, tool_calls)
        self.message_count += 1
        
        # 2. 触发观察（每10条消息）
        if self.message_count % 10 == 0:
            self._trigger_observation()
        
        # 3. 触发巩固（每50个事件）
        if self.episode_count >= 50:
            self._trigger_consolidation()
            self.episode_count = 0
            
        # 4. 触发元认知（每100轮）
        if self.total_rounds >= 100:
            self._trigger_metacognition()
            self.total_rounds = 0
    
    def process_task_completion(self, task_name: str, success: bool, 
                               rounds: int) -> Tuple[str, str, str]:
        """
        处理任务完成，生成情景记忆
        
        Args:
            task_name: 任务名称
            success: 是否成功
            rounds: 执行轮数
            
        Returns:
            三个记忆文件路径
        """
        # 从消息历史提取执行特征
        messages = self.message_manager.get_messages()
        event = self._extract_event_from_messages(task_name, success, rounds, messages)
        
        # 创建情景记忆
        paths = self.memory_system.create_episodic_memory(event)
        self.episode_count += 1
        
        return paths
    
    # ========== 认知触发 ==========
    
    def _trigger_observation(self):
        """触发L2观察Agent"""
        print("🔍 触发观察Agent分析执行模式...")
        
        # 获取观察Agent
        observer = self._get_observer_agent()
        
        # 准备观察任务
        messages = self.message_manager.get_recent_messages(10)
        observation_task = self._prepare_observation_task(messages)
        
        # 执行观察（异步或同步）
        try:
            result = observer.execute_task(observation_task)
            print("✅ 观察完成")
        except Exception as e:
            print(f"⚠️ 观察失败：{e}")
    
    def _trigger_consolidation(self):
        """触发L3海马体Agent"""
        print("🧠 触发海马体巩固记忆...")
        
        # 获取海马体Agent
        hippocampus = self._get_hippocampus_agent()
        
        # 执行巩固
        consolidation_task = """
        扫描最近的情景记忆，提取可复用的模式和知识。
        将重复出现的模式保存为语义记忆，
        将成功的执行步骤保存为程序性记忆。
        """
        
        try:
            result = hippocampus.execute_task(consolidation_task)
            print("✅ 记忆巩固完成")
            
            # 应用时间衰减
            decay_log = self.memory_system.apply_temporal_decay()
            if decay_log:
                print(f"🕐 时间衰减处理：{len(decay_log)}个文件")
                
        except Exception as e:
            print(f"⚠️ 巩固失败：{e}")
    
    def _trigger_metacognition(self):
        """触发L4元认知Agent"""
        print("🎯 触发元认知评估...")
        
        # 获取元认知Agent  
        metacognition = self._get_metacognition_agent()
        
        # 准备评估数据
        stats = self._collect_system_stats()
        evaluation_task = f"""
        评估系统整体表现：
        {json.dumps(stats, indent=2, ensure_ascii=False)}
        
        生成优化建议和策略调整。
        """
        
        try:
            result = metacognition.execute_task(evaluation_task)
            print("✅ 元认知评估完成")
        except Exception as e:
            print(f"⚠️ 元认知失败：{e}")
    
    # ========== Agent管理 ==========
    
    def _get_observer_agent(self) -> ReactAgent:
        """获取观察Agent（懒加载）"""
        if 'observer' not in self._agents:
            knowledge_file = Path(__file__).parent.parent / "knowledge" / "memory" / "nlpl" / "observer_agent.nlpl"
            self._agents['observer'] = ReactAgent(
                work_dir=str(self.work_dir / ".memory" / "episodic"),
                knowledge_files=[str(knowledge_file)] if knowledge_file.exists() else [],
                max_rounds=10,
                window_size=30  # 观察Agent使用较小的窗口
            )
        return self._agents['observer']
    
    def _get_hippocampus_agent(self) -> ReactAgent:
        """获取海马体Agent（懒加载）"""
        if 'hippocampus' not in self._agents:
            knowledge_file = Path(__file__).parent.parent / "knowledge" / "memory" / "nlpl" / "hippocampus_agent.nlpl"
            self._agents['hippocampus'] = ReactAgent(
                work_dir=str(self.work_dir / ".memory"),
                knowledge_files=[str(knowledge_file)] if knowledge_file.exists() else [],
                max_rounds=20,
                window_size=30  # 海马体使用较小窗口
            )
        return self._agents['hippocampus']
    
    def _get_metacognition_agent(self) -> ReactAgent:
        """获取元认知Agent（懒加载）"""
        if 'metacognition' not in self._agents:
            knowledge_file = Path(__file__).parent.parent / "knowledge" / "memory" / "nlpl" / "metacognition_agent.nlpl"
            self._agents['metacognition'] = ReactAgent(
                work_dir=str(self.work_dir / ".memory" / "metacognitive"),
                knowledge_files=[str(knowledge_file)] if knowledge_file.exists() else [],
                max_rounds=15,
                window_size=20  # 元认知使用更小窗口
            )
        return self._agents['metacognition']
    
    # ========== 辅助方法 ==========
    
    def _extract_event_from_messages(self, task_name: str, success: bool,
                                    rounds: int, messages: List[Message]) -> MemoryEvent:
        """从消息历史提取事件特征"""
        
        # 分析消息获取模式
        patterns = self._identify_patterns(messages)
        emotions = self._assess_emotions(messages)
        load = self._assess_cognitive_load(messages)
        innovations = self._find_innovations(messages)
        errors = self._find_errors(messages)
        
        return MemoryEvent(
            timestamp=datetime.now().isoformat(),
            task_name=task_name,
            task_type=self._classify_task(task_name),
            execution_rounds=rounds,
            success=success,
            key_patterns=patterns,
            emotional_markers=emotions,
            cognitive_load=load,
            innovations=innovations,
            errors=errors
        )
    
    def _prepare_observation_task(self, messages: List[Message]) -> str:
        """准备观察任务描述"""
        # 将消息转换为NLPL格式的执行轨迹
        trace = "# 执行轨迹\n\n"
        for i, msg in enumerate(messages, 1):
            trace += f"## 消息{i} ({msg.role})\n"
            trace += f"时间：{msg.timestamp}\n"
            trace += f"内容：{msg.content[:200]}...\n\n"
            
        return f"""
分析以下执行轨迹，识别执行模式和关键特征：

{trace}

请生成观察报告，包括：
1. 执行模式识别
2. 关键决策点
3. 认知负荷评估
4. 改进建议
"""
    
    def _collect_system_stats(self) -> Dict[str, Any]:
        """收集系统统计信息"""
        return {
            "message_stats": self.message_manager.get_stats(),
            "message_summary": self.message_manager.get_message_summary(),
            "episode_count": self.episode_count,
            "total_rounds": self.total_rounds,
            "memory_files": self._count_memory_files(),
            "recent_patterns": self._get_recent_patterns()
        }
    
    def _identify_patterns(self, messages: List[Message]) -> List[str]:
        """识别执行模式"""
        patterns = []
        
        # 统计工具使用
        tool_count = sum(1 for m in messages if m.role == "tool")
        if tool_count > len(messages) * 0.3:
            patterns.append("工具密集型")
            
        # 检查错误恢复
        error_recovery = any("错误" in m.content or "失败" in m.content 
                            for m in messages)
        if error_recovery:
            patterns.append("错误恢复")
            
        # 检查迭代模式
        if len(messages) > 15:
            patterns.append("迭代优化")
        else:
            patterns.append("快速执行")
            
        return patterns
    
    def _assess_emotions(self, messages: List[Message]) -> Dict[str, float]:
        """评估情绪标记"""
        emotions = {}
        
        # 简单的关键词匹配
        positive_words = ["成功", "完成", "很好", "完美"]
        negative_words = ["失败", "错误", "问题", "无法"]
        
        positive_count = 0
        negative_count = 0
        
        for msg in messages:
            content_lower = msg.content.lower()
            positive_count += sum(1 for word in positive_words if word in content_lower)
            negative_count += sum(1 for word in negative_words if word in content_lower)
        
        total = max(1, positive_count + negative_count)
        if positive_count > negative_count:
            emotions["满意"] = positive_count / total
        else:
            emotions["挫折"] = negative_count / total
            
        return emotions
    
    def _assess_cognitive_load(self, messages: List[Message]) -> float:
        """评估认知负荷"""
        # 基于消息长度和数量的简单估算
        avg_length = sum(len(m.content) for m in messages) / max(1, len(messages))
        
        if avg_length > 500 or len(messages) > 20:
            return 0.8  # 高负荷
        elif avg_length > 200 or len(messages) > 10:
            return 0.5  # 中负荷
        else:
            return 0.3  # 低负荷
    
    def _find_innovations(self, messages: List[Message]) -> List[str]:
        """发现创新点"""
        innovations = []
        
        innovation_markers = ["新方法", "创新", "发现", "原来", "想到"]
        for msg in messages:
            if msg.role == "assistant":
                for marker in innovation_markers:
                    if marker in msg.content:
                        # 提取包含创新标记的句子
                        sentences = msg.content.split("。")
                        for sent in sentences:
                            if marker in sent:
                                innovations.append(sent.strip())
                                break
                                
        return innovations[:3]  # 最多3个
    
    def _find_errors(self, messages: List[Message]) -> List[str]:
        """发现错误"""
        errors = []
        
        error_markers = ["错误", "失败", "异常", "无法", "Error", "Failed"]
        for msg in messages:
            for marker in error_markers:
                if marker in msg.content:
                    # 提取错误描述
                    lines = msg.content.split("\n")
                    for line in lines:
                        if marker in line:
                            errors.append(line.strip()[:100])
                            break
                            
        return errors[:3]  # 最多3个
    
    def _classify_task(self, task_name: str) -> str:
        """分类任务类型"""
        task_lower = task_name.lower()
        
        if any(word in task_lower for word in ["创建", "新建", "生成"]):
            return "创建任务"
        elif any(word in task_lower for word in ["修改", "更新", "编辑"]):
            return "修改任务"
        elif any(word in task_lower for word in ["分析", "检查", "评估"]):
            return "分析任务"
        elif any(word in task_lower for word in ["测试", "验证", "调试"]):
            return "测试任务"
        else:
            return "通用任务"
    
    def _count_memory_files(self) -> Dict[str, int]:
        """统计记忆文件数量"""
        counts = {}
        memory_dir = self.work_dir / ".memory"
        
        if memory_dir.exists():
            counts["episodic"] = len(list((memory_dir / "episodic").glob("**/*.nlpl")))
            counts["semantic"] = len(list((memory_dir / "semantic").glob("**/*.nlpl")))
            counts["procedural"] = len(list((memory_dir / "procedural").glob("**/*.nlpl")))
            
        return counts
    
    def _get_recent_patterns(self) -> List[str]:
        """获取最近使用的模式"""
        # 从语义记忆中读取最近的模式
        patterns = []
        patterns_dir = self.work_dir / ".memory" / "semantic" / "patterns"
        
        if patterns_dir.exists():
            pattern_files = sorted(patterns_dir.glob("*.nlpl"), 
                                 key=lambda p: p.stat().st_mtime, 
                                 reverse=True)
            for pf in pattern_files[:3]:
                patterns.append(pf.stem)
                
        return patterns
    
    # ========== 公共接口 ==========
    
    def get_context(self) -> List[Dict[str, Any]]:
        """获取LLM上下文"""
        return self.message_manager.get_context()
    
    def search_memory(self, query: str, limit: int = 10) -> List[str]:
        """搜索记忆"""
        return self.memory_system.search_memories(query, limit=limit)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取综合统计"""
        return {
            "message_manager": self.message_manager.get_stats(),
            "cognitive_counters": {
                "total_rounds": self.total_rounds,
                "message_count": self.message_count,
                "episode_count": self.episode_count
            },
            "memory_files": self._count_memory_files()
        }
    
    def cleanup(self):
        """清理资源"""
        self.message_manager.clear()
        # NLPLMemorySystem的文件保留，不清理


# 使用示例
if __name__ == "__main__":
    # 创建集成层
    cognitive_memory = CognitiveMemoryIntegration(
        work_dir="test_memory",
        window_size=30
    )
    
    # 模拟任务执行
    cognitive_memory.add_message("user", "创建一个计算器模块")
    cognitive_memory.add_message("assistant", "开始创建计算器模块...")
    cognitive_memory.add_message("tool", "文件 calculator.py 创建成功")
    cognitive_memory.add_message("assistant", "计算器模块创建完成")
    
    # 处理任务完成
    paths = cognitive_memory.process_task_completion(
        task_name="创建计算器模块",
        success=True,
        rounds=4
    )
    
    print(f"生成的记忆文件：")
    for path in paths:
        print(f"  - {path}")
    
    # 获取统计
    stats = cognitive_memory.get_stats()
    print(f"\n系统统计：{json.dumps(stats, indent=2, ensure_ascii=False)}")