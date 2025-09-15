#!/usr/bin/env python3
"""
订单Agent - 知识驱动架构演示
展示：业务流程完全由知识文件定义，代码只是框架
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal

def main():
    """
    极简的订单处理系统
    所有业务逻辑都在知识文件中
    """
    print("🌟 知识驱动的订单处理系统")
    print("=" * 60)
    print("核心理念：")
    print("  • 业务流程在知识文件中，不在代码中")
    print("  • 用户只需描述需求，不需要说明步骤")
    print("  • Agent理解业务，自主完成流程")
    print("=" * 60)
    
    # 创建子Agent
    customer_agent = ReactAgentMinimal(
        name="customer_service",
        description="获取客户信息、会员等级和折扣",
        work_dir="/tmp/microservices/customers",
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/customer_service/customer_knowledge.md"
        ]
    )
    
    product_agent = ReactAgentMinimal(
        name="product_service",
        description="获取商品价格和产品信息",
        work_dir="/tmp/microservices/products",
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/product_service/product_knowledge.md"
        ]
    )
    
    inventory_agent = ReactAgentMinimal(
        name="inventory_service",
        description="检查库存和扣减库存",
        work_dir="/tmp/microservices/inventory",
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/inventory_service/inventory_knowledge.md"
        ]
    )
    
    # 创建订单主Agent
    order_agent = ReactAgentMinimal(
        name="order_service",
        description="处理订单业务，协调其他服务完成订单流程",
        work_dir="/tmp/microservices/orders",
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/order_service/order_knowledge_v2.md"
        ]
    )
    
    # 组合Agent
    order_agent.add_function(customer_agent)
    order_agent.add_function(product_agent)
    order_agent.add_function(inventory_agent)
    
    print("\n📝 业务请求示例")
    print("-" * 60)
    
    # 示例1：简单的创建订单请求
    print("\n1️⃣ 创建订单（简单请求）")
    request1 = "为客户CUST001创建订单，购买一台iPhone和两个AirPods"
    print(f"请求：{request1}")
    print("Agent响应：自动执行6步流程...")
    
    # 示例2：更自然的请求
    print("\n2️⃣ 创建订单（自然语言）")
    request2 = "张三要买个iPhone，他是VIP客户"
    print(f"请求：{request2}")
    print("Agent响应：理解意图，查询客户，创建订单...")
    
    # 示例3：批量订单
    print("\n3️⃣ 批量订单")
    request3 = "帮公司采购10台iPhone作为年会奖品"
    print(f"请求：{request3}")
    print("Agent响应：批量处理，检查库存，应用企业折扣...")
    
    # 示例4：查询请求
    print("\n4️⃣ 查询订单")
    request4 = "查看今天的所有订单"
    print(f"请求：{request4}")
    print("Agent响应：查询订单，统计汇总...")
    
    print("\n" + "=" * 60)
    print("💡 关键洞察")
    print("=" * 60)
    print("""
传统方式 vs 知识驱动：

传统API调用：
    order_service.create_order(
        customer_id='CUST001',
        items=[
            {'id': 'PROD001', 'quantity': 1},
            {'id': 'PROD002', 'quantity': 2}
        ],
        steps=['get_customer', 'check_stock', 'calculate', ...]
    )

知识驱动方式：
    "张三要买个iPhone"
    
区别：
1. 无需指定流程步骤 - 知识文件已定义
2. 无需精确参数格式 - Agent理解意图
3. 无需API文档 - 自然语言即接口
4. 无需错误处理代码 - Agent自主处理

这就是为什么说：
✨ 编程的本质是建模，不是编码
✨ 知识即程序，Agent即函数
✨ 自然语言是最好的API
    """)
    
    # 实际执行一个简单请求
    print("\n" + "=" * 60)
    print("🚀 实际执行演示")
    print("=" * 60)
    
    simple_request = "为CUST001创建订单：iPhone一台，AirPods两个"
    print(f"\n📋 请求：{simple_request}")
    print("\n处理中...")
    
    # 执行请求 - 所有流程都在知识文件中定义
    result = order_agent.execute(task=simple_request)
    
    print("\n✅ 结果：")
    print(result[:300] if len(result) > 300 else result)
    
    print("\n" + "=" * 60)
    print("✨ 总结：知识文件定义了一切，代码只是载体")
    print("=" * 60)

if __name__ == "__main__":
    main()