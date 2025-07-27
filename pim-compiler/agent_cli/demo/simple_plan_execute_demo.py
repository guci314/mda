#!/usr/bin/env python3
"""
简单的 LangChain Plan-and-Execute 演示

展示最基本的 Plan-and-Execute 架构
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

from langchain_plan_execute_demo import PlanAndExecuteAgent
from agent_cli.core import LLMConfig


def main():
    """运行简单演示"""
    print("🤖 LangChain Plan-and-Execute 简单演示")
    print("=" * 50)
    
    # 创建配置
    config = LLMConfig.from_env('deepseek')
    print(f"使用 LLM: {config.provider} - {config.model}")
    
    # 创建 Agent
    try:
        agent = PlanAndExecuteAgent(llm_config=config)
        print("✅ Agent 创建成功")
    except Exception as e:
        print(f"❌ Agent 创建失败: {e}")
        return
    
    # 简单任务
    task = "创建一个 hello_world.py 文件，内容是打印 'Hello, World!'"
    
    print(f"\n任务: {task}")
    print("-" * 50)
    
    # 执行任务
    try:
        result = agent.execute_task(task)
        
        print("\n执行完成！")
        print(f"总步骤: {result['summary']['total_steps']}")
        print(f"完成步骤: {result['summary']['completed_steps']}")
        print(f"失败步骤: {result['summary']['failed_steps']}")
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()