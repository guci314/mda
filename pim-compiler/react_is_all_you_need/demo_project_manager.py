#!/usr/bin/env python3
"""
项目经理Agent演示
展示如何使用项目经理Agent编排多个子Agent协同工作
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent_minimal import ReactAgentMinimal

def create_project_manager_demo():
    """创建项目经理Agent并添加子Agent作为工具"""
    
    print("="*60)
    print("项目经理Agent演示")
    print("="*60)
    
    # 1. 创建项目经理Agent
    pm_agent = ReactAgentMinimal(
        work_dir="demo_project",
        name="project_manager",
        description="项目经理Agent，负责编排和协调其他Agent完成软件开发任务",
        model="x-ai/grok-code-fast-1",  # 使用Grok模型
        knowledge_files=["knowledge/roles/project_manager.md"],
        minimal_mode=False
    )
    
    print("\n" + "="*60)
    print("添加子Agent作为工具")
    print("="*60)
    
    # 2. 创建专业Agent（作为项目经理的工具）
    
    # 编码Agent
    coder_agent = ReactAgentMinimal(
        work_dir="demo_project",
        name="coder_agent",
        description="负责编写代码的Agent，擅长Python、JavaScript等语言",
        model="x-ai/grok-code-fast-1",
        minimal_mode=True  # 子Agent可以用极简模式
    )
    pm_agent.add_function(coder_agent)
    
    # 测试Agent
    tester_agent = ReactAgentMinimal(
        work_dir="demo_project",
        name="tester_agent", 
        description="负责编写和运行测试的Agent，确保代码质量",
        model="x-ai/grok-code-fast-1",
        minimal_mode=True
    )
    pm_agent.add_function(tester_agent)
    
    # 调试Agent
    debugger_agent = ReactAgentMinimal(
        work_dir="demo_project",
        name="debugger_agent",
        description="负责调试和修复bug的Agent，擅长问题诊断",
        model="x-ai/grok-code-fast-1",
        minimal_mode=True
    )
    pm_agent.add_function(debugger_agent)
    
    # 文档Agent
    doc_agent = ReactAgentMinimal(
        work_dir="demo_project",
        name="doc_agent",
        description="负责编写文档的Agent，包括README、API文档等",
        model="x-ai/grok-code-fast-1",
        minimal_mode=True
    )
    pm_agent.add_function(doc_agent)
    
    print("\n" + "="*60)
    print("项目经理Agent工具列表")
    print("="*60)
    
    # 3. 显示所有可用工具
    for tool in pm_agent.tool_instances:
        print(f"  🔧 {tool.name}: {tool.description}")
    
    return pm_agent

def demo_simple_project():
    """演示一个简单的项目开发流程"""
    
    # 创建项目经理Agent
    pm = create_project_manager_demo()
    
    print("\n" + "="*60)
    print("执行项目任务")
    print("="*60)
    
    # 定义项目任务
    task = """
    创建一个简单的TODO应用，要求：
    1. 实现添加任务功能
    2. 实现删除任务功能
    3. 实现标记完成功能
    4. 编写单元测试
    5. 生成README文档
    
    请协调各个Agent完成这个项目。先让coder_agent编写代码，
    然后让tester_agent编写测试，最后让doc_agent生成文档。
    """
    
    # 执行任务
    result = pm.execute(task=task)
    
    print("\n" + "="*60)
    print("任务完成")
    print("="*60)
    print(result)

def demo_debug_workflow():
    """演示调试工作流程"""
    
    # 创建项目经理Agent
    pm = create_project_manager_demo()
    
    print("\n" + "="*60)
    print("执行调试任务")
    print("="*60)
    
    # 定义调试任务
    task = """
    有一个Python函数出现了bug：
    
    ```python
    def calculate_average(numbers):
        total = sum(numbers)
        return total / len(numbers)
    ```
    
    当传入空列表时会报错。请协调debugger_agent找出问题，
    让coder_agent修复代码，然后让tester_agent验证修复。
    """
    
    # 执行任务
    result = pm.execute(task=task)
    
    print("\n" + "="*60)
    print("调试完成")
    print("="*60)
    print(result)

def demo_agent_as_function():
    """演示Agent作为Function的直接调用"""
    
    print("="*60)
    print("Agent作为Function直接调用演示")
    print("="*60)
    
    # 创建一个简单的Agent
    simple_agent = ReactAgentMinimal(
        work_dir="demo_function",
        name="calculator",
        description="计算器Agent",
        parameters={
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式"
            }
        },
        model="x-ai/grok-code-fast-1",
        minimal_mode=True
    )
    
    # 直接作为Function调用
    result = simple_agent.execute(expression="2 + 3 * 4")
    print(f"计算结果: {result}")
    
    # 也可以传统方式调用
    result2 = simple_agent.execute(task="计算 15 除以 3")
    print(f"计算结果2: {result2}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "simple":
            demo_simple_project()
        elif sys.argv[1] == "debug":
            demo_debug_workflow()
        elif sys.argv[1] == "function":
            demo_agent_as_function()
        else:
            print("Usage: python demo_project_manager.py [simple|debug|function]")
    else:
        # 默认只创建项目经理Agent
        pm = create_project_manager_demo()
        print("\n✅ 项目经理Agent已创建，包含4个子Agent作为工具")
        print("\n可以通过以下方式运行演示：")
        print("  python demo_project_manager.py simple   # 简单项目演示")
        print("  python demo_project_manager.py debug    # 调试工作流演示")
        print("  python demo_project_manager.py function # Agent作为Function演示")