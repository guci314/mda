#!/usr/bin/env python3
"""ReactAgentDebugger 使用示例

演示如何使用调试器调试 GenericReactAgent 的执行流程。
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from react_agent_debugger import (
    ReactAgentDebugger, 
    StepType, 
    StepBreakpoint, 
    ToolBreakpoint, 
    ConditionalBreakpoint
)


def demo_basic_debugging():
    """基础调试示例"""
    print("=== 基础调试示例 ===\n")
    
    # 创建一个简单的 agent
    config = ReactAgentConfig(
        work_dir="output/debug_demo",
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat",
        llm_temperature=0
    )
    
    agent = GenericReactAgent(config, name="debug_agent")
    
    # 创建调试器
    debugger = ReactAgentDebugger(agent)
    
    # 设置断点：在每个 THINK 步骤暂停
    debugger.add_breakpoint(StepBreakpoint(id="bp1", step_type=StepType.THINK))
    
    # 执行简单任务
    print("执行任务：创建一个简单的 hello.txt 文件")
    print("提示：输入 'c' 继续执行，'p' 查看状态，'?' 查看帮助\n")
    
    debugger.execute_task("创建一个 hello.txt 文件，内容为 'Hello, World!'")


def demo_tool_breakpoints():
    """工具断点示例"""
    print("\n=== 工具断点示例 ===\n")
    
    # 创建 agent
    config = ReactAgentConfig(
        work_dir="output/debug_demo",
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat",
        llm_temperature=0
    )
    
    agent = GenericReactAgent(config, name="tool_debug_agent")
    
    # 创建调试器
    debugger = ReactAgentDebugger(agent)
    
    # 设置工具断点：在调用 write_file 时暂停
    debugger.add_breakpoint(ToolBreakpoint(id="bp_write", tool_name="write_file"))
    debugger.add_breakpoint(ToolBreakpoint(id="bp_exec", tool_name="execute_command"))
    
    # 执行任务
    print("执行任务：创建并运行一个 Python 脚本")
    print("断点设置：write_file 和 execute_command 工具调用\n")
    
    debugger.execute_task("""
创建一个 test.py 文件，内容为：
```python
print("Hello from Python!")
print("2 + 2 =", 2 + 2)
```
然后运行这个文件
""")


def demo_conditional_breakpoints():
    """条件断点示例"""
    print("\n=== 条件断点示例 ===\n")
    
    # 创建 agent
    config = ReactAgentConfig(
        work_dir="output/debug_demo",  
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat",
        llm_temperature=0
    )
    
    agent = GenericReactAgent(config, name="conditional_debug_agent")
    
    # 创建调试器
    debugger = ReactAgentDebugger(agent)
    
    # 设置条件断点：当消息包含特定关键词时暂停
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_error",
            condition=lambda ctx: "error" in str(ctx.get("last_message", "")).lower(),
            condition_str="消息包含 'error'"
        )
    )
    
    # 设置条件断点：当执行深度大于 1 时暂停（嵌套工具调用）
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_deep",
            condition=lambda ctx: ctx.get("depth", 0) > 1,
            condition_str="调用深度 > 1"
        )
    )
    
    # 执行一个可能出错的任务
    print("执行任务：尝试读取不存在的文件")
    print("断点设置：消息包含 'error' 或调用深度 > 1\n")
    
    debugger.execute_task("""
1. 尝试读取 nonexistent.txt 文件
2. 如果失败，创建这个文件，内容为 "File created after error"
3. 再次读取文件确认创建成功
""")


def demo_step_modes():
    """步进模式示例"""
    print("\n=== 步进模式示例 ===\n")
    
    # 创建 agent
    config = ReactAgentConfig(
        work_dir="output/debug_demo",
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat",
        llm_temperature=0,
        knowledge_files=["knowledge/best_practices/absolute_path_usage.md"]  # 加载知识文件
    )
    
    agent = GenericReactAgent(config, name="step_debug_agent")
    
    # 创建调试器
    debugger = ReactAgentDebugger(agent)
    
    # 设置详细输出
    debugger.verbose = True
    
    # 设置初始断点
    debugger.add_breakpoint(StepBreakpoint(id="bp_first_think", step_type=StepType.THINK))
    
    print("执行任务：创建目录结构和多个文件")
    print("演示不同的步进模式：")
    print("  - step (s): 执行一个原子步骤")
    print("  - step in (si): 进入工具调用")
    print("  - step out (so): 退出当前层级")
    print("  - step over (sv): 跳过工具调用\n")
    
    debugger.execute_task("""
创建以下目录结构：
- project/
  - src/
    - main.py (内容: print("Main module"))
    - utils.py (内容: def helper(): return "Helper function")
  - tests/
    - test_main.py (内容: print("Testing main"))
  - README.md (内容: # Project README)
""")


def demo_complex_workflow():
    """复杂工作流调试示例"""
    print("\n=== 复杂工作流调试示例 ===\n")
    
    # 创建带有知识文件的 agent
    config = ReactAgentConfig(
        work_dir="output/debug_demo",
        memory_level=MemoryLevel.SMART,  # 使用智能记忆
        llm_model="deepseek-chat",
        llm_temperature=0,
        knowledge_files=[
            "knowledge/best_practices/absolute_path_usage.md",
            "knowledge/output/role_based_output.md"
        ]
    )
    
    agent = GenericReactAgent(config, name="workflow_debug_agent")
    
    # 创建调试器
    debugger = ReactAgentDebugger(agent)
    
    # 设置多个断点
    # 1. 在 ACT 步骤暂停（查看工具调用）
    debugger.add_breakpoint(StepBreakpoint(id="bp_act", step_type=StepType.ACT))
    
    # 2. 在调用搜索相关工具时暂停
    debugger.add_breakpoint(ToolBreakpoint(id="bp_search", tool_name="search_files"))
    debugger.add_breakpoint(ToolBreakpoint(id="bp_grep", tool_name="search_in_files"))
    
    # 3. 条件断点：当要创建 Python 文件时暂停
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_python",
            condition=lambda ctx: any(".py" in str(tc.get("args", {})) 
                          for tc in ctx.get("tool_calls", [])),
            condition_str="创建 Python 文件"
        )
    )
    
    print("执行任务：创建一个简单的 Web 应用")
    print("断点设置：")
    print("  - 所有 ACT（工具调用）步骤")
    print("  - 搜索相关工具调用")
    print("  - 创建 Python 文件时\n")
    
    debugger.execute_task("""
创建一个简单的 Flask Web 应用：
1. 创建 app.py 文件，实现一个返回 "Hello, World!" 的路由
2. 创建 requirements.txt，包含 flask 依赖
3. 创建 README.md，说明如何运行应用
4. 搜索项目中的所有 Python 文件，确认创建成功
""")


def interactive_menu():
    """交互式菜单"""
    while True:
        print("\n" + "="*60)
        print("ReactAgentDebugger 演示菜单")
        print("="*60)
        print("1. 基础调试示例")
        print("2. 工具断点示例")
        print("3. 条件断点示例")
        print("4. 步进模式示例")
        print("5. 复杂工作流调试")
        print("0. 退出")
        print("="*60)
        
        choice = input("\n请选择示例 (0-5): ").strip()
        
        if choice == "0":
            print("退出演示")
            break
        elif choice == "1":
            demo_basic_debugging()
        elif choice == "2":
            demo_tool_breakpoints()
        elif choice == "3":
            demo_conditional_breakpoints()
        elif choice == "4":
            demo_step_modes()
        elif choice == "5":
            demo_complex_workflow()
        else:
            print("无效选择，请重试")


if __name__ == "__main__":
    # 确保输出目录存在
    output_dir = Path("output/debug_demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 设置环境变量（可选）
    # os.environ["DEBUG"] = "1"  # 开启调试日志
    
    print("🐛 ReactAgentDebugger 演示程序")
    print("="*60)
    print("这个演示展示了如何使用调试器来：")
    print("  - 设置不同类型的断点")
    print("  - 单步执行 Agent 的思考过程")
    print("  - 查看执行状态和消息历史")
    print("  - 使用 step in/out/over 控制执行流程")
    print("="*60)
    
    # 运行交互式菜单
    interactive_menu()