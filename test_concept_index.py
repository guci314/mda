#!/usr/bin/env python3
"""测试概念索引功能"""

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
print("知识索引测试")
print("=" * 60)

# 显示索引信息
print("\n" + loader.get_index_info())

print("\n" + "=" * 60)
print("搜索测试")
print("=" * 60)

# 测试搜索功能
print("\n搜索 '架构':")
results = loader.search_by_keyword("架构")
for item in results:
    print(f"  - @{item.name} ({item.item_type}): {item.docstring[:50]}...")

print("\n搜索 'Agent':")
results = loader.search_by_keyword("Agent")
for item in results:
    print(f"  - @{item.name} ({item.item_type}): {item.docstring[:50]}...")

print("\n" + "=" * 60)
print("引用检测测试")
print("=" * 60)

# 测试引用检测
test_message = """
我想了解@Agent驱动架构和@模型驱动架构的区别。
另外，@learning函数是如何工作的？
"""

detected = loader.detect_references(test_message)
print(f"\n从消息中检测到的引用: {detected}")

for ref in detected:
    if ref in loader.knowledge_index:
        item = loader.knowledge_index[ref]
        print(f"\n@{ref}:")
        print(f"  类型: {item.item_type}")
        print(f"  分类: {item.category}")
        print(f"  文件: {item.path.name}")
        print(f"  描述: {item.docstring}")

print("\n" + "=" * 60)
print("相关项查找")
print("=" * 60)

# 查找相关项
if "Agent驱动架构" in loader.knowledge_index:
    related = loader.get_related_items("Agent驱动架构")
    print(f"\n与 @Agent驱动架构 相关的知识项:")
    for item in related:
        print(f"  - @{item.name} ({item.item_type})")

print("\n" + "=" * 60)
print("统计信息")
print("=" * 60)

print(f"\n总计:")
print(f"  - 知识项总数: {len(loader.knowledge_index)}")
print(f"  - 可执行函数: {len(loader.functions)}")
print(f"  - 理论概念: {len(loader.concepts)}")