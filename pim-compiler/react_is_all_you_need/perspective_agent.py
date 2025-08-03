"""支持主观视图的 Agent 基类

提供主观视图功能的便捷封装。
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from react_agent import GenericReactAgent, ReactAgentConfig
from perspective_manager import PerspectiveManager

logger = logging.getLogger(__name__)


class PerspectiveAgent(GenericReactAgent):
    """具有主观视图能力的 Agent
    
    在 GenericReactAgent 基础上添加主观视图管理功能。
    只有在配置中启用 enable_perspective=True 时才会激活。
    """
    
    def __init__(self, config: ReactAgentConfig, name: str, role: str):
        """
        Args:
            config: Agent 配置（需要 enable_perspective=True）
            name: Agent 名称
            role: Agent 角色（如 code_reviewer, security_auditor）
        """
        super().__init__(config, name)
        self.role = role
        self.perspective_manager: Optional[PerspectiveManager] = None
        
        # 如果启用了主观视图，初始化管理器
        if config.enable_perspective:
            self.perspective_manager = PerspectiveManager(
                agent_name=name,
                agent_role=role,
                work_dir=self.work_dir
            )
            if os.environ.get('DEBUG'):
                logger.info(f"[{name}] Perspective view enabled for role: {role}")
    
    def record_observation(self, category: str, content: str, 
                          severity: str = "info", context: Optional[str] = None):
        """记录观察（仅在启用主观视图时有效）
        
        Args:
            category: 观察类别
            content: 观察内容
            severity: 严重程度（info/warning/critical）
            context: 上下文信息
        """
        if self.perspective_manager:
            self.perspective_manager.add_observation(
                category=category,
                content=content,
                severity=severity,
                context=context
            )
    
    def update_insight(self, topic: str, summary: str,
                      details: List[str], recommendations: List[str]):
        """更新洞察（仅在启用主观视图时有效）
        
        Args:
            topic: 洞察主题
            summary: 简要总结
            details: 详细说明列表
            recommendations: 建议列表
        """
        if self.perspective_manager:
            self.perspective_manager.update_insight(
                topic=topic,
                summary=summary,
                details=details,
                recommendations=recommendations
            )
    
    def query_other_perspectives(self, roles: List[str]) -> Dict[str, Any]:
        """查询其他角色的视角
        
        Args:
            roles: 要查询的角色列表
            
        Returns:
            其他角色的洞察摘要
        """
        if self.perspective_manager:
            return self.perspective_manager.query_perspectives(roles)
        return {}
    
    def get_perspective_summary(self) -> str:
        """获取当前视角摘要"""
        if self.perspective_manager:
            return self.perspective_manager.generate_summary()
        return "主观视图功能未启用"
    
    def _create_agent(self):
        """重写创建 Agent 方法，注入主观视图相关知识"""
        # 如果启用了主观视图，添加相关知识
        if self.config.enable_perspective and self.perspective_manager:
            # 添加视角相关的提示
            perspective_prompt = f"""
## 主观视图记录

你的角色是 {self.role}，在执行任务时请记录专业观察和洞察。

使用以下 Python 代码记录观察：
```python
# 这些函数已经为你准备好，直接调用即可
record_observation(
    category="{self._get_default_category()}",  # 使用你的专业类别
    content="观察内容",
    severity="info/warning/critical",
    context="相关文件或位置"
)

# 总结重要洞察
update_insight(
    topic="主题",
    summary="简要总结",
    details=["详细观察1", "详细观察2"],
    recommendations=["建议1", "建议2"]
)
```

请在工作中主动记录有价值的发现。
"""
            # 将主观视图提示添加到知识中
            if hasattr(self, 'prior_knowledge') and self.prior_knowledge:
                self.prior_knowledge += "\n" + perspective_prompt
            else:
                self.prior_knowledge = perspective_prompt
        
        # 调用父类方法创建 agent
        return super()._create_agent()
    
    def _get_default_category(self) -> str:
        """根据角色返回默认的观察类别"""
        category_map = {
            "code_reviewer": "code_quality",
            "security_auditor": "security_vulnerability",
            "performance_optimizer": "performance_bottleneck",
            "software_architect": "architecture_pattern",
            "devops_engineer": "deployment"
        }
        return category_map.get(self.role, "general")
    
    def execute_task(self, task: str) -> None:
        """执行任务（带主观视图支持）"""
        # 在任务开始时，可以查看其他视角
        if self.perspective_manager:
            print(f"\n[{self.name}] 检查其他 Agent 的视角...")
            other_views = self.query_other_perspectives(
                ["code_reviewer", "security_auditor", "software_architect"]
            )
            if other_views:
                print(f"[{self.name}] 发现相关视角: {list(other_views.keys())}")
        
        # 执行任务
        super().execute_task(task)
        
        # 任务完成后的处理
        if self.perspective_manager:
            print(f"\n[{self.name}] 主观视图已更新: {self.perspective_manager.perspective_file}")


# 便捷工厂函数
def create_code_reviewer(work_dir: str, name: str = "code_reviewer_001",
                        enable_perspective: bool = True) -> PerspectiveAgent:
    """创建代码审查者 Agent"""
    config = ReactAgentConfig(
        work_dir=work_dir,
        enable_perspective=enable_perspective,
        knowledge_files=[
            "knowledge/system_prompt.md",
            "knowledge/python_programming_knowledge.md",
            "knowledge/perspective_templates.md"
        ],
        specification="专业的代码审查者，关注代码质量、可维护性和最佳实践。"
    )
    return PerspectiveAgent(config, name, "code_reviewer")


def create_security_auditor(work_dir: str, name: str = "security_auditor_001",
                           enable_perspective: bool = True) -> PerspectiveAgent:
    """创建安全审计者 Agent"""
    config = ReactAgentConfig(
        work_dir=work_dir,
        enable_perspective=enable_perspective,
        knowledge_files=[
            "knowledge/system_prompt.md",
            "knowledge/perspective_templates.md"
        ],
        specification="安全审计专家，识别安全漏洞和风险。"
    )
    return PerspectiveAgent(config, name, "security_auditor")


def create_architect(work_dir: str, name: str = "architect_001",
                    enable_perspective: bool = True) -> PerspectiveAgent:
    """创建软件架构师 Agent"""
    config = ReactAgentConfig(
        work_dir=work_dir,
        enable_perspective=enable_perspective,
        knowledge_files=[
            "knowledge/system_prompt.md",
            "knowledge/perspective_templates.md"
        ],
        specification="软件架构师，关注系统设计、模块化和技术决策。"
    )
    return PerspectiveAgent(config, name, "software_architect")


# 使用示例
if __name__ == "__main__":
    import os
    
    # 创建一个启用主观视图的代码审查者
    reviewer = create_code_reviewer(
        work_dir="./output/test_project",
        enable_perspective=True  # 启用主观视图
    )
    
    # 执行代码审查任务
    reviewer.execute_task("请审查项目的代码质量并记录你的发现。")
    
    # 查看生成的主观视图摘要
    print("\n" + reviewer.get_perspective_summary())