#!/usr/bin/env python3
"""
测试子Agent的独立性和完备性
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal

def test_agent_independence():
    """测试子Agent是否真正独立"""

    print("=" * 60)
    print("子Agent独立性测试")
    print("=" * 60)

    # 1. 检查知识文件大小
    print("\n1. 知识文件完备性检查")
    print("-" * 40)

    agents = [
        ("book_agent", "父Agent"),
        ("book_management_agent", "图书管理子Agent"),
        ("customer_management_agent", "客户管理子Agent"),
        ("borrow_management_agent", "借阅管理子Agent")
    ]

    knowledge_sizes = {}
    for agent_name, desc in agents:
        knowledge_path = Path(f"~/.agent/{agent_name}/knowledge.md").expanduser()
        if knowledge_path.exists():
            with open(knowledge_path, 'r') as f:
                content = f.read()
                lines = len(content.splitlines())
                knowledge_sizes[agent_name] = {
                    'size': len(content),
                    'lines': lines,
                    'desc': desc
                }
                print(f"{desc:20} | {lines:5}行 | {len(content):7}字节")

                # 检查是否包含知识函数
                has_functions = '@' in content and '###' in content
                print(f"  包含知识函数: {'✅' if has_functions else '❌'}")

    # 2. 独立性判断
    print("\n2. 独立性分析")
    print("-" * 40)

    parent_size = knowledge_sizes.get('book_agent', {}).get('lines', 0)

    for agent_name in ['book_management_agent', 'customer_management_agent', 'borrow_management_agent']:
        if agent_name in knowledge_sizes:
            agent_info = knowledge_sizes[agent_name]
            lines = agent_info['lines']

            # 判断标准：子Agent的knowledge.md应该有实质内容（至少50行）
            if lines < 50:
                print(f"❌ {agent_info['desc']}: 知识不完备（仅{lines}行）")
                print(f"   需要继承父Agent的{parent_size}行知识")
            else:
                print(f"✅ {agent_info['desc']}: 知识完备（{lines}行）")

    # 3. 测试独立执行（不加载父Agent知识）
    print("\n3. 独立执行测试")
    print("-" * 40)

    test_agent = "book_management_agent"
    print(f"测试{test_agent}的独立执行能力...")

    try:
        # 只使用子Agent自己的knowledge.md
        agent = ReactAgentMinimal(
            name=test_agent,
            work_dir="/Users/guci/robot_projects/book_app",
            model="deepseek-chat",  # 使用可用的模型
            knowledge_files=[
                f"/Users/guci/.agent/{test_agent}/knowledge.md"  # 只用自己的知识
            ],
            max_rounds=5
        )

        print("✅ Agent初始化成功")

        # 测试执行图书管理任务
        result = agent.execute("添加一本新图书：《深度学习》，作者：Ian Goodfellow")

        if "不知道" in result or "无法" in result or "没有" in result:
            print(f"❌ 执行失败：Agent缺少必要的知识")
            print(f"   结果: {result[:200]}")
        else:
            print(f"✅ 执行成功")
            print(f"   结果: {result[:200]}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")

    # 4. 总结
    print("\n" + "=" * 60)
    print("测试结论")
    print("=" * 60)

    all_independent = True
    for agent_name in ['book_management_agent', 'customer_management_agent', 'borrow_management_agent']:
        if agent_name in knowledge_sizes:
            lines = knowledge_sizes[agent_name]['lines']
            if lines < 50:
                all_independent = False
                break

    if all_independent:
        print("✅ 所有子Agent都具备独立性和完备性")
    else:
        print("❌ 子Agent不独立，需要修复")
        print("\n修复建议：")
        print("1. 在创建子Agent时，将父Agent的knowledge.md内容复制到子Agent")
        print("2. 添加子Agent的专门知识函数")
        print("3. 确保子Agent可以独立执行任务，不依赖运行时加载")

    return all_independent


if __name__ == "__main__":
    result = test_agent_independence()
    sys.exit(0 if result else 1)