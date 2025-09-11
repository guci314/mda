#!/usr/bin/env python3
"""
异步Agent启动器
每个Agent作为独立进程运行，通过inbox/outbox通信
"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from core.react_agent_minimal import ReactAgentMinimal

def start_agent_service(agent_name: str, model: str = "x-ai/grok-code-fast-1"):
    """启动Agent作为后台服务，持续监听inbox"""
    
    print(f"Starting {agent_name} service...")
    
    # 创建inbox目录（没有outbox！）
    inbox = Path(f".inbox/{agent_name}")
    inbox.mkdir(parents=True, exist_ok=True)
    
    # 创建Agent，添加async_agent知识
    agent = ReactAgentMinimal(
        work_dir=".",
        name=agent_name,
        description=f"{agent_name} - 异步服务模式",
        model=model,
        knowledge_files=["knowledge/system/async_agent.md"],
        minimal_mode=True
    )
    
    # 主任务：持续监听inbox
    task = f"""
你是{agent_name}，运行在异步服务模式。

你的主要任务是：
1. 每秒检查一次 .inbox/{agent_name}/ 目录
2. 如果发现.md文件，读取并执行其中的任务
3. 提取消息中的From字段（发送者）
4. 完成后，如果需要回复，将结果写入发送者的inbox（不是outbox！）
5. 删除已处理的消息
6. 如果没有消息，等待1秒后再检查

记住：
- 没有outbox，所有回复都发到原发送者的inbox
- 回复消息要包含From: {agent_name}，这样接收者知道是谁发的

开始持续监听...
"""
    
    # 执行主循环
    result = agent.execute(task=task)
    print(f"{agent_name} service stopped: {result}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python start_async_agent.py <agent_name> [model]")
        print("Example: python start_async_agent.py coder_agent")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "x-ai/grok-code-fast-1"
    
    start_agent_service(agent_name, model)