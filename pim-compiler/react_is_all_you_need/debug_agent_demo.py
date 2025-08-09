#!/usr/bin/env python3
"""演示调试多 Agent 协作场景

展示如何使用 ReactAgentDebugger 调试子 Agent 调用，
包括 step in/out 功能的正确使用。
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from react_agent_debugger import (
    ReactAgentDebugger, 
    StepType, 
    StepBreakpoint,
    AgentBreakpoint,
    ToolBreakpoint
)
from core.langchain_agent_tool import create_langchain_tool


def demo_multi_agent_debugging():
    """演示多 Agent 协作的调试"""
    print("=== 多 Agent 协作调试示例 ===\n")
    
    work_dir = Path("output/debug_multi_agent")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建子 Agent：代码生成器
    code_gen_config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat",
        llm_temperature=0,
        specification="专门生成 Python 代码文件"
    )
    code_gen_agent = GenericReactAgent(code_gen_config, name="code_generator")
    
    # 创建子 Agent：代码审查器
    code_review_config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat",
        llm_temperature=0,
        specification="审查代码质量并提供改进建议"
    )
    code_review_agent = GenericReactAgent(code_review_config, name="code_reviewer")
    
    # 将子 Agent 转换为工具
    code_gen_tool = create_langchain_tool(code_gen_agent)
    code_gen_tool.name = "code_generator"
    
    code_review_tool = create_langchain_tool(code_review_agent)  
    code_review_tool.name = "code_reviewer"
    
    # 创建主协调 Agent
    main_config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat",
        llm_temperature=0,
        specification="协调多个专家 Agent 完成软件开发任务"
    )
    
    # 创建基本工具
    from core.tools import create_tools
    basic_tools = create_tools(str(work_dir))
    
    # 组合所有工具
    all_tools = basic_tools + [code_gen_tool, code_review_tool]
    
    # 创建主 Agent
    main_agent = GenericReactAgent(
        main_config, 
        name="project_manager",
        custom_tools=all_tools
    )
    
    # 创建调试器
    debugger = ReactAgentDebugger(main_agent)
    debugger.verbose = True
    
    # 设置断点
    print("设置断点：")
    print("1. Agent 断点：在调用 code_generator 时暂停")
    print("2. Agent 断点：在调用 code_reviewer 时暂停") 
    print("3. 工具断点：在调用 write_file 时暂停（对比普通工具）\n")
    
    debugger.add_breakpoint(AgentBreakpoint("bp_gen", "code_generator"))
    debugger.add_breakpoint(AgentBreakpoint("bp_review", "code_reviewer"))
    debugger.add_breakpoint(ToolBreakpoint("bp_write", "write_file"))
    
    print("任务说明：")
    print("- 主 Agent 会协调两个子 Agent")
    print("- 当调用子 Agent 时，可以使用 step in 进入")
    print("- 当调用普通工具时，step in 不可用")
    print("- 使用 step out 退出子 Agent\n")
    
    print("=" * 60)
    print("提示：")
    print("- 在子 Agent 调用处，尝试 'si' (step in)")
    print("- 在普通工具调用处，尝试 'si' 看提示信息")
    print("- 在子 Agent 内部，尝试 'so' (step out)")
    print("=" * 60)
    print()
    
    # 执行任务
    debugger.execute_task("""
请完成以下任务：
1. 使用 code_generator 创建一个 calculator.py 文件，实现加减乘除四个函数
2. 使用 code_reviewer 审查生成的代码质量
3. 根据审查建议，创建一个 improvements.md 文件记录改进点
""")
    
    print("\n✅ 多 Agent 调试演示完成")
    print("\n关键点总结：")
    print("- step in/out 只在子 Agent 调用时有效")
    print("- 调试器会自动识别并跟踪子 Agent 调用栈")
    print("- 普通工具调用使用 step over 即可")


def demo_nested_agents():
    """演示嵌套 Agent 调用的调试"""
    print("\n=== 嵌套 Agent 调用调试示例 ===\n")
    
    # 这里可以创建更复杂的嵌套场景
    # 例如：Manager -> TeamLead -> Developer
    # 展示多层 step in/out
    
    print("（此示例待实现，展示更深层的 Agent 嵌套调用）")


if __name__ == "__main__":
    print("🐛 多 Agent 协作调试演示")
    print("="*60)
    print("这个演示展示了：")
    print("  - 如何调试子 Agent 调用")
    print("  - step in/out 的正确使用场景") 
    print("  - 子 Agent vs 普通工具的区别")
    print("="*60)
    print()
    
    # 运行主要演示
    demo_multi_agent_debugging()
    
    # 可选：运行嵌套演示
    # demo_nested_agents()