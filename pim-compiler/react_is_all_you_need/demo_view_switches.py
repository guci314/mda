#!/usr/bin/env python3
"""演示视图功能开关的使用

展示如何控制 world_overview.md 和主观视图功能的启用/禁用。
"""

import os
import shutil
from pathlib import Path
from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from perspective_agent import PerspectiveAgent


def demo_world_overview_switch():
    """演示 world_overview.md 开关"""
    print("\n" + "=" * 70)
    print("World Overview 开关演示")
    print("=" * 70)
    
    # 创建测试目录
    test_dir = Path("output/test_overview_switch")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    
    # 创建一些文件
    (test_dir / "app.py").write_text("print('Hello World')")
    
    print(f"\n测试目录: {test_dir}")
    
    # 1. 禁用 world_overview
    print("\n### 1. 禁用 world_overview.md 检查")
    config1 = ReactAgentConfig(
        work_dir=str(test_dir),
        memory_level=MemoryLevel.NONE,
        enable_world_overview=False  # 禁用
    )
    
    agent1 = GenericReactAgent(config1, name="agent_no_overview")
    print(f"- Agent 创建完成")
    print(f"- _pending_overview_task: {agent1._pending_overview_task}")
    print(f"- world_overview.md 存在: {(test_dir / 'world_overview.md').exists()}")
    
    # 2. 启用 world_overview（默认）
    print("\n### 2. 启用 world_overview.md 检查（默认）")
    config2 = ReactAgentConfig(
        work_dir=str(test_dir),
        memory_level=MemoryLevel.NONE,
        enable_world_overview=True  # 启用（默认值）
    )
    
    agent2 = GenericReactAgent(config2, name="agent_with_overview")
    print(f"- Agent 创建完成")
    print(f"- _pending_overview_task 存在: {agent2._pending_overview_task is not None}")
    
    # 执行任务以触发生成
    if agent2._pending_overview_task:
        print("\n执行任务以生成 world_overview.md...")
        agent2.execute_task("列出当前目录的文件")
        print(f"- world_overview.md 已生成: {(test_dir / 'world_overview.md').exists()}")


def demo_perspective_switch():
    """演示主观视图开关"""
    print("\n" + "=" * 70)
    print("主观视图开关演示")
    print("=" * 70)
    
    # 使用当前项目目录
    work_dir = Path(__file__).parent
    
    # 1. 禁用主观视图（默认）
    print("\n### 1. 禁用主观视图（默认）")
    config1 = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        enable_perspective=False  # 禁用（默认值）
    )
    
    agent1 = PerspectiveAgent(config1, name="reviewer_no_perspective", role="code_reviewer")
    print(f"- Agent 创建完成")
    print(f"- perspective_manager: {agent1.perspective_manager}")
    
    # 尝试记录观察（不会有效果）
    agent1.record_observation(
        category="code_quality",
        content="测试观察",
        severity="info"
    )
    print("- 尝试记录观察（由于禁用，不会有效果）")
    
    # 2. 启用主观视图
    print("\n### 2. 启用主观视图")
    config2 = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        enable_perspective=True  # 启用
    )
    
    agent2 = PerspectiveAgent(config2, name="reviewer_with_perspective", role="code_reviewer")
    print(f"- Agent 创建完成")
    print(f"- perspective_manager 已初始化: {agent2.perspective_manager is not None}")
    print(f"- 视图文件路径: {agent2.perspective_manager.perspective_file if agent2.perspective_manager else 'N/A'}")
    
    # 记录观察
    agent2.record_observation(
        category="code_quality",
        content="发现代码重复问题",
        severity="warning",
        context="demo_*.py"
    )
    print("- 成功记录观察")
    
    # 查看摘要
    print("\n视角摘要:")
    print(agent2.get_perspective_summary())


def demo_combined_switches():
    """演示组合使用两个开关"""
    print("\n" + "=" * 70)
    print("组合开关演示")
    print("=" * 70)
    
    test_dir = Path("output/test_combined")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    
    # 创建配置：两个功能都启用
    config = ReactAgentConfig(
        work_dir=str(test_dir),
        memory_level=MemoryLevel.SMART,
        enable_world_overview=True,    # 启用客观视图
        enable_perspective=True,        # 启用主观视图
        knowledge_files=[
            "knowledge/core/system_prompt.md",
            "knowledge/output/perspective_templates.md"
        ]
    )
    
    # 创建架构师 Agent
    architect = PerspectiveAgent(config, name="architect_full", role="software_architect")
    
    print(f"\n配置状态:")
    print(f"- enable_world_overview: {config.enable_world_overview}")
    print(f"- enable_perspective: {config.enable_perspective}")
    print(f"- 工作目录: {test_dir}")
    
    # 执行任务
    print("\n执行架构分析任务...")
    architect.execute_task("""分析当前目录的架构，记录你的专业观察。
如果需要生成 world_overview.md，请先完成。
然后从架构角度评估项目结构。""")
    
    # 检查结果
    print(f"\n生成的文件:")
    if (test_dir / "world_overview.md").exists():
        print(f"✓ world_overview.md（客观视图）")
    
    perspectives_dir = test_dir / ".agent_perspectives"
    if perspectives_dir.exists():
        for file in perspectives_dir.glob("*.md"):
            print(f"✓ {file.relative_to(test_dir)}（主观视图）")


def show_configuration_examples():
    """展示各种配置示例"""
    print("\n" + "=" * 70)
    print("配置示例")
    print("=" * 70)
    
    print("""
# 1. 最小配置（两个视图都禁用）
config = ReactAgentConfig(
    work_dir="./workspace",
    enable_world_overview=False,
    enable_perspective=False
)

# 2. 只启用客观视图（默认）
config = ReactAgentConfig(
    work_dir="./workspace"
    # enable_world_overview=True  # 默认值
    # enable_perspective=False     # 默认值
)

# 3. 只启用主观视图
config = ReactAgentConfig(
    work_dir="./workspace",
    enable_world_overview=False,
    enable_perspective=True
)

# 4. 完整功能（推荐用于专业 Agent）
config = ReactAgentConfig(
    work_dir="./workspace",
    enable_world_overview=True,
    enable_perspective=True,
    memory_level=MemoryLevel.SMART
)

# 5. 环境变量控制
os.environ['ENABLE_WORLD_OVERVIEW'] = 'false'
os.environ['ENABLE_PERSPECTIVE'] = 'true'

config = ReactAgentConfig(
    work_dir="./workspace",
    enable_world_overview=os.environ.get('ENABLE_WORLD_OVERVIEW', 'true').lower() == 'true',
    enable_perspective=os.environ.get('ENABLE_PERSPECTIVE', 'false').lower() == 'true'
)
""")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        demo = sys.argv[1]
        
        if demo == "overview":
            demo_world_overview_switch()
        elif demo == "perspective":
            demo_perspective_switch()
        elif demo == "combined":
            demo_combined_switches()
        elif demo == "config":
            show_configuration_examples()
        else:
            print(f"未知的演示: {demo}")
    else:
        print("""视图功能开关演示

使用方法：
  python demo_view_switches.py overview     # World Overview 开关演示
  python demo_view_switches.py perspective  # 主观视图开关演示
  python demo_view_switches.py combined     # 组合使用演示
  python demo_view_switches.py config       # 查看配置示例

开关说明：
- enable_world_overview: 控制是否自动生成/更新 world_overview.md（默认启用）
- enable_perspective: 控制是否记录主观视图到 .agent_perspectives/（默认禁用）
""")


if __name__ == "__main__":
    # 清理输出目录
    output_dir = Path("output")
    if output_dir.exists():
        for test_dir in output_dir.glob("test_*"):
            if test_dir.is_dir():
                shutil.rmtree(test_dir)
    
    main()