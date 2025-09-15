#!/usr/bin/env python3
"""
极简订单系统演示
证明：自然语言函数 > 代码生成
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal

def demo_order_system():
    """演示用自然语言函数实现订单系统"""
    
    print("🛍️ 极简订单系统演示")
    print("=" * 50)
    
    # 创建订单处理Agent
    agent = ReactAgentMinimal(
        work_dir="/tmp/simple_order_system",
        model="x-ai/grok-code-fast-1",  # 或使用其他模型
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/simple_order_system.md"
        ]
    )
    
    # 示例1：创建订单
    print("\n📝 创建订单...")
    result = agent.execute(task="""
    调用 创建订单：
    - 客户：张三
    - 手机：13800138000
    - 商品：
      * MacBook Pro M3 x1 (￥15999)
      * Magic Mouse x1 (￥699)
    - 地址：北京市海淀区中关村
    - 应用VIP折扣（8折）
    """)
    print(f"结果：{result[:200]}...")
    
    # 示例2：查询订单
    print("\n🔍 查询订单...")
    result = agent.execute(task="""
    调用 查询订单：查询所有订单
    """)
    print(f"结果：{result[:200]}...")
    
    # 示例3：处理特殊情况
    print("\n⚠️ 处理特殊情况...")
    result = agent.execute(task="""
    客户要求修改订单，增加一个iPad Air，
    但是要保持原有的折扣。
    检查库存，如果有货就更新订单。
    """)
    print(f"结果：{result[:200]}...")
    
    print("\n" + "=" * 50)
    print("✅ 演示完成")
    print("\n核心洞察：")
    print("1. 没有生成任何代码")
    print("2. 直接用自然语言描述业务逻辑")
    print("3. Agent自动理解并执行")
    print("4. 灵活处理各种情况")

if __name__ == "__main__":
    demo_order_system()