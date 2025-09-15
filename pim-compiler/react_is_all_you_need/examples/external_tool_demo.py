#!/usr/bin/env python3
"""
演示：Agent使用外部工具
展示身体（Tool）、大脑（Agent）、外部工具的协作
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal

def demo_external_tools():
    """演示外部工具的使用"""
    
    print("🧠 Agent + 外部工具 演示")
    print("=" * 50)
    print("架构：")
    print("  🧠 大脑 = Agent + LLM（理解意图）")
    print("  🤚 身体 = Tool（ExecuteCommand）")  
    print("  🔨 外部工具 = order_system.py（执行任务）")
    print("  📚 知识 = 如何使用工具的说明")
    print("=" * 50)
    
    # 创建Agent
    agent = ReactAgentMinimal(
        work_dir="/tmp/external_tool_demo",
        model="x-ai/grok-code-fast-1",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/external_tools_usage.md"
        ]
    )
    
    # 测试外部工具
    print("\n1️⃣ 使用外部工具创建订单...")
    result = agent.execute(task="""
    使用订单系统外部工具创建一个订单：
    - 客户：李四
    - 电话：13900139000
    - 商品：iPhone 15 Pro（8999元）x1，AirPods Pro（1999元）x2
    - VIP折扣：8折
    """)
    print(f"结果：{result[:300]}...")
    
    print("\n2️⃣ 查询订单...")
    result = agent.execute(task="""
    使用外部工具查询李四的所有订单
    """)
    print(f"结果：{result[:300]}...")
    
    print("\n3️⃣ 更新订单状态...")
    result = agent.execute(task="""
    使用外部工具将李四最新的订单状态更新为"已支付"
    """)
    print(f"结果：{result[:300]}...")
    
    print("\n" + "=" * 50)
    print("✅ 演示完成")
    print("\n核心洞察：")
    print("1. Tool（ExecuteCommand）保持稳定 - 身体不进化")
    print("2. 外部工具（order_system.py）独立进化 - 工具进化")
    print("3. 知识文件描述如何使用 - 知识进化")
    print("4. Agent理解并协调一切 - 大脑指挥")

if __name__ == "__main__":
    demo_external_tools()