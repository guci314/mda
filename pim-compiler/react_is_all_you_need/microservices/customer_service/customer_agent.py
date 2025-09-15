#!/usr/bin/env python3
"""
客户服务Agent
负责客户信息、会员等级、优惠管理
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal
import json

class CustomerAgent:
    """客户服务Agent"""
    
    def __init__(self, model="x-ai/grok-code-fast-1"):
        """初始化客户Agent"""
        self.agent = ReactAgentMinimal(
            work_dir="/tmp/microservices/customers",
            model=model,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/customer_service/customer_knowledge.md"
            ],
            max_rounds=20
        )
        
        # 初始化客户数据
        self._init_customers()
    
    def _init_customers(self):
        """初始化客户数据"""
        initial_customers = {
            "CUST001": {
                "name": "张三",
                "phone": "13800138000",
                "address": "北京市朝阳区建国路88号",
                "level": "VIP",
                "registered_at": "2023-01-01",
                "total_spent": 25000,
                "points": 2500
            },
            "CUST002": {
                "name": "李四",
                "phone": "13900139000",
                "address": "上海市浦东新区陆家嘴",
                "level": "普通会员",
                "registered_at": "2023-06-15",
                "total_spent": 8000,
                "points": 800
            },
            "CUST003": {
                "name": "王五",
                "phone": "13700137000",
                "address": "广州市天河区珠江新城",
                "level": "非会员",
                "registered_at": "2024-01-01",
                "total_spent": 1000,
                "points": 100
            }
        }
        
        # 只在文件不存在时初始化
        customer_file = "/tmp/microservices/customers/customers.json"
        if not os.path.exists(customer_file):
            os.makedirs(os.path.dirname(customer_file), exist_ok=True)
            with open(customer_file, 'w') as f:
                json.dump(initial_customers, f, indent=2, ensure_ascii=False)
    
    def get_customer_info(self, customer_id):
        """获取客户信息"""
        task = f"""
        调用 获取客户信息：
        客户ID：{customer_id}
        """
        return self.agent.execute(task=task)
    
    def get_discount(self, customer_id):
        """获取客户折扣"""
        task = f"""
        调用 获取客户折扣：
        客户ID：{customer_id}
        """
        return self.agent.execute(task=task)
    
    def register_customer(self, customer_info):
        """注册新客户"""
        task = f"""
        调用 注册新客户：
        客户信息：{json.dumps(customer_info, ensure_ascii=False)}
        """
        return self.agent.execute(task=task)
    
    def update_level(self, customer_id, new_level):
        """更新会员等级"""
        task = f"""
        调用 更新会员等级：
        - 客户ID：{customer_id}
        - 新等级：{new_level}
        """
        return self.agent.execute(task=task)
    
    def handle_message(self, message):
        """处理来自其他Agent的消息"""
        return self.agent.execute(task=message)

def main():
    """测试客户Agent"""
    agent = CustomerAgent()
    
    # 测试获取客户信息
    print("获取客户信息...")
    result = agent.get_customer_info("CUST001")
    print(result[:500])

if __name__ == "__main__":
    main()