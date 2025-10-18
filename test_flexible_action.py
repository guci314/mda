#!/usr/bin/env python3
"""测试Agent的灵活调用方式"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "pim-compiler/react_is_all_you_need"))

from core.react_agent_minimal import ReactAgentMinimal

# 创建测试Agent
agent = ReactAgentMinimal(
    work_dir="/tmp/test_flexible",
    model="deepseek-chat",
    name="test_agent",
    knowledge_files=[]
)

print("=" * 60)
print("测试Agent的灵活调用方式")
print("=" * 60)

print("\n✅ 测试1：使用位置参数（最简洁）")
try:
    # 注意：这会真正执行任务，但我们只是测试参数传递
    result = agent.execute("hi")
    print(f"位置参数方式工作正常")
    print(f"结果开始：{result[:100]}...")
except Exception as e:
    print(f"异常：{e}")

print("\n✅ 测试2：使用关键字参数task")
try:
    result = agent.execute(task="hello")
    print(f"关键字参数task方式工作正常")
    print(f"结果开始：{result[:100]}...")
except Exception as e:
    print(f"异常：{e}")

print("\n✅ 测试3：使用完整的action + task")
try:
    result = agent.execute(action="execute_task", task="test")
    print(f"完整action方式工作正常")
    print(f"结果开始：{result[:100]}...")
except Exception as e:
    print(f"异常：{e}")

print("\n✅ 测试4：使用其他action（get_status）")
result = agent.execute(action="get_status")
print(f"get_status结果：{result[:100]}...")

print("\n✅ 测试5：不提供任何参数（应该报错）")
result = agent.execute()
print(f"结果：{result}")

print("\n" + "=" * 60)
print("测试完成！")
print("现在支持的调用方式：")
print("1. agent.execute('任务')           # 最简洁（位置参数）")
print("2. agent.execute(task='任务')      # 关键字参数")
print("3. agent.execute(action='execute_task', task='任务')  # 完整方式")
print("4. agent.execute(action='get_status')  # 其他操作")
print("\nOpenAI Schema中action仍然是必需参数")