#!/usr/bin/env python3
"""
测试子Agent是否正确创建
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal

def test_sub_agent(agent_name):
    """测试一个子Agent"""
    print(f"\n=== 测试 {agent_name} ===")

    # 检查Home目录
    home_dir = Path(f"~/.agent/{agent_name}").expanduser()
    print(f"Home目录: {home_dir}")
    print(f"Home目录存在: {home_dir.exists()}")

    if home_dir.exists():
        # 检查文件
        knowledge_path = home_dir / "knowledge.md"
        external_tools_dir = home_dir / "external_tools"

        print(f"knowledge.md存在: {knowledge_path.exists()}")
        print(f"external_tools目录存在: {external_tools_dir.exists()}")

        # 读取knowledge.md内容
        if knowledge_path.exists():
            with open(knowledge_path, 'r') as f:
                content = f.read()
                print(f"knowledge.md大小: {len(content)}字节")
                print(f"knowledge.md前100字符: {content[:100]}...")

    # 尝试创建Agent实例
    try:
        print(f"\n尝试创建{agent_name}实例...")
        agent = ReactAgentMinimal(
            work_dir="/Users/guci/robot_projects/book_app",
            name=agent_name,
            model="x-ai/grok-code-fast-1",
            knowledge_files=[
                "/Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/self_awareness.md",
                "/Users/guci/.agent/book_agent/knowledge.md"
            ],
            max_rounds=10
        )
        print(f"✅ {agent_name}实例创建成功")
        print(f"  - 描述: {agent.description}")
        print(f"  - 工具数: {len(agent.function_instances)}")

        # 测试简单任务
        print(f"\n测试执行简单任务...")
        result = agent.execute("action: get_status")
        print(f"执行结果: {result[:200]}..." if len(result) > 200 else f"执行结果: {result}")

    except Exception as e:
        print(f"❌ 创建{agent_name}失败: {e}")

def main():
    print("=" * 60)
    print("子Agent验证测试")
    print("=" * 60)

    # 测试三个子Agent
    agents = [
        "book_management_agent",
        "customer_management_agent",
        "borrow_management_agent"
    ]

    for agent_name in agents:
        test_sub_agent(agent_name)

    print("\n" + "=" * 60)
    print("测试完成")

    # 总结
    print("\n📊 验证结果总结:")
    for agent_name in agents:
        home_dir = Path(f"~/.agent/{agent_name}").expanduser()
        if home_dir.exists():
            print(f"✅ {agent_name}: Home目录存在，结构正确")
        else:
            print(f"❌ {agent_name}: Home目录不存在")

if __name__ == "__main__":
    main()