#!/usr/bin/env python3
"""
NLPL-based Memory System
基于文件系统和NLPL的认知记忆系统
"""

import os
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import re

@dataclass
class MemoryEvent:
    """记忆事件"""
    timestamp: str
    task_name: str
    task_type: str
    execution_rounds: int
    success: bool
    key_patterns: List[str]
    emotional_markers: Dict[str, float]
    cognitive_load: float
    innovations: List[str]
    errors: List[str]

class NLPLMemorySystem:
    """NLPL记忆系统"""
    
    def __init__(self, memory_dir: str = ".memory"):
        self.memory_dir = Path(memory_dir)
        self._initialize_structure()
        
    def _initialize_structure(self):
        """初始化记忆目录结构"""
        directories = [
            "episodic",
            "semantic/concepts",
            "semantic/patterns",
            "procedural/skills",
            "procedural/habits",
            "working",
            "metacognitive",
            "archive"
        ]
        
        for dir_path in directories:
            (self.memory_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
        # 创建索引文件
        index_files = [
            "episodic/index.nlpl",
            "semantic/relations.nlpl",
            "procedural/proficiency.nlpl",
            "metacognitive/self_knowledge.nlpl"
        ]
        
        for index_file in index_files:
            file_path = self.memory_dir / index_file
            if not file_path.exists():
                file_path.write_text(f"# {index_file}\n生成时间：{datetime.now().isoformat()}\n\n")
    
    # ========== 情景记忆 ==========
    
    def create_episodic_memory(self, event: MemoryEvent) -> Tuple[str, str, str]:
        """创建三层清晰度的情景记忆"""
        timestamp = datetime.now()
        date_dir = self.memory_dir / "episodic" / timestamp.strftime("%Y-%m-%d")
        date_dir.mkdir(exist_ok=True)
        
        base_name = timestamp.strftime("%H-%M-%S") + f"_{self._sanitize_filename(event.task_name)}"
        
        # 生成三个版本
        detailed_path = date_dir / f"{base_name}_detailed.nlpl"
        summary_path = date_dir / f"{base_name}_summary.nlpl"
        gist_path = date_dir / f"{base_name}_gist.nlpl"
        
        # 详细版本
        detailed_content = self._generate_detailed_memory(event)
        detailed_path.write_text(detailed_content, encoding='utf-8')
        
        # 摘要版本
        summary_content = self._generate_summary_memory(event)
        summary_path.write_text(summary_content, encoding='utf-8')
        
        # 要点版本
        gist_content = self._generate_gist_memory(event)
        gist_path.write_text(gist_content, encoding='utf-8')
        
        # 更新索引
        self._update_episodic_index(event, detailed_path, summary_path, gist_path)
        
        return str(detailed_path), str(summary_path), str(gist_path)
    
    def _generate_detailed_memory(self, event: MemoryEvent) -> str:
        """生成详细版本的记忆"""
        return f"""# 任务：{event.task_name}
执行时间：{event.timestamp}
总轮数：{event.execution_rounds}
成功状态：{'成功' if event.success else '失败'}

## 完整执行分析

### 任务类型识别
- **类型**：{event.task_type}
- **复杂度**：{self._assess_complexity(event)}
- **新颖度**：{self._assess_novelty(event)}

### 执行模式分析
识别的模式：
{self._format_patterns(event.key_patterns)}

### 认知负荷评估
- **总体负荷**：{event.cognitive_load:.2f}
- **峰值时刻**：{self._identify_peak_moments(event)}
- **资源使用**：{self._assess_resource_usage(event)}

### 情绪标记
{self._format_emotions(event.emotional_markers)}

### 创新与发现
{self._format_innovations(event.innovations)}

### 错误与恢复
{self._format_errors(event.errors)}

## 详细时间线
[这里应包含完整的执行步骤，由观察Agent填充]

## 性能指标
- **效率评分**：{self._calculate_efficiency(event)}/10
- **创新指数**：{len(event.innovations)}/10
- **稳定性**：{self._calculate_stability(event)}/10

## 经验提取
{self._extract_lessons(event)}
"""
    
    def _generate_summary_memory(self, event: MemoryEvent) -> str:
        """生成摘要版本的记忆"""
        return f"""# 任务：{event.task_name}
时间：{event.timestamp[:10]}
结果：{'成功' if event.success else '失败'}（{event.execution_rounds}轮）

## 关键信息
- **任务类型**：{event.task_type}
- **主要模式**：{', '.join(event.key_patterns[:3])}
- **认知负荷**：{'高' if event.cognitive_load > 0.7 else '中' if event.cognitive_load > 0.4 else '低'}

## 执行特征
{self._summarize_execution(event)}

## 重要发现
{self._summarize_findings(event)}

## 核心经验
{self._extract_core_lessons(event)}
"""
    
    def _generate_gist_memory(self, event: MemoryEvent) -> str:
        """生成要点版本的记忆"""
        return f"""# {event.task_name}
时间：{event.timestamp[:10]}
结果：{'✓' if event.success else '✗'}

## 一句话总结
{self._one_line_summary(event)}

## 核心模式
{event.key_patterns[0] if event.key_patterns else '无特定模式'}

## 记住
✓ {self._key_takeaway(event)}
"""
    
    # ========== 语义记忆 ==========
    
    def create_semantic_concept(self, concept_name: str, definition: str, 
                               features: Dict[str, List[str]], 
                               examples: Dict[str, str]) -> str:
        """创建语义概念"""
        concept_path = self.memory_dir / "semantic" / "concepts" / f"{concept_name}.nlpl"
        
        content = f"""# 概念：{concept_name}
生成时间：{datetime.now().isoformat()}

## 定义
{definition}

## 特征
- **必要特征**：{', '.join(features.get('essential', []))}
- **典型特征**：{', '.join(features.get('typical', []))}
- **可选特征**：{', '.join(features.get('optional', []))}

## 示例
- **典型例子**：{examples.get('typical', '')}
- **边界例子**：{examples.get('boundary', '')}
- **反例**：{examples.get('counter', '')}

## 关联概念
[由海马体Agent后续填充]
"""
        
        concept_path.write_text(content, encoding='utf-8')
        self._update_semantic_relations(concept_name)
        
        return str(concept_path)
    
    def create_semantic_pattern(self, pattern_name: str, trigger: str,
                               steps: List[str], success_rate: float) -> str:
        """创建语义模式"""
        pattern_path = self.memory_dir / "semantic" / "patterns" / f"{pattern_name}.nlpl"
        
        content = f"""# 模式：{pattern_name}
提取时间：{datetime.now().isoformat()}
成功率：{success_rate:.1%}

## 触发条件
{trigger}

## 执行步骤
{self._format_steps(steps)}

## 参数配置
[可根据具体情况调整]

## 使用统计
- **使用次数**：0
- **成功次数**：0
- **平均轮数**：N/A

## 优化历史
- v1.0：初始版本
"""
        
        pattern_path.write_text(content, encoding='utf-8')
        return str(pattern_path)
    
    # ========== 程序性记忆 ==========
    
    def create_procedural_skill(self, skill_name: str, trigger_conditions: str,
                               execution_steps: List[Dict[str, Any]], 
                               proficiency: float = 0.0) -> str:
        """创建程序性技能"""
        skill_path = self.memory_dir / "procedural" / "skills" / f"{skill_name}.nlpl"
        
        content = f"""# 技能：{skill_name}
创建时间：{datetime.now().isoformat()}
熟练度：{proficiency:.1%}

## 触发情境
{trigger_conditions}

## 执行步骤
{self._format_procedural_steps(execution_steps)}

## 熟练度指标
- **使用次数**：0
- **成功率**：0%
- **平均用时**：N/A
- **自动化程度**：{proficiency}

## 相关技能
- **前置技能**：[]
- **组合技能**：[]
- **进阶技能**：[]

## 优化记录
[随使用逐步更新]
"""
        
        skill_path.write_text(content, encoding='utf-8')
        self._update_proficiency_index(skill_name, proficiency)
        
        return str(skill_path)
    
    # ========== 工作记忆 ==========
    
    def update_working_memory(self, task: str, state: Dict[str, Any], 
                             focus: str, activated_memories: List[str]):
        """更新工作记忆"""
        working_path = self.memory_dir / "working" / "current_context.nlpl"
        
        content = f"""# 当前工作上下文
更新时间：{datetime.now().isoformat()}

## 活动任务
**主任务**：{task}
**状态**：{state.get('status', '进行中')}

## 注意力焦点
**当前关注**：{focus}

## 临时状态
{self._format_state(state)}

## 激活的记忆
{self._format_activated_memories(activated_memories)}
"""
        
        working_path.write_text(content, encoding='utf-8')
    
    # ========== 元认知记忆 ==========
    
    def update_metacognitive_assessment(self, metrics: Dict[str, float], 
                                       strategies: Dict[str, Dict],
                                       recommendations: List[str]):
        """更新元认知评估"""
        meta_path = self.memory_dir / "metacognitive" / "assessment.nlpl"
        
        content = f"""# 元认知评估
评估时间：{datetime.now().isoformat()}

## 性能指标
{self._format_metrics(metrics)}

## 策略效果
{self._format_strategies(strategies)}

## 改进建议
{self._format_recommendations(recommendations)}

## 系统健康度
{self._assess_system_health()}
"""
        
        meta_path.write_text(content, encoding='utf-8')
    
    # ========== 记忆检索 ==========
    
    def search_memories(self, query: str, memory_type: Optional[str] = None, 
                       limit: int = 10) -> List[str]:
        """使用grep搜索记忆"""
        if memory_type:
            search_dir = self.memory_dir / memory_type
        else:
            search_dir = self.memory_dir
            
        try:
            # 使用grep搜索
            result = subprocess.run(
                ["grep", "-r", "-l", query, str(search_dir), "--include=*.nlpl"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return files[:limit] if files[0] else []
            else:
                return []
                
        except (subprocess.TimeoutExpired, Exception):
            return []
    
    def get_recent_memories(self, days: int = 7) -> List[str]:
        """获取最近N天的记忆"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_memories = []
        
        episodic_dir = self.memory_dir / "episodic"
        for date_dir in episodic_dir.iterdir():
            if date_dir.is_dir():
                try:
                    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                    if dir_date >= cutoff:
                        for memory_file in date_dir.glob("*.nlpl"):
                            recent_memories.append(str(memory_file))
                except ValueError:
                    continue
                    
        return sorted(recent_memories, reverse=True)
    
    # ========== 记忆衰减 ==========
    
    def apply_temporal_decay(self):
        """应用时间衰减规则"""
        now = datetime.now()
        decay_log = []
        
        episodic_dir = self.memory_dir / "episodic"
        for date_dir in episodic_dir.iterdir():
            if not date_dir.is_dir():
                continue
                
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                age_days = (now - dir_date).days
                
                for memory_file in date_dir.glob("*.nlpl"):
                    if age_days > 7 and "detailed" in memory_file.name:
                        # 7天后删除详细版本
                        importance = self._assess_importance(memory_file)
                        if importance < 0.7:
                            memory_file.unlink()
                            decay_log.append(f"删除详细版本：{memory_file.name}")
                            
                    elif age_days > 30 and "summary" in memory_file.name:
                        # 30天后删除摘要版本
                        if not self._is_consolidated(memory_file):
                            memory_file.unlink()
                            decay_log.append(f"删除摘要版本：{memory_file.name}")
                            
                    elif age_days > 90 and "gist" in memory_file.name:
                        # 90天后归档要点版本
                        if self._should_archive(memory_file):
                            archive_dir = self.memory_dir / "archive" / date_dir.name
                            archive_dir.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(memory_file), str(archive_dir))
                            decay_log.append(f"归档：{memory_file.name}")
                            
            except ValueError:
                continue
                
        return decay_log
    
    # ========== 辅助方法 ==========
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        return re.sub(r'[^\w\s-]', '', name)[:50]
    
    def _assess_complexity(self, event: MemoryEvent) -> str:
        """评估任务复杂度"""
        if event.execution_rounds > 20:
            return "高"
        elif event.execution_rounds > 10:
            return "中"
        else:
            return "低"
    
    def _assess_novelty(self, event: MemoryEvent) -> str:
        """评估任务新颖度"""
        # 简化实现：基于创新数量
        if len(event.innovations) > 2:
            return "高"
        elif len(event.innovations) > 0:
            return "中"
        else:
            return "低"
    
    def _format_patterns(self, patterns: List[str]) -> str:
        """格式化模式列表"""
        if not patterns:
            return "- 无特定模式"
        return "\n".join(f"- {p}" for p in patterns)
    
    def _format_emotions(self, emotions: Dict[str, float]) -> str:
        """格式化情绪标记"""
        if not emotions:
            return "无特殊情绪标记"
        
        lines = []
        for emotion, intensity in emotions.items():
            bars = "■" * int(intensity * 10)
            lines.append(f"- **{emotion}**：{bars} ({intensity:.1f})")
        return "\n".join(lines)
    
    def _format_innovations(self, innovations: List[str]) -> str:
        """格式化创新发现"""
        if not innovations:
            return "无创新发现"
        return "\n".join(f"💡 {i}" for i in innovations)
    
    def _format_errors(self, errors: List[str]) -> str:
        """格式化错误记录"""
        if not errors:
            return "无错误发生"
        return "\n".join(f"⚠️ {e}" for e in errors)
    
    def _calculate_efficiency(self, event: MemoryEvent) -> float:
        """计算效率分数"""
        base_score = 10.0
        if not event.success:
            base_score *= 0.5
        if event.execution_rounds > 20:
            base_score *= 0.8
        if event.cognitive_load > 0.8:
            base_score *= 0.9
        return min(10, max(0, base_score))
    
    def _calculate_stability(self, event: MemoryEvent) -> float:
        """计算稳定性分数"""
        error_penalty = len(event.errors) * 1.5
        return max(0, 10 - error_penalty)
    
    def _extract_lessons(self, event: MemoryEvent) -> str:
        """提取经验教训"""
        lessons = []
        
        if event.success:
            lessons.append(f"成功因素：{event.key_patterns[0] if event.key_patterns else '稳定执行'}")
        else:
            lessons.append(f"失败原因：{event.errors[0] if event.errors else '未知'}")
            
        if event.innovations:
            lessons.append(f"创新价值：{event.innovations[0]}")
            
        return "\n".join(f"- {l}" for l in lessons)
    
    def _update_episodic_index(self, event: MemoryEvent, 
                               detailed_path: Path, 
                               summary_path: Path, 
                               gist_path: Path):
        """更新情景记忆索引"""
        index_path = self.memory_dir / "episodic" / "index.nlpl"
        
        entry = f"""
## {event.timestamp}
- **任务类型**：{event.task_type}
- **执行模式**：{event.key_patterns[0] if event.key_patterns else '默认'}
- **关键特征**：[{', '.join(event.key_patterns[:3])}]
- **文件路径**：
  - 详细：{detailed_path}
  - 摘要：{summary_path}
  - 要点：{gist_path}
"""
        
        with open(index_path, 'a', encoding='utf-8') as f:
            f.write(entry)
    
    def _update_semantic_relations(self, concept_name: str):
        """更新语义关系网络"""
        relations_path = self.memory_dir / "semantic" / "relations.nlpl"
        
        # 简化实现：追加新概念
        with open(relations_path, 'a', encoding='utf-8') as f:
            f.write(f"\n- 新概念：{concept_name} (待建立关系)\n")
    
    def _update_proficiency_index(self, skill_name: str, proficiency: float):
        """更新技能熟练度索引"""
        proficiency_path = self.memory_dir / "procedural" / "proficiency.nlpl"
        
        with open(proficiency_path, 'a', encoding='utf-8') as f:
            f.write(f"\n- {skill_name}：{proficiency:.1%}\n")
    
    def _assess_importance(self, file_path: Path) -> float:
        """评估记忆重要性"""
        # 简化实现：基于文件大小和访问时间
        try:
            stat = file_path.stat()
            size_factor = min(1.0, stat.st_size / 10000)
            
            # 最近访问时间
            last_access = datetime.fromtimestamp(stat.st_atime)
            days_since_access = (datetime.now() - last_access).days
            access_factor = max(0, 1 - days_since_access / 30)
            
            return (size_factor + access_factor) / 2
        except:
            return 0.5
    
    def _is_consolidated(self, file_path: Path) -> bool:
        """检查记忆是否已巩固"""
        # 简化实现：检查是否有对应的语义或程序性记忆
        memory_name = file_path.stem.split('_')[0]
        
        semantic_exists = any(
            (self.memory_dir / "semantic" / "concepts").glob(f"*{memory_name}*")
        )
        procedural_exists = any(
            (self.memory_dir / "procedural" / "skills").glob(f"*{memory_name}*")
        )
        
        return semantic_exists or procedural_exists
    
    def _should_archive(self, file_path: Path) -> bool:
        """判断是否应该归档"""
        importance = self._assess_importance(file_path)
        return importance < 0.3
    
    # 简化的辅助方法
    def _identify_peak_moments(self, event):
        return "执行中期"
    
    def _assess_resource_usage(self, event):
        return "中等"
    
    def _summarize_execution(self, event):
        return f"采用{event.key_patterns[0] if event.key_patterns else '默认'}模式执行"
    
    def _summarize_findings(self, event):
        if event.innovations:
            return f"发现{len(event.innovations)}个创新点"
        return "无特殊发现"
    
    def _extract_core_lessons(self, event):
        if event.success:
            return "任务成功完成，模式有效"
        return "需要改进执行策略"
    
    def _one_line_summary(self, event):
        return f"使用{event.execution_rounds}轮{'成功' if event.success else '失败'}完成{event.task_type}任务"
    
    def _key_takeaway(self, event):
        if event.innovations:
            return event.innovations[0]
        elif event.key_patterns:
            return f"{event.key_patterns[0]}模式有效"
        else:
            return "保持稳定执行"
    
    def _format_steps(self, steps):
        return "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    
    def _format_procedural_steps(self, steps):
        formatted = []
        for i, step in enumerate(steps, 1):
            formatted.append(f"### 步骤{i}：{step.get('name', '未命名')}")
            if 'action' in step:
                formatted.append(f"- **动作**：{step['action']}")
            if 'tool' in step:
                formatted.append(f"- **工具**：{step['tool']}")
            if 'validation' in step:
                formatted.append(f"- **验证**：{step['validation']}")
        return "\n".join(formatted)
    
    def _format_state(self, state):
        lines = []
        for key, value in state.items():
            if isinstance(value, dict):
                lines.append(f"**{key}**：")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"**{key}**：{value}")
        return "\n".join(lines)
    
    def _format_activated_memories(self, memories):
        if not memories:
            return "无激活记忆"
        return "\n".join(f"- {m}" for m in memories[:5])
    
    def _format_metrics(self, metrics):
        lines = []
        for metric, value in metrics.items():
            percentage = int(value * 100)
            bars = "■" * (percentage // 10) + "□" * (10 - percentage // 10)
            lines.append(f"- **{metric}**：{bars} {percentage}%")
        return "\n".join(lines)
    
    def _format_strategies(self, strategies):
        lines = []
        for name, stats in strategies.items():
            lines.append(f"### {name}")
            lines.append(f"- 成功率：{stats.get('success_rate', 0):.1%}")
            lines.append(f"- 使用频率：{stats.get('usage_frequency', 0):.1%}")
            lines.append(f"- 效率得分：{stats.get('efficiency', 0):.2f}")
        return "\n".join(lines)
    
    def _format_recommendations(self, recommendations):
        return "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
    
    def _assess_system_health(self):
        """评估系统健康度"""
        # 简化实现
        return """
- 记忆容量：正常
- 检索效率：良好
- 知识增长：稳定
- 系统负载：适中
"""


# 使用示例
if __name__ == "__main__":
    # 初始化记忆系统
    memory = NLPLMemorySystem()
    
    # 创建一个情景记忆
    event = MemoryEvent(
        timestamp=datetime.now().isoformat(),
        task_name="创建计算器模块",
        task_type="文件创建",
        execution_rounds=12,
        success=True,
        key_patterns=["快速原型", "迭代开发"],
        emotional_markers={"满意": 0.8, "自信": 0.7},
        cognitive_load=0.4,
        innovations=["使用类型注解提高代码质量"],
        errors=[]
    )
    
    paths = memory.create_episodic_memory(event)
    print(f"创建情景记忆：\n  详细：{paths[0]}\n  摘要：{paths[1]}\n  要点：{paths[2]}")
    
    # 创建语义概念
    concept_path = memory.create_semantic_concept(
        "文件操作",
        "与文件系统交互的行为",
        {
            "essential": ["路径", "内容"],
            "typical": ["编码", "权限"],
            "optional": ["缓冲", "锁"]
        },
        {
            "typical": "读取配置文件",
            "boundary": "读取网络文件",
            "counter": "内存操作"
        }
    )
    print(f"创建语义概念：{concept_path}")
    
    # 创建程序性技能
    skill_path = memory.create_procedural_skill(
        "调试Python错误",
        "当出现Python异常时",
        [
            {"name": "读取错误", "action": "提取错误信息", "tool": "parse_traceback"},
            {"name": "定位问题", "action": "找到错误位置", "tool": "read_file"},
            {"name": "修复错误", "action": "应用修复方案", "tool": "edit_file"}
        ],
        proficiency=0.7
    )
    print(f"创建程序性技能：{skill_path}")
    
    # 搜索记忆
    results = memory.search_memories("计算器")
    print(f"搜索结果：{results}")
    
    # 应用时间衰减
    decay_log = memory.apply_temporal_decay()
    if decay_log:
        print(f"衰减处理：{decay_log}")