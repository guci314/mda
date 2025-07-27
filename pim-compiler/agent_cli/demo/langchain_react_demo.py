#!/usr/bin/env python3
"""
使用 LangChain 标准 ReAct Agent

这是 LangChain 最常用和稳定的 Agent 类型
"""

import sys
import os
from pathlib import Path

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
from langchain.memory import ConversationBufferMemory
from pydantic import SecretStr

# Agent CLI 工具
from agent_cli.tools import get_all_tools
from agent_cli.core import LLMConfig


# ReAct prompt template
REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

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


def main():
    """主函数 - 使用 ReAct Agent"""
    print("🤖 LangChain ReAct Agent 演示")
    print("=" * 60)
    
    # 创建 LLM
    config = LLMConfig.from_env('deepseek')
    llm = ChatOpenAI(
        api_key=SecretStr(config.api_key) if config.api_key else None,
        base_url=config.base_url,
        model=config.model,
        temperature=0
    )
    
    print(f"使用 LLM: {config.provider} - {config.model}")
    
    # 获取并简化工具
    agent_cli_tools = get_all_tools()
    
    # 创建简化的工具列表
    tools = []
    
    # 1. 文件操作工具
    read_tool = next((t for t in agent_cli_tools if t.name == "read_file"), None)
    if read_tool:
        tools.append(Tool(
            name="read_file",
            description="Read the contents of a file. Input should be a file path.",
            func=lambda path: read_tool.run({"path": path})
        ))
    
    write_tool = next((t for t in agent_cli_tools if t.name == "write_file"), None)
    if write_tool:
        tools.append(Tool(
            name="write_file",
            description="Write content to a file. Input should be 'path|content' format.",
            func=lambda x: write_tool.run({
                "path": x.split("|")[0],
                "content": x.split("|", 1)[1] if "|" in x else ""
            })
        ))
    
    list_tool = next((t for t in agent_cli_tools if t.name == "list_files"), None)
    if list_tool:
        tools.append(Tool(
            name="list_files",
            description="List files in a directory. Input should be a directory path.",
            func=lambda path: list_tool.run({"path": path})
        ))
    
    # 2. Python 执行工具
    python_tool = next((t for t in agent_cli_tools if t.name == "python_repl"), None)
    if python_tool:
        tools.append(Tool(
            name="python_repl",
            description="Execute Python code. Input should be Python code string.",
            func=lambda code: python_tool.run({"code": code})
        ))
    
    print(f"可用工具: {[t.name for t in tools]}")
    
    # 创建 prompt
    prompt = PromptTemplate.from_template(REACT_PROMPT)
    
    # 创建 ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # 创建 executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )
    
    # 演示任务
    demo_tasks = [
        "创建一个 hello.py 文件，内容是打印 'Hello, World!'",
        "列出当前目录的所有文件",
        "创建一个函数计算斐波那契数列的第10项并执行它",
        "读取 README_langchain_demo.md 文件的前100个字符"
    ]
    
    print("\n预设任务:")
    for i, task in enumerate(demo_tasks, 1):
        print(f"{i}. {task}")
    
    choice = input("\n选择任务 (1-4) 或输入自定义任务: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(demo_tasks):
        task = demo_tasks[int(choice) - 1]
    else:
        task = choice
    
    print(f"\n执行任务: {task}")
    print("-" * 60)
    
    try:
        # 执行任务
        result = agent_executor.invoke({"input": task})
        
        print("\n" + "=" * 60)
        print("✅ 执行完成!")
        print(f"最终答案: {result.get('output', 'No output')}")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()