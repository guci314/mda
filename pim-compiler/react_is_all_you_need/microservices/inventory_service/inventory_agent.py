#!/usr/bin/env python3
"""
库存服务Agent
负责库存的查询、扣减、补充等操作
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal
import json

class InventoryAgent:
    """库存服务Agent"""
    
    def __init__(self, model="x-ai/grok-code-fast-1"):
        """初始化库存Agent"""
        self.agent = ReactAgentMinimal(
            work_dir="/tmp/microservices/inventory",
            model=model,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/inventory_service/inventory_knowledge.md"
            ],
            max_rounds=20
        )
        
        # 初始化库存数据
        self._init_stock()
    
    def _init_stock(self):
        """初始化库存数据"""
        initial_stock = {
            "PROD001": {
                "name": "iPhone 15 Pro",
                "stock": 50,
                "reserved": 0,
                "available": 50,
                "alert_threshold": 10
            },
            "PROD002": {
                "name": "AirPods Pro",
                "stock": 100,
                "reserved": 0,
                "available": 100,
                "alert_threshold": 20
            },
            "PROD003": {
                "name": "MacBook Pro",
                "stock": 30,
                "reserved": 0,
                "available": 30,
                "alert_threshold": 5
            },
            "PROD004": {
                "name": "iPad Air",
                "stock": 40,
                "reserved": 0,
                "available": 40,
                "alert_threshold": 10
            }
        }
        
        # 只在文件不存在时初始化
        stock_file = "/tmp/microservices/inventory/stock.json"
        if not os.path.exists(stock_file):
            os.makedirs(os.path.dirname(stock_file), exist_ok=True)
            with open(stock_file, 'w') as f:
                json.dump(initial_stock, f, indent=2, ensure_ascii=False)
    
    def check_stock(self, items):
        """检查库存"""
        task = f"""
        调用 检查库存：
        商品列表：{json.dumps(items, ensure_ascii=False)}
        """
        return self.agent.execute(task=task)
    
    def deduct_stock(self, items):
        """扣减库存"""
        task = f"""
        调用 扣减库存：
        商品列表：{json.dumps(items, ensure_ascii=False)}
        """
        return self.agent.execute(task=task)
    
    def replenish_stock(self, product_id, quantity):
        """补充库存"""
        task = f"""
        调用 补充库存：
        - 商品ID：{product_id}
        - 补充数量：{quantity}
        """
        return self.agent.execute(task=task)
    
    def query_stock(self, product_ids=None):
        """查询库存"""
        if product_ids:
            task = f"调用 查询库存：商品ID列表 {product_ids}"
        else:
            task = "调用 查询库存：查询所有商品库存"
        
        return self.agent.execute(task=task)
    
    def handle_message(self, message):
        """处理来自其他Agent的消息"""
        return self.agent.execute(task=message)

def main():
    """测试库存Agent"""
    agent = InventoryAgent()
    
    # 测试查询库存
    print("查询库存...")
    result = agent.query_stock()
    print(result[:500])

if __name__ == "__main__":
    main()