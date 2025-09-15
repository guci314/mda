#!/usr/bin/env python3
"""
订单服务Agent
负责订单的创建、查询、状态管理
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal
import json

class OrderAgent:
    """订单服务Agent"""
    
    def __init__(self, model="x-ai/grok-code-fast-1"):
        """初始化订单Agent"""
        self.agent = ReactAgentMinimal(
            work_dir="/tmp/microservices/orders",
            model=model,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/order_service/order_knowledge.md"
            ],
            max_rounds=30
        )
        
    def create_order(self, customer_id, items):
        """创建订单"""
        task = f"""
        调用 创建订单：
        - 客户ID：{customer_id}
        - 商品列表：{json.dumps(items, ensure_ascii=False)}
        
        注意：需要调用其他服务获取信息
        """
        return self.agent.execute(task=task)
    
    def query_orders(self, customer_id=None, order_id=None):
        """查询订单"""
        if order_id:
            task = f"调用 查询订单：查询订单号 {order_id}"
        elif customer_id:
            task = f"调用 查询订单：查询客户 {customer_id} 的所有订单"
        else:
            task = "调用 查询订单：查询所有订单"
        
        return self.agent.execute(task=task)
    
    def update_status(self, order_id, new_status):
        """更新订单状态"""
        task = f"""
        调用 更新订单状态：
        - 订单号：{order_id}
        - 新状态：{new_status}
        """
        return self.agent.execute(task=task)
    
    def handle_message(self, message):
        """处理来自其他Agent的消息"""
        return self.agent.execute(task=message)

def main():
    """测试订单Agent"""
    agent = OrderAgent()
    
    # 测试创建订单
    print("创建订单...")
    result = agent.create_order(
        "CUST001",
        [
            {"id": "PROD001", "name": "iPhone 15 Pro", "quantity": 1},
            {"id": "PROD002", "name": "AirPods Pro", "quantity": 2}
        ]
    )
    print(result[:500])

if __name__ == "__main__":
    main()