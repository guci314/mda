#!/usr/bin/env python3
"""
订单主Agent演示
订单Agent作为主Agent，协调其他子Agent完成订单流程
无需AgentNetwork，直接通过add_function组合
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal

def create_order_main_agent():
    """
    创建订单主Agent
    订单Agent负责协调其他服务完成订单流程
    """
    print("🚀 创建订单主Agent系统")
    print("=" * 60)
    
    # 创建子Agent（作为订单Agent的函数）
    print("📦 创建子Agent服务...")
    
    # 客户服务Agent
    customer_agent = ReactAgentMinimal(
        name="调用客户服务",
        description="获取客户信息、会员等级和折扣",
        work_dir="/tmp/microservices/customers",
        model="x-ai/grok-code-fast-1",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/customer_service/customer_knowledge.md"
        ],
        max_rounds=20
    )
    
    # 产品服务Agent
    product_agent = ReactAgentMinimal(
        name="调用产品服务",
        description="获取商品价格和产品信息",
        work_dir="/tmp/microservices/products",
        model="x-ai/grok-code-fast-1",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/product_service/product_knowledge.md"
        ],
        max_rounds=20
    )
    
    # 库存服务Agent
    inventory_agent = ReactAgentMinimal(
        name="调用库存服务",
        description="检查库存和扣减库存",
        work_dir="/tmp/microservices/inventory",
        model="x-ai/grok-code-fast-1",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/inventory_service/inventory_knowledge.md"
        ],
        max_rounds=20
    )
    
    print("✅ 子Agent创建完成")
    
    # 创建订单主Agent
    print("\n🎯 创建订单主Agent...")
    order_agent = ReactAgentMinimal(
        name="订单服务主Agent",
        description="处理订单业务，协调其他服务完成订单流程",
        work_dir="/tmp/microservices/orders",
        model="x-ai/grok-code-fast-1",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/order_service/order_knowledge_v2.md"
        ],
        max_rounds=30
    )
    
    # 将子Agent注册为订单Agent的函数
    print("📌 注册子Agent为订单Agent的函数...")
    order_agent.add_function(customer_agent)
    order_agent.add_function(product_agent)
    order_agent.add_function(inventory_agent)
    print("✅ 子Agent已注册")
    
    return order_agent

def demonstrate_order_processing():
    """演示订单处理流程"""
    print("\n" + "=" * 60)
    print("📝 订单处理演示")
    print("=" * 60)
    
    # 创建订单主Agent
    order_agent = create_order_main_agent()
    
    # 测试场景1：创建订单
    print("\n场景1：为VIP客户创建订单")
    print("-" * 40)
    
    # 简单的业务请求，流程在知识文件中定义
    task = """
    为客户CUST001创建订单：
    - 购买iPhone 15 Pro (PROD001) 1台
    - 购买AirPods Pro (PROD002) 2个
    """
    
    print("📋 任务：", task)
    print("\n🤖 订单Agent开始处理...")
    print("（订单处理流程已在知识文件中定义）")
    print("-" * 40)
    
    result = order_agent.execute(task=task)
    
    print("\n✅ 处理结果：")
    print(result[:500] if len(result) > 500 else result)
    
    # 测试场景2：查询订单
    print("\n\n场景2：查询订单状态")
    print("-" * 40)
    
    query_task = "查询所有订单的状态"
    print("📋 任务：", query_task)
    
    result = order_agent.execute(task=query_task)
    print("\n✅ 查询结果：")
    print(result[:500] if len(result) > 500 else result)

def main():
    """主函数"""
    print("🌟 订单主Agent架构演示")
    print("=" * 60)
    print("架构特点：")
    print("  • 订单Agent是主Agent，负责协调流程")
    print("  • 其他服务是子Agent，通过add_function注册")
    print("  • 订单知识文件定义完整业务流程")
    print("  • 无需额外的AgentNetwork类")
    print("=" * 60)
    
    try:
        demonstrate_order_processing()
        
        print("\n" + "=" * 60)
        print("🎯 架构优势总结")
        print("=" * 60)
        print("""
1. **简洁性**：无需AgentNetwork，直接组合Agent
2. **清晰性**：订单Agent明确是主Agent
3. **知识驱动**：流程定义在知识文件中
4. **可扩展**：轻松添加新的子Agent
5. **自然分工**：每个Agent专注自己的领域

这才是真正的Agent架构：
- 主Agent = 业务流程协调者
- 子Agent = 专业服务提供者
- 知识文件 = 业务逻辑定义
        """)
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()