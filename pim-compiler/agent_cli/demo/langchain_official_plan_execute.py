#!/usr/bin/env python3
"""
使用 LangChain 官方 Plan-and-Execute Agent

基于 LangChain 的实验性 plan-and-execute agents
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

try:
    # 尝试导入 langchain_experimental
    from langchain_experimental.plan_and_execute import (
        PlanAndExecute,
        load_agent_executor,
        load_chat_planner
    )
    EXPERIMENTAL_AVAILABLE = True
except ImportError:
    EXPERIMENTAL_AVAILABLE = False
    print("❌ 需要安装 langchain-experimental:")
    print("   pip install langchain-experimental")

from langchain_openai import ChatOpenAI
from langchain.agents.tools import Tool
from pydantic import SecretStr

# Agent CLI 工具
from agent_cli.tools import get_all_tools
from agent_cli.core import LLMConfig


def create_langchain_tools():
    """将 Agent CLI 工具转换为 LangChain Tool 格式"""
    agent_cli_tools = get_all_tools()
    
    # 转换为简单的 Tool 对象
    tools = []
    for tool in agent_cli_tools:
        # 创建包装函数来处理参数
        def make_func(t):
            def wrapper(query: str) -> str:
                try:
                    # 简单的参数解析
                    if ":" in query:
                        parts = query.split(":", 1)
                        if len(parts) == 2:
                            return t.run({"path": parts[1].strip()})
                    return t.run(query)
                except Exception as e:
                    return f"Error: {str(e)}"
            return wrapper
        
        tools.append(Tool(
            name=tool.name,
            description=tool.description,
            func=make_func(tool)
        ))
    
    return tools


def main():
    """主函数 - 使用 LangChain 官方 Plan-and-Execute"""
    
    if not EXPERIMENTAL_AVAILABLE:
        return
    
    print("🤖 LangChain 官方 Plan-and-Execute Agent 演示")
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
    tools = create_langchain_tools()
    print(f"可用工具: {len(tools)} 个")
    
    # 创建 planner
    planner = load_chat_planner(llm)
    
    # 创建 executor 
    # 使用 zero-shot-react-description 代理
    executor = load_agent_executor(
        llm,
        tools,
        verbose=True
    )
    
    # 创建 Plan-and-Execute agent
    agent = PlanAndExecute(
        planner=planner,
        executor=executor,
        verbose=True
    )
    
    # 演示任务
    demo_tasks = [
        "创建一个 hello.py 文件，内容是打印当前时间",
        "列出当前目录的所有 Python 文件",
        "创建一个简单的计算器函数并测试它"
    ]
    
    print("\n预设任务:")
    for i, task in enumerate(demo_tasks, 1):
        print(f"{i}. {task}")
    
    choice = input("\n选择任务 (1-3) 或输入自定义任务: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(demo_tasks):
        task = demo_tasks[int(choice) - 1]
    else:
        task = choice
    
    print(f"\n执行任务: {task}")
    print("-" * 60)
    
    try:
        # 执行任务
        result = agent.run(task)
        
        print("\n" + "=" * 60)
        print("✅ 执行完成!")
        print(f"结果: {result}")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()