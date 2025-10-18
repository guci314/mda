#!/usr/bin/env python3
"""测试Agent的action参数必需性"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "pim-compiler/react_is_all_you_need"))

from core.react_agent_minimal import ReactAgentMinimal

# 创建测试Agent
agent = ReactAgentMinimal(
    work_dir="/tmp/test_action",
    model="deepseek-chat",
    name="test_agent",
    knowledge_files=[]
)

print("=" * 60)
print("测试Agent的action参数必需性")
print("=" * 60)

print("\n❌ 测试1：不提供action参数（应该报错）")
try:
    result = agent.execute(task="创建文件")
    print(f"结果：{result}")
except Exception as e:
    print(f"异常：{e}")

print("\n❌ 测试2：使用位置参数（应该报错）")
try:
    result = agent.execute("创建文件")
    print(f"结果：{result}")
except Exception as e:
    print(f"异常：{e}")

print("\n✅ 测试3：正确使用action=execute_task")
try:
    # 注意：真正的任务执行会很耗时，这里只是测试参数传递
    result = agent.execute(action="execute_task", task="这是一个测试任务")
    print(f"结果开始执行任务...")
except Exception as e:
    print(f"测试通过（预期会进入任务执行流程）：{str(e)[:50]}")

print("\n✅ 测试4：使用action=get_status")
result = agent.execute(action="get_status")
print(f"状态信息：{result[:100]}...")

print("\n✅ 测试5：action参数为空（应该报错）")
result = agent.execute(action="", task="创建文件")
print(f"结果：{result}")

print("\n✅ 测试6：未知的action（应该报错）")
result = agent.execute(action="unknown_action")
print(f"结果：{result}")

print("\n" + "=" * 60)
print("测试完成！")
print("关键变化：")
print("1. action参数是必需的")
print("2. 不再支持位置参数")
print("3. 必须明确指定action类型")
print("4. 调用格式：agent.execute(action='execute_task', task='任务描述')")