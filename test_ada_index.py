#!/usr/bin/env python3
"""测试@ada自我实现函数是否被正确索引"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "pim-compiler/react_is_all_you_need"))

from core.knowledge_concept_loader import KnowledgeConceptLoader

# 创建加载器
knowledge_dir = Path(__file__).parent / "pim-compiler/react_is_all_you_need/knowledge"
loader = KnowledgeConceptLoader(
    knowledge_dirs=[str(knowledge_dir)],
    already_loaded=set()
)

print("=" * 60)
print("测试@ada自我实现函数的索引")
print("=" * 60)

# 查找ada自我实现
if "ada自我实现" in loader.knowledge_index:
    item = loader.knowledge_index["ada自我实现"]
    print(f"\n✅ 找到 @ada自我实现")
    print(f"  类型: {item.item_type}")
    print(f"  分类: {item.category}")
    print(f"  文件: {item.path.name}")
    print(f"  描述: {item.docstring}")
else:
    print("\n❌ 未找到 @ada自我实现")

# 搜索相关概念
print("\n" + "=" * 60)
print("搜索ADA相关知识项")
print("=" * 60)

ada_items = loader.search_by_keyword("ADA")
print(f"\n找到 {len(ada_items)} 个ADA相关项:")
for item in ada_items:
    print(f"  - @{item.name} ({item.item_type})")

# 测试引用检测
print("\n" + "=" * 60)
print("测试引用检测")
print("=" * 60)

test_message = """
我想使用@ada自我实现来处理需求文档，
这体现了@Agent驱动架构的理念。
"""

detected = loader.detect_references(test_message)
print(f"\n检测到的引用: {detected}")

# 显示统计
print("\n" + "=" * 60)
print("知识库统计")
print("=" * 60)
print(f"  总计: {len(loader.knowledge_index)}项")
print(f"  可执行函数: {len(loader.functions)}个")
print(f"  理论概念: {len(loader.concepts)}个")