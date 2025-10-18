#!/usr/bin/env python3
"""
测试@ada自我实现是否正确要求更新description
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "pim-compiler/react_is_all_you_need"))

from core.knowledge_concept_loader import KnowledgeConceptLoader

print("=" * 60)
print("🔍 验证@ada自我实现的完整定义")
print("=" * 60)

# 加载知识
knowledge_dir = Path(__file__).parent / "pim-compiler/react_is_all_you_need/knowledge"
loader = KnowledgeConceptLoader(
    knowledge_dirs=[str(knowledge_dir)],
    already_loaded=set()
)

# 读取ADA文件
ada_file = knowledge_dir / "agent_driven_architecture.md"
content = ada_file.read_text(encoding='utf-8')

print("\n📝 核心要求验证：")
print("-" * 40)

# 检查关键要求
requirements = [
    ("必须更新Agent自己的knowledge.md文件", "更新先天知识"),
    ("必须更新Agent的description", "更新对外接口"),
    ("不要创建其他文件", "自我编程原则"),
    ("knowledge.md是Agent的先天知识", "理解架构"),
    ("description是Agent的对外接口", "理解接口"),
    ("self.description = new_description", "代码实现")
]

for req, desc in requirements:
    if req in content:
        print(f"✅ {desc}: {req[:40]}...")
    else:
        print(f"❌ 缺失: {desc}")

print("\n📊 返回值验证：")
print("-" * 40)

# 检查函数签名
if "-> (knowledge.md, description)" in content:
    print("✅ 函数返回knowledge.md和description")
else:
    print("❌ 函数签名不完整")

# 检查执行契约
if "更新了对外接口description" in content:
    print("✅ 执行结果包含description更新")
else:
    print("❌ 执行结果未提及description")

print("\n📄 示例输出验证：")
print("-" * 40)

# 检查示例
if "输出1：更新后的knowledge.md" in content:
    print("✅ 包含knowledge.md输出示例")

if "输出2：更新后的description" in content:
    print("✅ 包含description输出示例")

# 显示description示例
print("\n💬 description示例内容：")
start = content.find("输出2：更新后的description")
if start != -1:
    end = content.find("```", start + 100)
    if end != -1:
        desc_example = content[start:end]
        lines = desc_example.split('\n')[2:8]  # 显示主要内容
        for line in lines:
            if line.strip():
                print(f"   {line}")

print("\n" + "=" * 60)
print("💡 完整性检查")
print("=" * 60)

complete = all([
    "必须更新Agent自己的knowledge.md文件" in content,
    "必须更新Agent的description" in content,
    "-> (knowledge.md, description)" in content,
    "self.description = new_description" in content,
    "输出1：更新后的knowledge.md" in content,
    "输出2：更新后的description" in content
])

if complete:
    print("✅ @ada自我实现定义完整！")
    print("✅ Agent将更新knowledge.md（先天知识）")
    print("✅ Agent将更新description（对外接口）")
    print("✅ 实现了真正的自我编程")
else:
    print("❌ 定义仍需完善")

print("\n🎯 Agent执行@ada自我实现后将：")
print("1. 更新~/.agent/{name}/knowledge.md - 获得新能力")
print("2. 更新self.description - 声明新能力")
print("3. 不创建其他文件 - 自我编程原则")