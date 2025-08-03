#!/usr/bin/env python3
"""高效的 Agent 协作演示 - 展示优化后的多 Agent 协同工作"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from langchain_agent_tool import GenericAgentTool
from langchain_core.tools import tool

def main():
    print("=== 高效 Agent 协作演示 ===\n")
    print("目标：展示简化的任务流程和信任机制\n")
    
    # 共享工作目录
    work_dir = Path("output/efficient_demo")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 创建专家 Agent（极简配置）
    print("1. 创建专家 Agent...")
    
    # 开发者 Agent
    developer = GenericReactAgent(
        ReactAgentConfig(
            work_dir=str(work_dir),
            memory_level=MemoryLevel.NONE,
            knowledge_files=[],
            specification="Python 开发专家"
        ),
        name="developer"
    )
    
    # 测试员 Agent  
    tester = GenericReactAgent(
        ReactAgentConfig(
            work_dir=str(work_dir),
            memory_level=MemoryLevel.NONE,
            knowledge_files=[],
            specification="代码测试专家"
        ),
        name="tester"
    )
    
    # 2. 创建工具（使用 GenericAgentTool）
    dev_tool = GenericAgentTool(developer)
    test_tool = GenericAgentTool(tester)
    
    # 3. 创建高效的主管 Agent
    print("2. 创建主管 Agent...")
    
    manager_config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        knowledge_files=[
            "knowledge/delegation_best_practices.md",
            "knowledge/task_dependencies.md",
            "knowledge/context_passing.md"
        ],
        specification="高效的项目主管"
    )
    
    # 传入工具
    manager = GenericReactAgent(manager_config, name="manager", custom_tools=[dev_tool, test_tool])
    
    # 4. 执行精简任务
    print("3. 执行任务\n")
    
    simple_task = """快速完成：
1. 让开发者创建 utils.py（包含一个 format_date 函数）
2. 开发完成后，让测试员验证函数是否工作

记住：相信每个专家的结果，不要重复检查。"""
    
    print("[主管] 开始协调任务...\n")
    manager.execute_task(simple_task)
    
    # 5. 显示最终结果
    print(f"\n=== 最终产出 ===")
    for file in work_dir.iterdir():
        if file.is_file() and not str(file).startswith('.'):
            print(f"✅ {file.name}")
            if file.suffix == '.py':
                content = file.read_text()
                print(f"   预览: {content[:100]}...")
    
    print("\n=== 演示完成 ===")
    print("展示了：")
    print("- 简化的任务描述")
    print("- 高效的 Agent 协作")
    print("- 信任机制的实践")

if __name__ == "__main__":
    main()