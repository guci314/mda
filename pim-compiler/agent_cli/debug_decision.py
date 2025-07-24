#!/usr/bin/env python3
"""
调试 LLM 决策过程
"""
import os
import json
from dotenv import load_dotenv
from agent_cli.core import AgentCLI, LLMConfig
from agent_cli.executors import LangChainToolExecutor

# 加载环境变量
load_dotenv()


def debug_llm_decision():
    """调试 LLM 的工具选择决策"""
    print("=== Debugging LLM Tool Decision ===\n")
    
    # 创建配置
    config = LLMConfig.from_env("deepseek")
    
    # 创建执行器查看工具
    executor = LangChainToolExecutor()
    tools_info = executor.format_tools_for_prompt()
    
    print("Available tools:")
    print(tools_info)
    print("\n" + "="*60 + "\n")
    
    # 创建 agent
    agent = AgentCLI(
        llm_config=config,
        use_langchain_tools=True
    )
    
    # 模拟决策过程
    step = "执行Python代码计算2+3"
    thought = "需要使用Python执行 print(2+3)"
    
    # 调用内部的决策方法
    try:
        action = agent._decide_action(thought, step)
        print(f"Decision made:")
        print(f"  Action type: {action.type}")
        print(f"  Description: {action.description}")
        print(f"  Parameters: {json.dumps(action.params, indent=2)}")
    except Exception as e:
        print(f"Error in decision: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_llm_decision()