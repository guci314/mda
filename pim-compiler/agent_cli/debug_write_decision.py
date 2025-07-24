#!/usr/bin/env python3
"""
调试 write_file 决策问题
"""
import os
import json
from dotenv import load_dotenv
from agent_cli.core import AgentCLI, LLMConfig

# 加载环境变量
load_dotenv()

def debug_write_file_decision():
    """调试 write_file 工具的参数生成"""
    print("=== Debugging write_file Decision ===\n")
    
    # 创建配置
    config = LLMConfig.from_env("deepseek")
    
    # 创建 agent
    agent = AgentCLI(
        llm_config=config,
        use_langchain_tools=True,
        enable_symbolic_fallback=False  # 禁用符号回退
    )
    
    # 设置上下文
    agent.context = {
        "task": "创建文件 hello.py，内容是 def hello(): print('Hello!')"
    }
    
    # 模拟决策过程
    step = "使用 write_file 工具创建 hello.py 文件，内容是 def hello(): print('Hello!')"
    thought = "需要使用 write_file 工具创建文件，路径是 hello.py，内容是函数定义"
    
    print("Step:", step)
    print("Thought:", thought)
    print("\n" + "="*50 + "\n")
    
    # 调用决策方法
    try:
        action = agent._decide_action(thought, step)
        print(f"Decision made:")
        print(f"  Action type: {action.type}")
        print(f"  Description: {action.description}")
        print(f"  Parameters: {json.dumps(action.params, indent=2, ensure_ascii=False)}")
        
        # 如果是 write_file，检查参数
        if action.type.value == "write_file":
            print("\nParameter check:")
            print(f"  - path: {'✓' if 'path' in action.params else '✗'} {action.params.get('path', 'MISSING')}")
            print(f"  - content: {'✓' if 'content' in action.params and action.params['content'] else '✗'} {repr(action.params.get('content', 'MISSING'))[:100]}")
            
    except Exception as e:
        print(f"Error in decision: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_write_file_decision()