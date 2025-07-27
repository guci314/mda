#!/usr/bin/env python3
"""
验证 Agent CLI v3 是否正常工作
"""

import sys
from pathlib import Path

# 添加 pim-compiler 到 Python 路径
pim_compiler_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(pim_compiler_path))

# 从 agent_cli 导入
from agent_cli import AgentCLI, LLMConfig, __version__
from agent_cli import TaskClassifier, TaskType

print(f"Agent CLI 版本: {__version__}")
print(f"默认 AgentCLI 类: {AgentCLI.__name__}")
print("-" * 60)

# 测试任务分类器
classifier = TaskClassifier()
test_tasks = [
    "pim-compiler的执行流程是什么？",
    "创建一个 Python 程序 hello.py",
    "优化代码性能"
]

print("任务分类测试:")
for task in test_tasks:
    task_type, confidence = classifier.classify(task)
    print(f"- '{task[:30]}...' -> {task_type.value} (置信度: {confidence:.2f})")

print("\n✅ Agent CLI v3 导入和基本功能正常！")

# 提示用户如何使用
print("\n使用示例:")
print("1. Python 代码:")
print("   from agent_cli import AgentCLI, LLMConfig")
print("   config = LLMConfig.from_env('deepseek')")
print("   agent = AgentCLI(llm_config=config)  # 这是 v3")
print("")
print("2. 命令行:")
print("   python -m agent_cli run '任务描述'  # 默认使用 v3")
print("   python -m agent_cli run '任务描述' --use-v2  # 使用 v2")