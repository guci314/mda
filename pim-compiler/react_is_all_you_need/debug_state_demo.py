#!/usr/bin/env python3
"""演示调试器状态查看功能

展示触发断点时可以观察到的所有状态信息。
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from react_agent_debugger import (
    ReactAgentDebugger,
    StepType,
    StepBreakpoint,
    ToolBreakpoint,
    ConditionalBreakpoint,
    AgentBreakpoint
)


def demo_state_inspection():
    """演示状态查看功能"""
    print("=== 调试器状态查看演示 ===\n")
    
    # 创建一个配置了知识文件和记忆的 Agent
    config = ReactAgentConfig(
        work_dir="output/debug_state_demo",
        memory_level=MemoryLevel.SMART,  # 启用记忆系统
        knowledge_files=["knowledge/best_practices/absolute_path_usage.md"],  # 加载知识文件
        llm_model="deepseek-chat",
        llm_temperature=0,
        specification="演示调试器状态查看的测试 Agent"
    )
    
    agent = GenericReactAgent(config, name="state_demo_agent")
    
    # 创建调试器
    debugger = ReactAgentDebugger(agent)
    debugger.verbose = True  # 开启详细输出
    
    # 设置多种类型的断点来展示不同状态
    print("设置断点：")
    print("1. THINK 步骤断点 - 查看 AI 思考状态")
    print("2. ACT 步骤断点 - 查看工具调用状态")
    print("3. OBSERVE 步骤断点 - 查看结果观察状态")
    print("4. 条件断点 - 当创建文件时触发\n")
    
    # 添加断点
    debugger.add_breakpoint(StepBreakpoint(id="bp_think", step_type=StepType.THINK))
    debugger.add_breakpoint(StepBreakpoint(id="bp_act", step_type=StepType.ACT))
    debugger.add_breakpoint(StepBreakpoint(id="bp_observe", step_type=StepType.OBSERVE))
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_file_create",
            condition=lambda ctx: any("write_file" in str(tc) for tc in ctx.get("tool_calls", [])),
            condition_str="创建文件操作"
        )
    )
    
    print("执行任务：创建测试文件并读取")
    print("=" * 80)
    print("在每个断点处，使用 'p' 命令查看完整状态信息")
    print("=" * 80)
    print()
    
    # 执行任务
    debugger.execute_task("""
请完成以下任务：
1. 创建一个 test_state.txt 文件，内容包含当前时间
2. 读取刚创建的文件并显示内容
3. 列出工作目录中的所有文件
""")
    
    print("\n✅ 状态查看演示完成")


def demo_detailed_state_analysis():
    """深入分析特定状态"""
    print("\n\n=== 详细状态分析演示 ===\n")
    
    # 创建包含自定义工具的 Agent
    from tools import create_tools
    
    config = ReactAgentConfig(
        work_dir="output/debug_state_analysis",
        memory_level=MemoryLevel.PRO,  # 使用专业级记忆
        llm_model="deepseek-chat",
        llm_temperature=0
    )
    
    # 创建自定义工具
    tools = create_tools(config.work_dir)
    
    agent = GenericReactAgent(
        config,
        name="analysis_agent",
        custom_tools=tools
    )
    
    # 创建调试器
    debugger = ReactAgentDebugger(agent)
    
    # 添加一个条件断点，在执行到第5步时暂停
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_step5",
            condition=lambda ctx: len(debugger.execution_history) == 5,
            condition_str="执行到第5步"
        )
    )
    
    print("任务：执行多步骤操作，在第5步时分析状态")
    print()
    
    # 执行任务
    debugger.execute_task("""
创建一个简单的 Python 项目：
1. 创建 main.py 文件
2. 创建 utils.py 文件  
3. 创建 README.md 文件
4. 运行 ls 命令查看文件
5. 读取 README.md 内容
""")


def print_observable_states():
    """打印可观察状态的文档"""
    print("\n" + "="*80)
    print("📋 调试器可观察状态总览")
    print("="*80)
    
    states = {
        "🎯 执行状态": [
            "当前步骤类型 (THINK/ACT/OBSERVE)",
            "调用深度（子 Agent 嵌套层级）",
            "执行历史长度",
            "当前调试模式"
        ],
        "💬 当前消息": [
            "消息类型（Human/AI/Tool/System）",
            "消息内容（支持截断显示）",
            "工具调用信息",
            "工具返回结果"
        ],
        "📜 消息历史": [
            "所有历史消息",
            "消息总数统计",
            "最近N条消息预览"
        ],
        "🔧 工具调用详情": [
            "工具名称",
            "调用参数（键值对）",
            "工具类型（普通工具/子Agent）",
            "多个工具调用的顺序"
        ],
        "🤖 Agent 信息": [
            "Agent 名称",
            "工作目录路径",
            "记忆级别设置",
            "使用的 LLM 模型"
        ],
        "📚 调用栈": [
            "子 Agent 调用层级",
            "当前执行位置",
            "嵌套深度"
        ],
        "🔴 断点信息": [
            "活跃断点列表",
            "断点类型和条件",
            "断点命中次数"
        ],
        "📈 执行统计": [
            "各类步骤执行次数",
            "THINK/ACT/OBSERVE 分布",
            "总执行步数"
        ],
        "💾 系统状态": [
            "知识文件加载状态",
            "记忆系统状态",
            "工作目录内容"
        ]
    }
    
    for category, items in states.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    # 确保输出目录存在
    Path("output/debug_state_demo").mkdir(parents=True, exist_ok=True)
    Path("output/debug_state_analysis").mkdir(parents=True, exist_ok=True)
    
    print("🔍 ReactAgentDebugger 状态查看演示")
    print("="*80)
    print("这个演示展示了触发断点时可以观察到的所有状态信息")
    print("="*80)
    
    # 首先展示状态总览
    print_observable_states()
    
    input("\n按回车键开始状态查看演示...")
    
    # 运行主演示
    demo_state_inspection()
    
    # 可选：运行详细分析
    choice = input("\n是否运行详细状态分析演示？(y/n): ")
    if choice.lower() == 'y':
        demo_detailed_state_analysis()