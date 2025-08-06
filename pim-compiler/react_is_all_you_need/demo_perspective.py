#!/usr/bin/env python3
"""演示 Agent 主观视图功能

展示不同角色的 Agent 如何记录和使用主观视图。
"""

import os
from pathlib import Path
from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from perspective_manager import PerspectiveManager
from typing import Optional


class PerspectiveAwareAgent(GenericReactAgent):
    """具有主观视图能力的 Agent"""
    
    def __init__(self, config: ReactAgentConfig, name: str, role: str):
        super().__init__(config, name)
        self.role = role
        self.perspective_manager: Optional[PerspectiveManager] = None
    
    def execute_task(self, task: str) -> None:
        """执行任务并记录主观视图"""
        # 初始化主观视图管理器
        self.perspective_manager = PerspectiveManager(
            agent_name=self.name,
            agent_role=self.role,
            work_dir=self.work_dir
        )
        
        # 执行原始任务
        super().execute_task(task)
        
        # 任务完成后可以总结洞察
        print(f"\n[{self.name}] 主观视图已更新到: {self.perspective_manager.perspective_file}")


def demo_code_reviewer():
    """演示代码审查者的主观视图"""
    print("\n" + "=" * 70)
    print("代码审查者视角演示")
    print("=" * 70)
    
    # 使用当前项目作为示例
    work_dir = Path(__file__).parent
    
    config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.SMART,
        knowledge_files=[
            "knowledge/core/system_prompt.md",
            "knowledge/programming/python_programming_knowledge.md",
            "knowledge/output/perspective_templates.md"
        ],
        specification="""你是一个专业的代码审查者，负责：
1. 评估代码质量
2. 发现潜在问题
3. 提出改进建议

在工作中，请使用 PerspectiveManager 记录你的专业观察和洞察。"""
    )
    
    agent = PerspectiveAwareAgent(config, name="reviewer_001", role="code_reviewer")
    
    # 让代码审查者分析项目
    agent.execute_task("""请审查当前项目的代码质量，特别关注：
1. 代码复杂度和可读性
2. 潜在的代码异味
3. 测试覆盖情况
4. 文档完整性

使用以下代码记录你的观察：
```python
from perspective_manager import PerspectiveManager

pm = PerspectiveManager(
    agent_name="reviewer_001",
    agent_role="code_reviewer", 
    work_dir="."
)

# 记录观察
pm.add_observation(
    category="code_quality",
    content="你的观察内容",
    severity="info/warning/critical",
    context="相关文件路径"
)

# 总结洞察
pm.update_insight(
    topic="总体评估",
    summary="简要总结",
    details=["详细发现1", "详细发现2"],
    recommendations=["建议1", "建议2"]
)
```

请确保记录至少3个观察和1个结构化洞察。""")


def demo_security_auditor():
    """演示安全审计者的主观视图"""
    print("\n" + "=" * 70)
    print("安全审计者视角演示")
    print("=" * 70)
    
    work_dir = Path(__file__).parent
    
    config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.SMART,
        knowledge_files=[
            "knowledge/core/system_prompt.md",
            "knowledge/programming/python_programming_knowledge.md",
            "knowledge/output/perspective_templates.md"
        ],
        specification="""你是一个安全审计专家，负责：
1. 识别安全漏洞
2. 评估安全风险
3. 提出安全加固建议

在工作中，请使用 PerspectiveManager 记录安全相关的发现。"""
    )
    
    agent = PerspectiveAwareAgent(config, name="auditor_001", role="security_auditor")
    
    agent.execute_task("""请对当前项目进行安全审计，重点检查：
1. API密钥和敏感信息管理
2. 输入验证和注入风险
3. 认证和授权机制
4. 依赖库的安全性

使用 PerspectiveManager 记录所有安全相关的发现，
特别是任何 severity="critical" 的问题。""")


def demo_cross_perspective():
    """演示跨视角协作"""
    print("\n" + "=" * 70)
    print("跨视角协作演示")
    print("=" * 70)
    
    work_dir = Path(__file__).parent
    perspectives_dir = work_dir / ".agent_perspectives"
    
    if perspectives_dir.exists():
        print("\n已有的 Agent 视角：")
        for file in perspectives_dir.glob("*.md"):
            if not file.name.endswith("_data.json"):
                print(f"- {file.stem}")
        
        # 创建一个架构师 Agent 来综合其他视角
        config = ReactAgentConfig(
            work_dir=str(work_dir),
            memory_level=MemoryLevel.SMART,
            knowledge_files=[
                "knowledge/core/system_prompt.md",
                "knowledge/output/perspective_templates.md"
            ]
        )
        
        agent = PerspectiveAwareAgent(config, name="architect_001", role="software_architect")
        
        agent.execute_task("""作为软件架构师，请：
1. 查看 .agent_perspectives/ 目录中其他 Agent 的视角
2. 综合代码审查者和安全审计者的发现
3. 从架构角度提出整体改进方案

使用 PerspectiveManager 的 query_perspectives 方法查看其他视角：
```python
pm = PerspectiveManager(...)
other_views = pm.query_perspectives(["code_reviewer", "security_auditor"])
```

基于综合分析，创建架构层面的洞察。""")
    else:
        print("还没有其他 Agent 的视角，请先运行 code_reviewer 和 security_auditor 演示。")


def show_perspectives():
    """显示所有主观视图"""
    print("\n" + "=" * 70)
    print("当前项目的所有主观视图")
    print("=" * 70)
    
    work_dir = Path(__file__).parent
    perspectives_dir = work_dir / ".agent_perspectives"
    
    if perspectives_dir.exists():
        for md_file in sorted(perspectives_dir.glob("*.md")):
            if not md_file.name.endswith("_data.json"):
                print(f"\n### {md_file.name}")
                print("-" * 50)
                content = md_file.read_text()
                # 只显示前 500 字符
                preview = content[:500] + "..." if len(content) > 500 else content
                print(preview)
    else:
        print("还没有任何主观视图。")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        demo_type = sys.argv[1]
        
        if demo_type == "reviewer":
            demo_code_reviewer()
        elif demo_type == "auditor":
            demo_security_auditor()
        elif demo_type == "cross":
            demo_cross_perspective()
        elif demo_type == "show":
            show_perspectives()
        else:
            print(f"未知的演示类型: {demo_type}")
    else:
        print("""Agent 主观视图演示

使用方法：
  python demo_perspective.py reviewer  # 运行代码审查者演示
  python demo_perspective.py auditor   # 运行安全审计者演示  
  python demo_perspective.py cross     # 运行跨视角协作演示
  python demo_perspective.py show      # 显示所有主观视图

建议按顺序运行：
1. 先运行 reviewer 和 auditor 建立基础视角
2. 再运行 cross 查看协作效果
3. 最后运行 show 查看所有生成的视角
""")


if __name__ == "__main__":
    # 可选：启用调试模式
    # os.environ['DEBUG'] = '1'
    
    main()