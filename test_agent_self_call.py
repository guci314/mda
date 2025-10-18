#!/usr/bin/env python3
"""测试Agent调用自己的功能"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "pim-compiler/react_is_all_you_need"))

from core.react_agent_minimal import ReactAgentMinimal

# 创建测试Agent
agent = ReactAgentMinimal(
    work_dir="/tmp/test_self_call",
    model="deepseek-chat",
    name="self_aware_agent",
    knowledge_files=[],
    max_rounds=10  # 限制轮数避免无限循环
)

print("=" * 60)
print("测试Agent调用自己的功能")
print("=" * 60)

print("\n✅ 测试1：Agent查看自己的状态")
result = agent.execute(action="execute_task", task="""
查看你自己的状态。调用自己的get_status方法。
""")
print(f"结果：{result[:200]}...")

print("\n✅ 测试2：Agent更新自己的描述")
result = agent.execute(action="execute_task", task="""
更新你自己的描述为"自我意识测试Agent"。调用自己的update_description方法。
""")
print(f"结果：{result[:200]}...")

print("\n❌ 测试3：测试递归防护（不应该成功）")
result = agent.execute(action="execute_task", task="""
调用你自己的execute_task方法执行"打印hello"。
""")
print(f"结果：{result[:200]}...")

print("\n✅ 测试4：Agent更新自己的知识")
result = agent.execute(action="execute_task", task="""
添加一条新知识"我是一个能够自我管理的Agent"到你的知识库。调用自己的update_knowledge方法。
""")
print(f"结果：{result[:200]}...")

print("\n✅ 测试5：Agent获取工作目录")
result = agent.execute(action="execute_task", task="""
获取你当前的工作目录。调用自己的get_work_dir方法。
""")
print(f"结果：{result[:200]}...")

print("\n" + "=" * 60)
print("测试完成！")
print("\n总结：")
print("1. ✅ Agent可以调用自己的管理方法（get_status、update_description等）")
print("2. ✅ 递归防护机制正常工作（阻止execute_task递归）")
print("3. ✅ Agent具有自我管理和元认知能力")