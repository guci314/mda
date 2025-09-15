#!/usr/bin/env python3
"""
真正的Agent网络架构
每个服务都是 ReactAgentMinimal + 知识文件
协作器通过add_function将子Agent注册为函数
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal

class AgentNetwork:
    """Agent网络 - 真正的分布式智能体架构"""
    
    def __init__(self, model="x-ai/grok-code-fast-1"):
        """初始化Agent网络"""
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        print("🌟 初始化Agent网络...")
        print("=" * 60)
        
        # 创建各个服务Agent（都是ReactAgentMinimal + 知识文件）
        self.agents = {}
        self._create_service_agents()
        
        # 创建协作器Agent
        self._create_orchestrator_agent()
        
        print("=" * 60)
        print("✅ Agent网络已就绪\n")
    
    def _create_service_agents(self):
        """创建服务Agent - 每个都是独立的ReactAgentMinimal实例"""
        
        # 客户服务Agent
        print("👥 创建客户服务Agent...")
        self.agents['customer'] = ReactAgentMinimal(
            name="调用客户服务",
            description="向客户服务Agent发送消息并获取响应",
            work_dir="/tmp/microservices/customers",
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/customer_service/customer_knowledge.md"
            ],
            max_rounds=20
        )
        
        # 产品服务Agent
        print("🛍️ 创建产品服务Agent...")
        self.agents['product'] = ReactAgentMinimal(
            name="调用产品服务",
            description="向产品服务Agent发送消息并获取响应",
            work_dir="/tmp/microservices/products",
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/product_service/product_knowledge.md"
            ],
            max_rounds=20
        )
        
        # 库存服务Agent
        print("📊 创建库存服务Agent...")
        self.agents['inventory'] = ReactAgentMinimal(
            name="调用库存服务",
            description="向库存服务Agent发送消息并获取响应",
            work_dir="/tmp/microservices/inventory",
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/inventory_service/inventory_knowledge.md"
            ],
            max_rounds=20
        )
        
        # 订单服务Agent
        print("📦 创建订单服务Agent...")
        self.agents['order'] = ReactAgentMinimal(
            name="调用订单服务",
            description="向订单服务Agent发送消息并获取响应",
            work_dir="/tmp/microservices/orders",
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/order_service/order_knowledge.md"
            ],
            max_rounds=20
        )
    
    def _create_orchestrator_agent(self):
        """创建协作器Agent并注册子Agent为函数"""
        
        print("\n🎯 创建协作器Agent...")
        self.orchestrator = ReactAgentMinimal(
            work_dir="/tmp/microservices/orchestrator",
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/microservices/orchestrator_network_knowledge.md"
            ],
            max_rounds=30
        )
        
        # 将子Agent注册为协作器的函数
        print("📌 注册子Agent为自然语言函数...")
        
        # 直接添加子Agent作为函数（Agent本身就是Function）
        self.orchestrator.add_function(self.agents['customer'])
        self.orchestrator.add_function(self.agents['product'])
        self.orchestrator.add_function(self.agents['inventory'])
        self.orchestrator.add_function(self.agents['order'])
        
        print("✅ 子Agent已注册为函数")
    
    def process_business_request(self, request):
        """处理业务请求 - 协作器自主协调子Agent"""
        return self.orchestrator.execute(task=request)
    
    def create_order_workflow(self, customer_id, items):
        """创建订单工作流"""
        task = f"""
        为客户 {customer_id} 创建订单，购买以下商品：
        {items}
        
        请协调各个服务Agent完成订单创建流程：
        1. 向客户服务查询客户信息和会员折扣
        2. 向产品服务查询商品价格
        3. 向库存服务检查库存
        4. 向订单服务创建订单
        5. 向库存服务扣减库存
        
        使用你的自然语言函数完成这个工作流。
        """
        
        return self.orchestrator.execute(task=task)

def demonstrate_agent_network():
    """演示Agent网络的威力"""
    print("\n🚀 Agent网络架构演示")
    print("=" * 60)
    print("架构特点：")
    print("  • 每个服务 = ReactAgentMinimal + 知识文件")
    print("  • 没有CustomerAgent等类，全是统一的Agent")
    print("  • 协作器通过add_function注册子Agent")
    print("  • 真正的自然语言函数调用")
    print("=" * 60)
    
    # 创建Agent网络
    network = AgentNetwork()
    
    # 演示1：简单请求
    print("\n📝 演示1：查询客户信息")
    print("-" * 40)
    result = network.process_business_request(
        "查询客户CUST001的信息和会员等级"
    )
    print(f"结果：{result[:300]}...")
    
    # 演示2：复杂工作流
    print("\n📝 演示2：创建订单工作流")
    print("-" * 40)
    items = [
        {"id": "PROD001", "name": "iPhone 15 Pro", "quantity": 1},
        {"id": "PROD002", "name": "AirPods Pro", "quantity": 2}
    ]
    result = network.create_order_workflow("CUST001", items)
    print(f"结果：{result[:500]}...")
    
    # 演示3：展示架构优势
    print("\n" + "=" * 60)
    print("🎯 架构优势")
    print("=" * 60)
    
    print("""
1. **统一性**：所有服务都是ReactAgentMinimal
   - 无需为每个服务写类
   - 统一的Agent行为
   
2. **灵活性**：通过知识文件定义行为
   - 修改知识文件即可改变服务行为
   - 无需修改代码
   
3. **可组合性**：Agent可以自由组合
   - add_function动态注册
   - 运行时决定调用关系
   
4. **分布式**：每个Agent独立运行
   - 可以部署在不同机器
   - 通过消息通信
   
5. **智能协作**：自然语言驱动
   - 理解意图而非执行命令
   - 自主决策和错误处理
    """)
    
    print("\n" + "=" * 60)
    print("✨ 这就是真正的Agent网络架构！")
    print("=" * 60)

def main():
    """主函数"""
    try:
        demonstrate_agent_network()
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()