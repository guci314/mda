#!/usr/bin/env python3
"""
Agent Creator - 帮助业务人员创建Agent的元Agent
通过自然语言交互，生成知识文件和可执行的Agent
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal
from core.tools.create_agent_tool import CreateAgentTool
from pathlib import Path
import json
from datetime import datetime

class AgentCreator:
    """Agent创建器 - 元Agent"""
    
    def __init__(self, model="x-ai/grok-code-fast-1"):
        """初始化Agent Creator"""
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Creator本身是一个Agent
        self.creator_agent = ReactAgentMinimal(
            name="learner",
            description="帮助业务人员创建Agent的智能助手",
            work_dir="/tmp/agent_creator",
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            knowledge_files=[
                "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/agent_creator_self_knowledge.md"
            ],
            stateful=False,  # 每次创建都是独立的
            max_rounds=20
        )

        # 添加CreateAgentTool，这样Creator可以创建并直接使用Agent
        create_tool = CreateAgentTool(work_dir="/tmp/agent_creator", parent_agent=self.creator_agent)
        self.creator_agent.append_tool(create_tool)
        
        print("🤖 Agent Creator 已初始化")
        print("=" * 60)
        print("我可以帮您创建各种业务Agent，无需编程知识！")
        print("=" * 60)
    
    def create_from_description(self, business_description):
        """根据业务描述创建Agent"""
        
        # 让Creator Agent理解需求并生成知识文件
        creation_task = f"""
        用户的业务需求：
        {business_description}
        
        请执行以下步骤：
        1. 理解业务需求
        2. 选择合适的模板
        3. 生成完整的知识文件内容
        4. 设计3个测试用例
        5. 返回生成的知识文件和测试用例
        
        输出格式：
        === 知识文件内容 ===
        [完整的markdown格式知识文件]
        === 测试用例 ===
        [测试用例列表]
        """
        
        result = self.creator_agent.execute(task=creation_task)
        
        # 解析结果，提取知识文件内容
        knowledge_content = self._extract_knowledge(result)
        test_cases = self._extract_test_cases(result)
        
        # 生成Agent名称
        agent_name = self._generate_agent_name(business_description)
        
        # 保存知识文件
        knowledge_path = self._save_knowledge_file(agent_name, knowledge_content)
        
        # 创建Agent实例
        agent = self._create_agent_instance(agent_name, knowledge_path)
        
        return {
            "agent": agent,
            "agent_name": agent_name,
            "knowledge_file": knowledge_path,
            "test_cases": test_cases,
            "creation_result": result
        }
    
    def _extract_knowledge(self, result):
        """从Creator的结果中提取知识文件内容"""
        # 简单的提取逻辑，可以根据需要改进
        if "=== 知识文件内容 ===" in result:
            start = result.index("=== 知识文件内容 ===") + len("=== 知识文件内容 ===")
            if "=== 测试用例 ===" in result:
                end = result.index("=== 测试用例 ===")
                return result[start:end].strip()
        return result
    
    def _extract_test_cases(self, result):
        """从Creator的结果中提取测试用例"""
        if "=== 测试用例 ===" in result:
            start = result.index("=== 测试用例 ===") + len("=== 测试用例 ===")
            return result[start:].strip()
        return "暂无测试用例"
    
    def _generate_agent_name(self, description):
        """生成Agent名称"""
        # 简单的名称生成逻辑
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 尝试从描述中提取关键词
        if "订单" in description:
            return f"order_agent_{timestamp}"
        elif "客户" in description or "客服" in description:
            return f"customer_agent_{timestamp}"
        elif "审批" in description:
            return f"approval_agent_{timestamp}"
        elif "数据" in description:
            return f"data_agent_{timestamp}"
        else:
            return f"business_agent_{timestamp}"
    
    def _save_knowledge_file(self, agent_name, content):
        """保存知识文件"""
        # 创建知识文件目录
        knowledge_dir = Path("/tmp/agent_creator/knowledge")
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = knowledge_dir / f"{agent_name}_knowledge.md"
        file_path.write_text(content, encoding='utf-8')
        
        print(f"✅ 知识文件已保存: {file_path}")
        return str(file_path)
    
    def _create_agent_instance(self, agent_name, knowledge_path):
        """创建Agent实例"""
        agent = ReactAgentMinimal(
            name=agent_name,
            description=f"由Agent Creator创建的业务Agent",
            work_dir=f"/tmp/agents/{agent_name}",
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            knowledge_files=[knowledge_path],
            stateful=False,  # 业务Agent通常无状态
            max_rounds=15
        )
        
        print(f"✅ Agent实例已创建: {agent_name}")
        return agent
    
    def test_agent(self, agent, test_case):
        """测试创建的Agent"""
        print(f"\n🧪 测试: {test_case}")
        result = agent.execute(task=test_case)
        return result
    
    def interactive_create(self):
        """交互式创建Agent"""
        print("\n🎯 交互式Agent创建")
        print("-" * 60)
        
        # 收集需求
        print("请回答以下问题来帮助我理解您的需求：\n")
        
        business_type = input("1. 您要创建什么类型的系统？(订单/客服/审批/数据处理/其他): ")
        main_function = input("2. 主要功能是什么？: ")
        
        # 根据类型询问特定问题
        specific_rules = ""
        if "订单" in business_type:
            has_member = input("3. 有会员折扣吗？(是/否): ")
            if has_member.lower() in ['是', 'yes', 'y']:
                vip_discount = input("   VIP折扣是多少？(如0.8表示8折): ")
                specific_rules += f"VIP客户享受{vip_discount}折扣。"
            
            has_promotion = input("4. 有满减活动吗？(是/否): ")
            if has_promotion.lower() in ['是', 'yes', 'y']:
                promotion = input("   满减规则是什么？(如:满1000减100): ")
                specific_rules += f"促销活动：{promotion}。"
        
        elif "客服" in business_type or "客户" in business_type:
            services = input("3. 提供哪些服务？(用逗号分隔): ")
            specific_rules += f"提供的服务：{services}"
        
        elif "审批" in business_type:
            approval_levels = input("3. 审批级别规则是什么？: ")
            specific_rules += f"审批规则：{approval_levels}"
        
        # 构建完整描述
        full_description = f"""
        创建一个{business_type}系统
        主要功能：{main_function}
        {specific_rules}
        """
        
        print("\n" + "=" * 60)
        print("📝 需求总结：")
        print(full_description)
        print("=" * 60)
        
        confirm = input("\n确认创建？(是/否): ")
        if confirm.lower() in ['是', 'yes', 'y']:
            return self.create_from_description(full_description)
        else:
            print("已取消创建")
            return None

def demo_order_agent():
    """演示：创建订单处理Agent"""
    print("\n" + "=" * 60)
    print("📦 演示：创建订单处理Agent")
    print("=" * 60)
    
    creator = AgentCreator()
    
    # 业务描述
    business_description = """
    我需要一个电商订单处理系统：
    1. 能查询客户信息，VIP客户打8折，普通会员9折
    2. 能查询产品价格和库存
    3. 有满减活动：满1000减100，满5000减500
    4. 生成订单号并扣减库存
    5. 订单状态管理（待支付、已支付、已发货、已完成）
    """
    
    print("业务需求：")
    print(business_description)
    print("-" * 60)
    
    # 创建Agent
    print("\n🚀 开始创建Agent...")
    result = creator.create_from_description(business_description)
    
    if result:
        print("\n" + "=" * 60)
        print("✅ Agent创建成功！")
        print(f"Agent名称: {result['agent_name']}")
        print(f"知识文件: {result['knowledge_file']}")
        print("-" * 60)
        
        # 显示测试用例
        print("\n📋 生成的测试用例：")
        print(result['test_cases'])
        
        # 执行测试
        if result['agent']:
            print("\n🧪 执行测试...")
            test_result = creator.test_agent(
                result['agent'],
                "为VIP客户CUST001创建订单，购买2000元的商品"
            )
            print(f"测试结果: {test_result[:500]}...")

def demo_customer_service():
    """演示：创建客户服务Agent"""
    print("\n" + "=" * 60)
    print("👥 演示：创建客户服务Agent")
    print("=" * 60)
    
    creator = AgentCreator()
    
    business_description = """
    创建一个客户服务系统：
    1. 管理客户基本信息
    2. 会员等级管理（普通、银牌、金牌、钻石）
    3. 积分系统（消费1元得1分，1000分升级）
    4. 投诉处理流程
    5. 服务记录跟踪
    """
    
    print("业务需求：")
    print(business_description)
    
    result = creator.create_from_description(business_description)
    
    if result:
        print(f"\n✅ 客服Agent创建成功: {result['agent_name']}")

def main():
    """主函数"""
    print("🌟 Agent Creator - 让业务人员轻松创建Agent")
    print("=" * 60)
    
    mode = input("""
请选择模式：
1. 演示：订单处理Agent
2. 演示：客户服务Agent  
3. 交互式创建（推荐）
4. 自定义描述

选择 (1-4): """)
    
    if mode == "1":
        demo_order_agent()
    elif mode == "2":
        demo_customer_service()
    elif mode == "3":
        creator = AgentCreator()
        result = creator.interactive_create()
        if result:
            print(f"\n✅ 创建成功！Agent: {result['agent_name']}")
    elif mode == "4":
        print("\n请输入您的业务需求描述（输入END结束）：")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)
        
        description = "\n".join(lines)
        creator = AgentCreator()
        result = creator.create_from_description(description)
        
        if result:
            print(f"\n✅ Agent创建成功: {result['agent_name']}")
    else:
        print("无效选择")

if __name__ == "__main__":
    main()