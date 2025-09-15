#!/usr/bin/env python3
"""
产品服务Agent
负责商品信息、价格管理
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal
import json

class ProductAgent:
    """产品服务Agent"""
    
    def __init__(self, model="x-ai/grok-code-fast-1"):
        """初始化产品Agent"""
        self.agent = ReactAgentMinimal(
            work_dir="/tmp/microservices/products",
            model=model,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/product_service/product_knowledge.md"
            ],
            max_rounds=20
        )
        
        # 初始化产品数据
        self._init_products()
    
    def _init_products(self):
        """初始化产品数据"""
        initial_products = {
            "PROD001": {
                "name": "iPhone 15 Pro",
                "price": 8999,
                "category": "手机",
                "description": "苹果最新旗舰手机，A17 Pro芯片",
                "status": "active",
                "created_at": "2024-01-01",
                "updated_at": "2024-01-15"
            },
            "PROD002": {
                "name": "AirPods Pro",
                "price": 1999,
                "category": "耳机",
                "description": "主动降噪无线耳机",
                "status": "active",
                "created_at": "2024-01-01",
                "updated_at": "2024-01-10"
            },
            "PROD003": {
                "name": "MacBook Pro",
                "price": 15999,
                "category": "电脑",
                "description": "14英寸专业笔记本电脑",
                "status": "active",
                "created_at": "2024-01-01",
                "updated_at": "2024-01-20"
            },
            "PROD004": {
                "name": "iPad Air",
                "price": 4999,
                "category": "平板",
                "description": "轻薄高性能平板电脑",
                "status": "active",
                "created_at": "2024-01-01",
                "updated_at": "2024-01-05"
            }
        }
        
        # 只在文件不存在时初始化
        product_file = "/tmp/microservices/products/products.json"
        if not os.path.exists(product_file):
            os.makedirs(os.path.dirname(product_file), exist_ok=True)
            with open(product_file, 'w') as f:
                json.dump(initial_products, f, indent=2, ensure_ascii=False)
    
    def get_product_info(self, product_ids):
        """获取商品信息"""
        task = f"""
        调用 获取商品信息：
        商品ID列表：{product_ids}
        """
        return self.agent.execute(task=task)
    
    def get_prices(self, product_ids):
        """获取商品价格"""
        task = f"""
        调用 获取商品价格：
        商品ID列表：{product_ids}
        """
        return self.agent.execute(task=task)
    
    def update_price(self, product_id, new_price):
        """更新商品价格"""
        task = f"""
        调用 更新商品价格：
        - 商品ID：{product_id}
        - 新价格：{new_price}
        """
        return self.agent.execute(task=task)
    
    def add_product(self, product_info):
        """添加新商品"""
        task = f"""
        调用 添加新商品：
        商品信息：{json.dumps(product_info, ensure_ascii=False)}
        """
        return self.agent.execute(task=task)
    
    def handle_message(self, message):
        """处理来自其他Agent的消息"""
        return self.agent.execute(task=message)

def main():
    """测试产品Agent"""
    agent = ProductAgent()
    
    # 测试获取商品信息
    print("获取商品信息...")
    result = agent.get_product_info(["PROD001", "PROD002"])
    print(result[:500])

if __name__ == "__main__":
    main()