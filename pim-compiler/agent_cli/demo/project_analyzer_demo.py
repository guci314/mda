#!/usr/bin/env python3
"""
使用 LangChain Agent 分析项目结构

专门用于分析代码项目的演示
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
from pydantic import SecretStr

# Agent CLI 工具
from agent_cli.tools import get_all_tools
from agent_cli.core import LLMConfig


# 专门的项目分析 prompt
PROJECT_ANALYSIS_PROMPT = """You are a code project analyzer. You need to understand project structure and execution flow.

You have access to the following tools:

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

Tips for analyzing projects:
1. Start by listing the project root directory to understand structure
2. Look for README files, main.py, __main__.py, or entry point scripts
3. Read configuration files like setup.py, pyproject.toml
4. Analyze the main execution flow by reading key files

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


def main():
    """主函数 - 项目分析器"""
    print("🔍 项目分析器 - 使用 LangChain Agent")
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
    
    # 获取工具
    agent_cli_tools = get_all_tools()
    
    # 创建项目分析相关的工具
    tools = []
    
    # 1. 列出文件
    list_tool = next((t for t in agent_cli_tools if t.name == "list_files"), None)
    if list_tool:
        tools.append(Tool(
            name="list_files",
            description="List files in a directory. Input should be a directory path.",
            func=lambda path: list_tool.run({"path": path.strip()})  # 去除空格
        ))
    
    # 2. 读取文件
    read_tool = next((t for t in agent_cli_tools if t.name == "read_file"), None)
    if read_tool:
        tools.append(Tool(
            name="read_file",
            description="Read file contents. Input should be a file path.",
            func=lambda path: read_tool.run({"path": path.strip()})
        ))
    
    # 3. 搜索文件
    search_tool = next((t for t in agent_cli_tools if "search" in t.name), None)
    if search_tool:
        tools.append(Tool(
            name="search_files",
            description="Search for files by pattern. Input: 'directory|pattern'",
            func=lambda x: search_tool.run({
                "path": x.split("|")[0].strip() if "|" in x else ".",
                "pattern": x.split("|")[1].strip() if "|" in x else x.strip()
            })
        ))
    
    print(f"可用工具: {[t.name for t in tools]}")
    
    # 创建 prompt
    prompt = PromptTemplate.from_template(PROJECT_ANALYSIS_PROMPT)
    
    # 创建 agent
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
        max_iterations=10,  # 增加迭代次数
        handle_parsing_errors=True
    )
    
    # 获取当前项目路径
    current_project = str(pim_compiler_path)
    
    # 演示任务
    demo_tasks = [
        f"分析 {current_project} 项目的结构和主要组件",
        f"理解 {current_project} 的执行流程，从入口点开始",
        f"查找并解释 {current_project} 项目的核心功能模块",
        "分析当前目录下的 Python 项目结构"
    ]
    
    print("\n预设任务:")
    for i, task in enumerate(demo_tasks, 1):
        print(f"{i}. {task}")
    
    # 添加自定义项目路径选项
    print(f"\n当前项目路径: {current_project}")
    print("提示: 你也可以输入其他项目的完整路径来分析")
    
    choice = input("\n选择任务 (1-4) 或输入自定义任务/路径: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(demo_tasks):
        task = demo_tasks[int(choice) - 1]
    else:
        # 检查是否是路径
        if choice.startswith("/") or choice.startswith("~"):
            task = f"分析 {choice} 项目的结构和执行流程"
        else:
            task = choice
    
    print(f"\n执行任务: {task}")
    print("-" * 60)
    
    try:
        # 执行任务
        result = agent_executor.invoke({"input": task})
        
        print("\n" + "=" * 60)
        print("✅ 分析完成!")
        print("\n📊 分析结果:")
        print("-" * 60)
        print(result.get('output', 'No output'))
        
        # 保存结果
        if input("\n是否保存分析结果？(y/n): ").lower() == 'y':
            from datetime import datetime
            filename = f"project_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"任务: {task}\n")
                f.write(f"时间: {datetime.now()}\n")
                f.write(f"\n分析结果:\n{result.get('output', 'No output')}")
            print(f"✅ 结果已保存到: {filename}")
        
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()