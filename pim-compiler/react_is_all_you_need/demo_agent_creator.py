#!/usr/bin/env python3
"""
Agent Creator 演示程序
展示如何使用Agent Creator来创建业务Agent
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from agent_creator import AgentCreator

def demo_simple():
    """简单演示：创建一个订单处理Agent"""
    print("\n" + "="*60)
    print("🎯 Agent Creator 简单演示")
    print("="*60)
    
    # 创建Agent Creator实例
    creator = AgentCreator()  # 使用默认的grok模型
    
    # 业务需求描述
    business_description = """
    我需要一个简单的订单处理系统：
    1. VIP客户打8折
    2. 普通会员打9折
    3. 满1000减100的促销活动
    """
    
    print("📝 业务需求：")
    print(business_description)
    print("-" * 60)
    
    # 创建Agent
    print("\n🚀 正在创建Agent...")
    result = creator.create_from_description(business_description)
    
    if result:
        print("\n✅ Agent创建成功！")
        print(f"   Agent名称: {result['agent_name']}")
        print(f"   知识文件: {result['knowledge_file']}")
        
        # 测试创建的Agent
        if result['agent']:
            print("\n🧪 测试Agent功能...")
            test_case = "为VIP客户创建订单，购买1200元的商品"
            print(f"   测试用例: {test_case}")
            
            test_result = creator.test_agent(result['agent'], test_case)
            print(f"\n   测试结果: {test_result[:300]}...")
    
    return result

def demo_interactive():
    """交互式演示：通过对话创建Agent"""
    print("\n" + "="*60)
    print("💬 Agent Creator 交互式演示")
    print("="*60)
    
    creator = AgentCreator()  # 使用默认的grok模型
    
    # 启动交互式创建
    result = creator.interactive_create()
    
    if result:
        print("\n🎉 交互式创建完成！")
        print(f"   生成的Agent: {result['agent_name']}")

def demo_custom():
    """自定义演示：创建特定业务的Agent"""
    print("\n" + "="*60)
    print("🏭 创建库存管理Agent")
    print("="*60)
    
    creator = AgentCreator()  # 使用默认的grok模型
    
    # 库存管理需求
    business_description = """
    创建一个库存管理系统：
    1. 实时跟踪商品库存数量
    2. 库存低于10件时自动预警
    3. 支持入库和出库操作
    4. 记录所有库存变动历史
    5. 生成库存报表
    """
    
    print("业务需求：")
    print(business_description)
    
    result = creator.create_from_description(business_description)
    
    if result:
        print(f"\n✅ 库存管理Agent创建成功: {result['agent_name']}")
        
        # 测试库存查询
        if result['agent']:
            test_result = creator.test_agent(
                result['agent'],
                "查询iPhone的当前库存"
            )
            print(f"库存查询结果: {test_result[:200]}...")

def main():
    """主函数"""
    print("🌟 Agent Creator 演示程序")
    print("="*60)
    print("本演示展示如何使用Agent Creator创建各种业务Agent")
    print("="*60)
    
    print("\n请选择演示模式：")
    print("1. 简单演示 - 创建订单处理Agent")
    print("2. 交互式演示 - 通过对话创建Agent")
    print("3. 自定义演示 - 创建库存管理Agent")
    print("4. 运行所有演示")
    
    choice = input("\n选择 (1-4，默认1): ").strip() or "1"
    
    if choice == "1":
        demo_simple()
    elif choice == "2":
        demo_interactive()
    elif choice == "3":
        demo_custom()
    elif choice == "4":
        # 运行所有非交互式演示
        demo_simple()
        print("\n" + "="*60)
        input("按Enter继续...")
        demo_custom()
    else:
        print("无效选择，运行默认演示")
        demo_simple()
    
    print("\n" + "="*60)
    print("✨ 演示完成！")
    print("="*60)
    print("\n说明：")
    print("- Agent Creator可以根据自然语言描述创建Agent")
    print("- 生成的知识文件使用纯自然语言，业务人员可以理解")
    print("- 创建的Agent可以立即执行和验证")
    print("- 这实现了从MDA到ADA的跨越：可执行的模型")

if __name__ == "__main__":
    main()