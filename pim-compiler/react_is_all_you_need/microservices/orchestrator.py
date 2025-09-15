#!/usr/bin/env python3
"""
微服务协作器
协调多个Agent完成订单处理
展示自然语言函数的微服务架构
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from microservices.order_service.order_agent import OrderAgent
from microservices.inventory_service.inventory_agent import InventoryAgent
from microservices.product_service.product_agent import ProductAgent
from microservices.customer_service.customer_agent import CustomerAgent
import json

class MicroserviceOrchestrator:
    """微服务协作器"""
    
    def __init__(self):
        """初始化所有服务Agent"""
        print("🚀 初始化微服务架构...")
        print("=" * 60)
        
        print("📦 启动订单服务...")
        self.order_agent = OrderAgent()
        
        print("📊 启动库存服务...")
        self.inventory_agent = InventoryAgent()
        
        print("🛍️ 启动产品服务...")
        self.product_agent = ProductAgent()
        
        print("👥 启动客户服务...")
        self.customer_agent = CustomerAgent()
        
        print("=" * 60)
        print("✅ 所有服务已就绪\n")
    
    def process_order_creation(self, customer_id, items):
        """
        处理订单创建流程
        展示多个Agent协作
        """
        print("🎯 开始处理订单创建...")
        print("-" * 60)
        
        # Step 1: 客户服务 - 获取客户信息
        print("\n1️⃣ 【客户服务】获取客户信息...")
        customer_result = self.customer_agent.handle_message(
            f"获取客户 {customer_id} 的信息和会员等级"
        )
        print(f"   结果：{customer_result[:200]}...")
        
        # Step 2: 产品服务 - 获取商品价格
        print("\n2️⃣ 【产品服务】获取商品价格...")
        product_ids = [item['id'] for item in items]
        price_result = self.product_agent.handle_message(
            f"获取以下商品的价格信息：{product_ids}"
        )
        print(f"   结果：{price_result[:200]}...")
        
        # Step 3: 库存服务 - 检查库存
        print("\n3️⃣ 【库存服务】检查库存...")
        stock_result = self.inventory_agent.handle_message(
            f"检查以下商品的库存：{json.dumps(items, ensure_ascii=False)}"
        )
        print(f"   结果：{stock_result[:200]}...")
        
        # Step 4: 订单服务 - 创建订单
        print("\n4️⃣ 【订单服务】创建订单...")
        print("   整合所有信息，创建订单...")
        
        # 模拟订单服务接收到其他服务的信息后创建订单
        order_task = f"""
        基于以下信息创建订单：
        - 客户ID：{customer_id}
        - 商品列表：{json.dumps(items, ensure_ascii=False)}
        - 客户信息：已获取（VIP客户）
        - 商品价格：已获取
        - 库存状态：充足
        
        请：
        1. 计算总价（应用VIP 8折）
        2. 生成订单号
        3. 扣减库存
        4. 保存订单
        """
        
        order_result = self.order_agent.handle_message(order_task)
        print(f"   结果：{order_result[:300]}...")
        
        # Step 5: 库存服务 - 扣减库存
        print("\n5️⃣ 【库存服务】扣减库存...")
        deduct_result = self.inventory_agent.handle_message(
            f"扣减以下商品的库存：{json.dumps(items, ensure_ascii=False)}"
        )
        print(f"   结果：{deduct_result[:200]}...")
        
        print("\n" + "=" * 60)
        print("✅ 订单创建流程完成！")
        
        return order_result
    
    def demonstrate_microservice_communication(self):
        """演示微服务间的通信"""
        print("\n🎭 微服务通信演示")
        print("=" * 60)
        
        # 场景1：创建订单
        print("\n场景1：VIP客户创建订单")
        print("-" * 40)
        
        items = [
            {"id": "PROD001", "name": "iPhone 15 Pro", "quantity": 1},
            {"id": "PROD002", "name": "AirPods Pro", "quantity": 2}
        ]
        
        self.process_order_creation("CUST001", items)
        
        # 场景2：查询服务状态
        print("\n\n场景2：查询各服务状态")
        print("-" * 40)
        
        print("\n📊 查询库存状态...")
        stock_status = self.inventory_agent.handle_message("查询所有商品库存")
        print(f"   {stock_status[:300]}...")
        
        print("\n📦 查询订单状态...")
        order_status = self.order_agent.handle_message("查询所有订单")
        print(f"   {order_status[:300]}...")
        
        print("\n" + "=" * 60)
        print("🎉 演示完成！")

def main():
    """主函数"""
    print("🌟 微服务架构 + 自然语言函数 演示")
    print("=" * 60)
    print("架构特点：")
    print("  • 每个Agent负责一个业务领域")
    print("  • 通过自然语言消息通信")
    print("  • 无需API定义，灵活协作")
    print("  • 知识驱动，易于理解和修改")
    print("=" * 60)
    
    # 创建协作器
    orchestrator = MicroserviceOrchestrator()
    
    # 演示微服务通信
    orchestrator.demonstrate_microservice_communication()
    
    print("\n" + "=" * 60)
    print("核心洞察：")
    print("1. 自然语言函数替代了API定义")
    print("2. Agent间通过语义理解协作")
    print("3. 每个服务保持独立和专注")
    print("4. 系统灵活性极高")
    print("=" * 60)

if __name__ == "__main__":
    main()