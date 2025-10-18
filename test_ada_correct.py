#!/usr/bin/env python3
"""
测试@ada自我实现的正确行为：
Agent应该更新自己的knowledge.md，而不是创建其他文件
"""

import sys
from pathlib import Path
import json

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "pim-compiler/react_is_all_you_need"))

from core.react_agent_minimal import ReactAgentMinimal

print("=" * 60)
print("🚀 正确的@ada自我实现测试")
print("=" * 60)

# 创建新的测试Agent
print("\n📚 创建测试Agent...")
test_agent = ReactAgentMinimal(
    work_dir="/tmp/ada_test",
    model="deepseek-chat",
    name="ada_test_agent",
    description="测试ADA自我实现的Agent",
    knowledge_files=[
        "knowledge/agent_driven_architecture.md"  # 包含@ada自我实现
    ],
    max_rounds=50
)

print("\n📋 检查Agent初始状态...")
agent_home = Path.home() / ".agent" / "ada_test_agent"
knowledge_path = agent_home / "knowledge.md"

if knowledge_path.exists():
    initial_content = knowledge_path.read_text(encoding='utf-8')
    print(f"  初始knowledge.md大小: {len(initial_content)}字符")
else:
    print("  ❌ knowledge.md不存在")

print("\n🎯 执行@ada自我实现...")
print("-" * 60)

# 准备正确的任务指令
task = """
执行@ada自我实现契约函数，参数是需求文档：
/Users/guci/robot_projects/book_app/图书管理业务设计文档.md

重要：按照ADA理念，你必须：
1. 读取需求文档
2. 生成知识函数
3. 更新你自己的knowledge.md文件（~/.agent/ada_test_agent/knowledge.md）
4. 不要创建其他文件

记住：
- 你的knowledge.md就是你的"代码"
- 修改knowledge.md就是"自我编程"
- 这是ADA的核心：Agent能够自己实现自己
"""

# 执行任务
result = test_agent.execute(action="execute_task", task=task)

print("\n" + "=" * 60)
print("📊 验证结果")
print("=" * 60)

# 检查knowledge.md是否被更新
if knowledge_path.exists():
    final_content = knowledge_path.read_text(encoding='utf-8')
    print(f"✅ knowledge.md存在")
    print(f"  最终大小: {len(final_content)}字符")

    # 检查是否包含图书管理函数
    if "@borrowBook" in final_content:
        print("✅ 包含@borrowBook函数")
    else:
        print("❌ 未找到@borrowBook函数")

    if "@returnBook" in final_content:
        print("✅ 包含@returnBook函数")
    else:
        print("❌ 未找到@returnBook函数")

    # 统计契约函数数量
    contract_count = final_content.count("契约函数 @")
    print(f"  契约函数数量: {contract_count}个")
else:
    print("❌ knowledge.md未找到")

# 检查是否错误地创建了其他文件
wrong_file = Path("/Users/guci/robot_projects/book_app/book_management_implementation.md")
if wrong_file.exists():
    print("\n⚠️ 警告：Agent错误地创建了其他文件")
    print(f"  错误文件: {wrong_file}")
    print("  应该更新自己的knowledge.md，而不是创建新文件")

print("\n" + "=" * 60)
print("💡 ADA理念检查")
print("=" * 60)

if knowledge_path.exists() and "@borrowBook" in final_content:
    print("✅ Agent成功实现了自我编程")
    print("✅ 知识函数已内化为Agent能力")
    print("✅ 符合ADA的PIM→Code理念")
else:
    print("❌ Agent未能正确执行@ada自我实现")
    print("❌ 应该更新~/.agent/{name}/knowledge.md")
    print("❌ 而不是创建其他文件")

print("\n🎉 测试完成！")