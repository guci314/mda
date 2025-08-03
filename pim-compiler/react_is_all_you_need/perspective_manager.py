"""Agent 主观视图管理器

管理 Agent 对外部世界的专业判断和洞察。
主观视图存储在外部世界的 .agent_perspectives/ 目录中。
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Observation:
    """单个观察记录"""
    timestamp: str
    category: str  # 如：code_quality, security, architecture
    severity: str  # 如：info, warning, critical
    content: str
    context: Optional[str] = None  # 相关文件或模块


@dataclass
class Insight:
    """结构化的洞察"""
    topic: str
    summary: str
    details: List[str]
    recommendations: List[str]
    last_updated: str


class PerspectiveManager:
    """管理 Agent 的主观视图"""
    
    def __init__(self, agent_name: str, agent_role: str, work_dir: Path):
        """
        Args:
            agent_name: Agent 的名称
            agent_role: Agent 的角色（如 code_reviewer, architect）
            work_dir: 外部世界目录
        """
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.work_dir = Path(work_dir)
        
        # 主观视图目录
        self.perspectives_dir = self.work_dir / ".agent_perspectives"
        self.perspectives_dir.mkdir(exist_ok=True)
        
        # 当前 Agent 的视图文件
        self.perspective_file = self.perspectives_dir / f"{agent_role}.md"
        self.data_file = self.perspectives_dir / f"{agent_role}_data.json"
        
        # 加载现有数据
        self.observations: List[Observation] = []
        self.insights: Dict[str, Insight] = {}
        self._load_data()
    
    def _load_data(self):
        """加载现有的观察和洞察数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 加载观察记录
                self.observations = [
                    Observation(**obs) for obs in data.get('observations', [])
                ]
                
                # 加载洞察
                for topic, insight_data in data.get('insights', {}).items():
                    self.insights[topic] = Insight(**insight_data)
                    
            except Exception as e:
                print(f"Warning: Failed to load perspective data: {e}")
    
    def _save_data(self):
        """保存观察和洞察数据"""
        data = {
            'observations': [asdict(obs) for obs in self.observations],
            'insights': {topic: asdict(insight) for topic, insight in self.insights.items()}
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_observation(self, category: str, content: str, 
                       severity: str = "info", context: Optional[str] = None):
        """添加新的观察
        
        Args:
            category: 观察类别
            content: 观察内容
            severity: 严重程度
            context: 上下文（如相关文件）
        """
        observation = Observation(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            category=category,
            severity=severity,
            content=content,
            context=context
        )
        
        self.observations.append(observation)
        
        # 保持观察记录在合理范围内（最新的100条）
        if len(self.observations) > 100:
            self.observations = self.observations[-100:]
        
        self._save_data()
        self._update_perspective_file()
    
    def update_insight(self, topic: str, summary: str, 
                      details: List[str], recommendations: List[str]):
        """更新或创建结构化洞察
        
        Args:
            topic: 洞察主题
            summary: 简要总结
            details: 详细说明
            recommendations: 建议措施
        """
        self.insights[topic] = Insight(
            topic=topic,
            summary=summary,
            details=details,
            recommendations=recommendations,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self._save_data()
        self._update_perspective_file()
    
    def _update_perspective_file(self):
        """更新 Markdown 格式的主观视图文件"""
        content = f"""# {self.agent_role.replace('_', ' ').title()} Perspective

**Agent**: {self.agent_name}  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 专业洞察

"""
        
        # 添加结构化洞察
        for topic, insight in sorted(self.insights.items()):
            content += f"""### {topic}

**概述**: {insight.summary}

**详细观察**:
"""
            for detail in insight.details:
                content += f"- {detail}\n"
            
            content += "\n**建议**:\n"
            for rec in insight.recommendations:
                content += f"1. {rec}\n"
            
            content += f"\n*更新于: {insight.last_updated}*\n\n"
        
        # 添加最近的观察（按类别分组）
        content += "## 最近观察\n\n"
        
        # 按类别分组观察
        observations_by_category = {}
        for obs in self.observations[-20:]:  # 最近20条
            if obs.category not in observations_by_category:
                observations_by_category[obs.category] = []
            observations_by_category[obs.category].append(obs)
        
        for category, obs_list in sorted(observations_by_category.items()):
            content += f"### {category.replace('_', ' ').title()}\n\n"
            for obs in obs_list:
                severity_icon = {
                    'info': 'ℹ️',
                    'warning': '⚠️',
                    'critical': '🔴'
                }.get(obs.severity, '•')
                
                content += f"{severity_icon} **[{obs.timestamp}]** {obs.content}"
                if obs.context:
                    content += f" *(Context: {obs.context})*"
                content += "\n"
            content += "\n"
        
        # 保存文件
        self.perspective_file.write_text(content, encoding='utf-8')
    
    def get_insights_for_topic(self, topic: str) -> Optional[Insight]:
        """获取特定主题的洞察"""
        return self.insights.get(topic)
    
    def get_recent_observations(self, category: Optional[str] = None, 
                               limit: int = 10) -> List[Observation]:
        """获取最近的观察记录
        
        Args:
            category: 筛选特定类别
            limit: 返回数量限制
        """
        observations = self.observations
        if category:
            observations = [obs for obs in observations if obs.category == category]
        
        return observations[-limit:]
    
    def query_perspectives(self, other_roles: List[str]) -> Dict[str, Any]:
        """查询其他 Agent 的视角
        
        Args:
            other_roles: 要查询的其他 Agent 角色列表
            
        Returns:
            其他 Agent 的洞察摘要
        """
        results = {}
        
        for role in other_roles:
            data_file = self.perspectives_dir / f"{role}_data.json"
            if data_file.exists():
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        results[role] = {
                            'insights': list(data.get('insights', {}).keys()),
                            'observation_count': len(data.get('observations', []))
                        }
                except Exception:
                    pass
        
        return results
    
    def generate_summary(self) -> str:
        """生成当前主观视图的摘要"""
        summary = f"## {self.agent_role} 视角摘要\n\n"
        
        # 洞察数量
        summary += f"- 结构化洞察: {len(self.insights)} 个主题\n"
        summary += f"- 观察记录: {len(self.observations)} 条\n\n"
        
        # 主要洞察
        if self.insights:
            summary += "### 主要洞察:\n"
            for topic, insight in list(self.insights.items())[:3]:
                summary += f"- **{topic}**: {insight.summary}\n"
        
        # 最近关注
        if self.observations:
            recent_categories = {}
            for obs in self.observations[-10:]:
                recent_categories[obs.category] = recent_categories.get(obs.category, 0) + 1
            
            summary += "\n### 最近关注:\n"
            for cat, count in sorted(recent_categories.items(), key=lambda x: x[1], reverse=True):
                summary += f"- {cat}: {count} 次观察\n"
        
        return summary


# 使用示例
if __name__ == "__main__":
    # 创建代码审查者的视角管理器
    pm = PerspectiveManager(
        agent_name="reviewer_001",
        agent_role="code_reviewer",
        work_dir=Path("./output/test_project")
    )
    
    # 添加观察
    pm.add_observation(
        category="code_quality",
        content="发现大量重复代码在 authentication 模块",
        severity="warning",
        context="src/auth/"
    )
    
    # 更新洞察
    pm.update_insight(
        topic="代码重复问题",
        summary="项目中存在显著的代码重复，影响可维护性",
        details=[
            "authentication 模块有3个几乎相同的验证函数",
            "错误处理逻辑在多处重复",
            "配置读取代码分散在各个模块"
        ],
        recommendations=[
            "提取通用验证逻辑到基类",
            "创建统一的错误处理中间件",
            "实现中心化的配置管理"
        ]
    )
    
    # 生成摘要
    print(pm.generate_summary())