#!/usr/bin/env python3
"""
协作器Agent
使用子Agent作为自然语言函数
实现真正的Agent网络架构
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal
from microservices.order_service.order_agent import OrderAgent
from microservices.inventory_service.inventory_agent import InventoryAgent
from microservices.product_service.product_agent import ProductAgent
from microservices.customer_service.customer_agent import CustomerAgent

class OrchestratorAgent:
    """协作器Agent - 使用其他Agent作为自然语言函数"""
    
    def __init__(self, model="x-ai/grok-code-fast-1"):
        """初始化协作器Agent"""
        # 初始化子Agent（作为外部函数）
        self.order_agent = OrderAgent(model=model)
        self.inventory_agent = InventoryAgent(model=model)
        self.product_agent = ProductAgent(model=model)
        self.customer_agent = CustomerAgent(model=model)
        
        # 初始化协作器Agent本身
        self.agent = ReactAgentMinimal(
            work_dir="/tmp/microservices/orchestrator",
            model=model,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/orchestrator_knowledge.md"
            ],
            max_rounds=30
        )
        
        # 注册子Agent为可调用的函数
        self._register_agent_functions()
    
    def _register_agent_functions(self):
        """将子Agent注册为自然语言函数"""
        # 在知识文件中描述如何调用这些Agent
        pass
    
    def _call_order_agent(self, message):
        """调用订单Agent"""
        return self.order_agent.handle_message(message)
    
    def _call_inventory_agent(self, message):
        """调用库存Agent"""
        return self.inventory_agent.handle_message(message)
    
    def _call_product_agent(self, message):
        """调用产品Agent"""
        return self.product_agent.handle_message(message)
    
    def _call_customer_agent(self, message):
        """调用客户Agent"""
        return self.customer_agent.handle_message(message)
    
    def process_request(self, request):
        """
        处理业务请求
        协作器Agent理解请求，协调子Agent完成任务
        """
        # 构建任务，包含可用的子Agent信息
        task = f"""
        处理以下业务请求：
        {request}
        
        你可以通过ExecuteCommand调用以下子Agent：
        1. 订单Agent: python -c "from orchestrator_agent import OrchestratorAgent; o=OrchestratorAgent(); print(o._call_order_agent('你的消息'))"
        2. 库存Agent: python -c "from orchestrator_agent import OrchestratorAgent; o=OrchestratorAgent(); print(o._call_inventory_agent('你的消息'))"
        3. 产品Agent: python -c "from orchestrator_agent import OrchestratorAgent; o=OrchestratorAgent(); print(o._call_product_agent('你的消息'))"
        4. 客户Agent: python -c "from orchestrator_agent import OrchestratorAgent; o=OrchestratorAgent(); print(o._call_customer_agent('你的消息'))"
        
        请协调这些Agent完成任务。
        """
        
        return self.agent.execute(task=task)
    
    def create_order_workflow(self, customer_id, items):
        """
        创建订单工作流
        展示Agent协作
        """
        task = f"""
        执行创建订单工作流：
        
        客户ID: {customer_id}
        商品列表: {items}
        
        工作流步骤：
        1. 调用客户Agent获取客户信息和会员折扣
        2. 调用产品Agent获取商品价格
        3. 调用库存Agent检查库存
        4. 如果库存充足，调用订单Agent创建订单
        5. 调用库存Agent扣减库存
        6. 返回订单创建结果
        
        使用知识文件中的自然语言函数完成这个工作流。
        """
        
        return self.agent.execute(task=task)

def main():
    """测试协作器Agent"""
    print("🌟 协作器Agent演示")
    print("=" * 60)
    
    orchestrator = OrchestratorAgent()
    
    # 测试创建订单工作流
    print("\n📦 创建订单工作流...")
    result = orchestrator.create_order_workflow(
        customer_id="CUST001",
        items=[
            {"id": "PROD001", "name": "iPhone 15 Pro", "quantity": 1},
            {"id": "PROD002", "name": "AirPods Pro", "quantity": 2}
        ]
    )
    print(result[:500])

if __name__ == "__main__":
    main()