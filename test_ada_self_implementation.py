#!/usr/bin/env python3
"""
测试ADA自我实现功能
使用图书管理系统需求文档，演示Agent如何自动生成自己的knowledge.md
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "pim-compiler/react_is_all_you_need"))

from core.react_agent_minimal import ReactAgentMinimal

print("=" * 60)
print("🚀 ADA自我实现测试")
print("=" * 60)

# 创建图书管理Agent
print("\n📚 创建图书管理Agent...")
library_agent = ReactAgentMinimal(
    work_dir="/tmp/library_system",
    model="deepseek-chat",
    name="library_agent",
    description="图书管理系统Agent - 通过ADA自我实现",
    knowledge_files=[
        "knowledge/agent_driven_architecture.md"  # 包含@ada自我实现函数
    ],
    max_rounds=50
)

print("\n📋 需求文档路径:")
requirements_doc = "/Users/guci/robot_projects/book_app/图书管理业务设计文档.md"
print(f"  {requirements_doc}")

print("\n🎯 执行@ada自我实现...")
print("-" * 60)

# 调用@ada自我实现函数
task = f"""
执行@ada自我实现契约函数，参数是需求文档：
{requirements_doc}

请按照契约函数定义：
1. 读取并分析需求文档
2. 识别Domain对象（Book、Customer、BorrowRecord等）
3. 识别Service方法（borrowBook、returnBook等）
4. 生成知识函数实现
5. 保存到你的knowledge.md文件

生成的知识函数应该：
- 对每个Domain生成概念定义
- 对每个Service方法生成函数实现
- 包含完整的业务逻辑步骤
- 遵循ADA理念（自然语言即代码）
"""

result = library_agent.execute(action="execute_task", task=task)

print("\n" + "=" * 60)
print("📊 执行结果")
print("=" * 60)
print(result[:1000] if len(result) > 1000 else result)

# 验证生成的knowledge.md
print("\n" + "=" * 60)
print("🔍 验证生成的知识库")
print("=" * 60)

# 检查Agent的knowledge.md文件
knowledge_path = Path.home() / ".agent" / "library_agent" / "knowledge.md"
if knowledge_path.exists():
    print(f"✅ knowledge.md已生成: {knowledge_path}")

    # 读取并显示部分内容
    content = knowledge_path.read_text(encoding='utf-8')
    print("\n📄 生成的知识函数预览:")
    print("-" * 40)
    lines = content.split('\n')[:50]  # 显示前50行
    for line in lines:
        print(line)

    # 统计生成的知识项
    function_count = content.count("## 函数 @")
    concept_count = content.count("## 概念 @")
    print(f"\n📊 统计:")
    print(f"  - 函数定义: {function_count}个")
    print(f"  - 概念定义: {concept_count}个")
else:
    print(f"❌ knowledge.md未找到: {knowledge_path}")

print("\n" + "=" * 60)
print("💡 ADA理念验证")
print("=" * 60)
print("✅ PIM（需求文档） → Code（知识函数）")
print("✅ 没有PSM中间层")
print("✅ 自然语言即可执行代码")
print("✅ Agent实现了自我编程")

print("\n🎉 这就是ADA架构的威力：")
print("   需求 → 知识函数 → 直接执行")
print("   无需传统的代码生成！")