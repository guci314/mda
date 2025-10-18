#!/usr/bin/env python3
"""
测试Agent是否正确理解@ada自我实现的含义
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "pim-compiler/react_is_all_you_need"))

from core.knowledge_concept_loader import KnowledgeConceptLoader

print("=" * 60)
print("🔍 验证@ada自我实现的更新定义")
print("=" * 60)

# 加载知识
knowledge_dir = Path(__file__).parent / "pim-compiler/react_is_all_you_need/knowledge"
loader = KnowledgeConceptLoader(
    knowledge_dirs=[str(knowledge_dir)],
    already_loaded=set()
)

# 读取完整的agent_driven_architecture.md
ada_file = knowledge_dir / "agent_driven_architecture.md"
content = ada_file.read_text(encoding='utf-8')

# 查找关键更新内容
print("\n📄 检查关键更新：")
print("-" * 40)

key_updates = [
    "必须更新Agent自己的knowledge.md文件",
    "第零步：定位自己的knowledge.md",
    "不要创建新文件",
    "自我编程的核心",
    "更新自己的knowledge.md（不是创建新文件！）",
    "my_knowledge_path = f\"~/.agent/{self.name}/knowledge.md\""
]

for update in key_updates:
    if update in content:
        print(f"✅ {update[:50]}...")
    else:
        print(f"❌ 未找到: {update[:50]}...")

# 显示执行契约部分
print("\n📝 执行契约关键部分：")
print("-" * 40)

# 找到执行契约部分
start = content.find("def ada自我实现(requirements_doc):")
if start != -1:
    end = content.find("```", start)
    if end != -1:
        contract_code = content[start:end]
        lines = contract_code.split('\n')[:20]  # 显示前20行
        for line in lines:
            print(line)

print("\n" + "=" * 60)
print("💡 核心理念验证")
print("=" * 60)

if all(update in content for update in key_updates[:3]):
    print("✅ @ada自我实现已正确更新")
    print("✅ 明确要求更新Agent自己的knowledge.md")
    print("✅ 禁止创建其他文件")
    print("✅ 强调自我编程的核心理念")
else:
    print("❌ 定义仍不够明确")

print("\n🎯 下一步：Agent应该能够：")
print("1. 读取需求文档")
print("2. 生成知识函数")
print("3. 更新 ~/.agent/{name}/knowledge.md")
print("4. 不创建其他文件")