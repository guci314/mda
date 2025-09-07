#!/usr/bin/env python3
"""
异步Agent演示
展示如何通过inbox/outbox实现Agent间异步通信
"""

import time
import subprocess
from pathlib import Path
from datetime import datetime

def send_message(to_agent: str, from_agent: str, task: str):
    """发送异步消息给Agent"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    inbox = Path(f".inbox/{to_agent}")
    inbox.mkdir(parents=True, exist_ok=True)
    
    message_file = inbox / f"msg_{timestamp}.md"
    message_file.write_text(f"""# Message

From: {from_agent}
To: {to_agent}
Time: {datetime.now()}

## Task
{task}
""")
    print(f"📤 Message sent to {to_agent}: {task[:50]}...")
    return message_file.name

def check_inbox_replies(from_agent: str, to_agent: str):
    """检查特定Agent发来的回复消息"""
    inbox = Path(f".inbox/{to_agent}")
    if not inbox.exists():
        return []
    
    results = []
    for file in inbox.glob(f"reply_*.md"):
        content = file.read_text()
        # 检查是否来自指定的agent
        if f"From: {from_agent}" in content:
            results.append(content)
            file.unlink()  # 读取后删除
    return results

def start_agents_in_background():
    """启动多个Agent作为后台进程"""
    agents = ["coder_agent", "tester_agent", "doc_agent"]
    processes = []
    
    for agent in agents:
        print(f"🚀 Starting {agent}...")
        p = subprocess.Popen(
            ["python", "start_async_agent.py", agent],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append((agent, p))
        time.sleep(1)  # 给Agent启动时间
    
    return processes

def demo_async_collaboration():
    """演示异步协作"""
    print("="*60)
    print("异步Agent协作演示")
    print("="*60)
    
    # 1. 启动Agent服务
    print("\n1. 启动Agent服务")
    processes = start_agents_in_background()
    
    # 2. 发送任务
    print("\n2. 项目经理分配任务")
    send_message("coder_agent", "project_manager", 
                 "创建一个简单的计算器类，包含加减乘除方法")
    send_message("tester_agent", "project_manager", 
                 "准备单元测试框架")
    send_message("doc_agent", "project_manager", 
                 "创建README模板")
    
    # 3. 异步等待结果（检查回复消息）
    print("\n3. 等待Agent完成任务...")
    completed = set()
    timeout = 60  # 最多等待60秒
    start_time = time.time()
    
    while len(completed) < 3 and (time.time() - start_time) < timeout:
        for agent, _ in processes:
            if agent not in completed:
                # 检查从agent发回给project_manager的回复
                results = check_inbox_replies(agent, "project_manager")
                if results:
                    print(f"\n✅ {agent} 完成:")
                    for result in results:
                        print(result[:200])
                    completed.add(agent)
        
        if len(completed) < 3:
            print(".", end="", flush=True)
            time.sleep(2)
    
    # 4. 清理
    print("\n\n4. 停止Agent服务")
    for agent, process in processes:
        process.terminate()
        print(f"🛑 {agent} stopped")
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60)

def demo_chain_communication():
    """演示链式通信：A → B → C"""
    print("="*60)
    print("链式通信演示")
    print("="*60)
    
    # 发送消息给第一个Agent
    send_message("coder_agent", "user",
                 "写一个hello world函数，完成后发消息给tester_agent测试")
    
    print("消息已发送，Agent会自动链式处理...")
    
    # 这里Agent会：
    # 1. coder_agent 收到消息，写代码
    # 2. coder_agent 完成后，发消息给 tester_agent
    # 3. tester_agent 收到消息，写测试
    # 等等...

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "collab":
            demo_async_collaboration()
        elif sys.argv[1] == "chain":
            demo_chain_communication()
    else:
        print("Usage:")
        print("  python demo_async_agents.py collab  # 并行协作演示")
        print("  python demo_async_agents.py chain   # 链式通信演示")
        print("\n或者手动启动单个Agent:")
        print("  python start_async_agent.py coder_agent")
        print("  python start_async_agent.py tester_agent")
        print("\n然后手动发送消息:")
        print('  echo "实现TODO类" > .inbox/coder_agent/task.md')