#!/usr/bin/env python3
"""演示增强版调试器的视图更新步骤

展示如何调试 world_overview.md 生成和主观视图更新。
"""

import os
import shutil
from pathlib import Path
from core.react_agent import ReactAgentConfig, MemoryLevel
from perspective_agent import PerspectiveAgent
from react_agent_debugger_enhanced import EnhancedReactAgentDebugger, StepType
from react_agent_debugger import StepBreakpoint, ConditionalBreakpoint


def demo_world_view_debugging():
    """演示客观视图生成的调试"""
    print("\n" + "=" * 70)
    print("客观视图（world_overview.md）调试演示")
    print("=" * 70)
    
    # 创建干净的测试目录
    test_dir = Path("output/debug_world_view")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    
    # 添加一些测试文件
    (test_dir / "README.md").write_text("# Test Project\n\nA demo project.")
    (test_dir / "main.py").write_text("def main():\n    print('Hello')")
    
    print(f"\n测试目录: {test_dir}")
    print("目录中没有 world_overview.md，Agent 应该会生成它")
    
    # 创建配置
    config = ReactAgentConfig(
        work_dir=str(test_dir),
        memory_level=MemoryLevel.NONE,
        enable_world_overview=True,  # 确保启用
        knowledge_files=[
            "knowledge/core/system_prompt.md",
            "knowledge/core/world_overview_generation.md"
        ]
    )
    
    # 创建 Agent
    agent = PerspectiveAgent(config, name="debugger_demo", role="code_reviewer")
    
    # 创建增强调试器
    debugger = EnhancedReactAgentDebugger(agent)
    
    # 添加客观视图更新断点
    print("\n设置断点：在生成 world_overview.md 时暂停")
    world_view_bp = StepBreakpoint(step_type=StepType.UPDATE_WORLD_VIEW)
    debugger.add_breakpoint(world_view_bp)
    
    # 执行任务
    print("\n开始调试...")
    debugger.execute_task("分析当前目录结构")


def demo_perspective_debugging():
    """演示主观视图更新的调试"""
    print("\n" + "=" * 70)
    print("主观视图（.agent_perspectives/）调试演示")
    print("=" * 70)
    
    # 使用当前项目目录
    work_dir = Path(__file__).parent
    
    # 创建配置（启用主观视图）
    config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        enable_world_overview=False,  # 关闭以专注于主观视图
        enable_perspective=True,      # 启用主观视图
        knowledge_files=[
            "knowledge/core/system_prompt.md",
            "knowledge/output/perspective_templates.md"
        ]
    )
    
    # 创建代码审查者
    agent = PerspectiveAgent(config, name="reviewer_debug", role="code_reviewer")
    
    # 创建增强调试器
    debugger = EnhancedReactAgentDebugger(agent)
    
    # 添加主观视图更新断点
    print("\n设置断点：")
    print("1. 在记录观察时暂停")
    print("2. 在更新洞察时暂停")
    
    perspective_bp = StepBreakpoint(step_type=StepType.UPDATE_PERSPECTIVE)
    debugger.add_breakpoint(perspective_bp)
    
    # 添加条件断点：只在严重级别为 warning 或 critical 时暂停
    conditional_bp = ConditionalBreakpoint(
        condition=lambda state: (
            state.get('execution_history', []) and
            state['execution_history'][-1].step_type == StepType.UPDATE_PERSPECTIVE and
            state['execution_history'][-1].data.get('severity') in ['warning', 'critical']
        ),
        description="严重观察断点"
    )
    debugger.add_breakpoint(conditional_bp)
    
    # 执行任务
    print("\n开始调试...")
    debugger.execute_task("""请审查 perspective_manager.py 文件，记录你的观察：
1. 使用 record_observation 记录至少 2 个不同严重级别的观察
2. 使用 update_insight 总结一个关于代码质量的洞察

示例代码：
```python
# 记录一般观察
record_observation(
    category="code_quality",
    content="类设计合理，职责清晰",
    severity="info",
    context="perspective_manager.py"
)

# 记录警告
record_observation(
    category="code_quality", 
    content="某些方法过长，建议拆分",
    severity="warning",
    context="perspective_manager.py:100-150"
)

# 更新洞察
update_insight(
    topic="整体代码质量",
    summary="代码结构良好但存在改进空间",
    details=["类设计合理", "部分方法过长", "文档完整"],
    recommendations=["拆分长方法", "添加类型注解"]
)
```""")


def demo_combined_debugging():
    """演示同时调试两种视图"""
    print("\n" + "=" * 70)
    print("组合调试演示（客观 + 主观视图）")
    print("=" * 70)
    
    # 创建新的测试目录
    test_dir = Path("output/debug_combined")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    
    # 创建项目结构
    (test_dir / "src").mkdir()
    (test_dir / "src" / "__init__.py").write_text("")
    (test_dir / "src" / "main.py").write_text("""
def calculate_sum(numbers):
    total = 0
    for n in numbers:
        total = total + n  # 可以用 sum() 函数
    return total

def process_data(data):
    # TODO: 添加错误处理
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
""")
    
    # 创建配置（两个视图都启用）
    config = ReactAgentConfig(
        work_dir=str(test_dir),
        memory_level=MemoryLevel.SMART,
        enable_world_overview=True,
        enable_perspective=True,
        knowledge_files=[
            "knowledge/core/system_prompt.md",
            "knowledge/programming/python_programming_knowledge.md",
            "knowledge/output/perspective_templates.md",
            "knowledge/core/world_overview_generation.md"
        ]
    )
    
    # 创建代码审查者
    agent = PerspectiveAgent(config, name="full_debug", role="code_reviewer")
    
    # 创建增强调试器
    debugger = EnhancedReactAgentDebugger(agent)
    
    # 添加所有视图相关断点
    print("\n设置断点：")
    print("1. UPDATE_WORLD_VIEW - 生成客观视图时")
    print("2. UPDATE_PERSPECTIVE - 更新主观视图时")
    
    debugger.add_breakpoint(StepBreakpoint(step_type=StepType.UPDATE_WORLD_VIEW))
    debugger.add_breakpoint(StepBreakpoint(step_type=StepType.UPDATE_PERSPECTIVE))
    
    # 执行复杂任务
    print("\n开始调试...")
    debugger.execute_task("""请完成以下任务：
1. 首先分析项目结构（这会触发 world_overview.md 生成）
2. 然后审查 src/main.py 的代码质量
3. 记录你发现的问题和改进建议
4. 最后总结一个关于项目代码质量的洞察""")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        demo = sys.argv[1]
        
        if demo == "world":
            demo_world_view_debugging()
        elif demo == "perspective":
            demo_perspective_debugging()
        elif demo == "combined":
            demo_combined_debugging()
        else:
            print(f"未知的演示: {demo}")
    else:
        print("""增强版调试器演示 - 支持视图更新步骤

使用方法：
  python demo_debugger_enhanced.py world        # 调试客观视图生成
  python demo_debugger_enhanced.py perspective  # 调试主观视图更新
  python demo_debugger_enhanced.py combined     # 组合调试演示

新增的原子步骤：
- UPDATE_WORLD_VIEW: 生成或更新 world_overview.md
- UPDATE_PERSPECTIVE: 记录观察或更新洞察

调试命令：
- c/continue: 继续执行
- s/step: 单步执行
- b <type>: 添加步骤断点（如 b UPDATE_WORLD_VIEW）
- bl: 列出所有断点
- ? : 显示帮助
""")


if __name__ == "__main__":
    # 可选：启用调试输出
    # os.environ['DEBUG'] = '1'
    
    main()