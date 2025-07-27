#!/usr/bin/env python3
"""
Agent 类型对比演示

展示 ReAct 和 Plan-and-Execute 在不同任务上的表现
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any
import time

# 添加 pim-compiler 到 Python 路径
pim_compiler_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(pim_compiler_path))

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# 设置 LLM
os.environ['LLM_PROVIDER'] = 'deepseek'

from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from pydantic import SecretStr

# Agent CLI 工具
from agent_cli.tools import get_all_tools
from agent_cli.core import LLMConfig


# ReAct prompt
REACT_PROMPT = """You are an AI assistant. You have access to the following tools:

{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
Question: {input}
Thought: {agent_scratchpad}"""


# Plan-and-Execute style prompt (模拟)
PLANNER_PROMPT = """You are a task planner. Given a task, create a step-by-step plan.

Task: {input}

Create a detailed plan with numbered steps. Be specific about what each step should do.
Format:
1. [Step description]
2. [Step description]
...

Plan:"""


class TaskDemo:
    """任务演示类"""
    
    def __init__(self, name: str, description: str, 
                 good_for_react: bool, good_for_plan: bool,
                 reason: str):
        self.name = name
        self.description = description
        self.good_for_react = good_for_react
        self.good_for_plan = good_for_plan
        self.reason = reason


# 定义演示任务
DEMO_TASKS = [
    TaskDemo(
        name="探索未知项目",
        description="分析一个未知项目的结构和功能",
        good_for_react=True,
        good_for_plan=False,
        reason="需要根据发现动态调整探索策略"
    ),
    TaskDemo(
        name="创建 Web 应用",
        description="创建一个包含前端和后端的简单 Web 应用",
        good_for_react=False,
        good_for_plan=True,
        reason="步骤明确：创建目录→安装依赖→编写代码→测试"
    ),
    TaskDemo(
        name="调试错误",
        description="查找并修复代码中的错误",
        good_for_react=True,
        good_for_plan=False,
        reason="需要根据错误信息灵活调整调试方向"
    ),
    TaskDemo(
        name="生成报告",
        description="根据模板生成月度报告",
        good_for_react=False,
        good_for_plan=True,
        reason="流程固定：收集数据→分析→格式化→输出"
    ),
    TaskDemo(
        name="寻找配置文件",
        description="在项目中查找所有配置文件并分析其用途",
        good_for_react=True,
        good_for_plan=False,
        reason="不确定配置文件的位置和格式，需要探索"
    )
]


def create_tools():
    """创建简化的工具集"""
    agent_cli_tools = get_all_tools()
    tools = []
    
    # 基本工具
    for tool_name in ["read_file", "write_file", "list_files", "python_repl"]:
        tool = next((t for t in agent_cli_tools if t.name == tool_name), None)
        if tool:
            tools.append(Tool(
                name=tool_name,
                description=f"{tool_name} tool",
                func=lambda x, t=tool: t.run({"path": x} if "file" in t.name else {"code": x})
            ))
    
    return tools


def demonstrate_react(task: str, tools: list):
    """演示 ReAct Agent"""
    print("\n🔄 ReAct Agent 执行方式:")
    print("-" * 50)
    
    config = LLMConfig.from_env('deepseek')
    llm = ChatOpenAI(
        api_key=SecretStr(config.api_key) if config.api_key else None,
        base_url=config.base_url,
        model=config.model,
        temperature=0
    )
    
    prompt = PromptTemplate.from_template(REACT_PROMPT)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )
    
    start_time = time.time()
    try:
        result = agent_executor.invoke({"input": task})
        print(f"\n⏱️  执行时间: {time.time() - start_time:.2f}秒")
        return result.get('output', 'No output')
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def demonstrate_plan_execute(task: str):
    """演示 Plan-and-Execute 风格（简化版）"""
    print("\n📋 Plan-and-Execute 执行方式:")
    print("-" * 50)
    
    config = LLMConfig.from_env('deepseek')
    llm = ChatOpenAI(
        api_key=SecretStr(config.api_key) if config.api_key else None,
        base_url=config.base_url,
        model=config.model,
        temperature=0
    )
    
    # 第一步：创建计划
    print("📝 第一步：生成执行计划")
    planner_prompt = PromptTemplate.from_template(PLANNER_PROMPT)
    plan_chain = planner_prompt | llm
    
    start_time = time.time()
    plan_response = plan_chain.invoke({"input": task})
    
    print("\n生成的计划:")
    print(plan_response.content)
    
    print(f"\n⏱️  规划时间: {time.time() - start_time:.2f}秒")
    
    # 注意：这里只是演示规划步骤，实际执行需要更复杂的实现
    print("\n📌 注：Plan-and-Execute 需要额外的执行器来执行每个步骤")
    
    return plan_response.content


def main():
    """主函数"""
    print("🤖 Agent 类型对比演示")
    print("=" * 60)
    
    print("\n📚 任务类型和推荐的 Agent：\n")
    
    # 显示任务表格
    print(f"{'任务类型':<20} {'适合ReAct':<12} {'适合Plan':<12} {'原因':<40}")
    print("-" * 85)
    
    for task in DEMO_TASKS:
        react_mark = "✅" if task.good_for_react else "❌"
        plan_mark = "✅" if task.good_for_plan else "❌"
        print(f"{task.name:<20} {react_mark:<12} {plan_mark:<12} {task.reason:<40}")
    
    print("\n" + "=" * 60)
    print("\n选择演示:")
    print("1. 项目分析任务（适合 ReAct）")
    print("2. 创建应用任务（适合 Plan-and-Execute）")
    print("3. 对比同一任务的两种执行方式")
    
    choice = input("\n你的选择 (1-3): ")
    
    tools = create_tools()
    
    if choice == "1":
        # ReAct 示例
        task = "分析当前目录的项目结构，找出主要的 Python 文件"
        print(f"\n任务: {task}")
        demonstrate_react(task, tools)
        
    elif choice == "2":
        # Plan-and-Execute 示例
        task = "创建一个简单的 Flask Web 应用，包含首页和 API 端点"
        print(f"\n任务: {task}")
        demonstrate_plan_execute(task)
        
    elif choice == "3":
        # 对比示例
        task = input("\n输入要对比的任务: ")
        
        print("\n" + "=" * 60)
        # 先展示 Plan-and-Execute
        plan_result = demonstrate_plan_execute(task)
        
        if input("\n是否继续查看 ReAct 执行？(y/n): ").lower() == 'y':
            print("\n" + "=" * 60)
            react_result = demonstrate_react(task, tools)
            
            print("\n" + "=" * 60)
            print("📊 对比总结:")
            print("- Plan-and-Execute: 先规划，步骤清晰，但缺乏灵活性")
            print("- ReAct: 边做边想，灵活应对，但可能效率较低")


if __name__ == "__main__":
    main()