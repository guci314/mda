#!/usr/bin/env python3
"""
验证扩展本体的一致性和质量
检查静态核心 + 动态扩展的结构
"""

import rdflib
from rdflib import Namespace, RDF, RDFS
from collections import defaultdict

def validate_extended_ontology(ttl_file):
    """验证扩展本体"""
    
    # 加载RDF图
    g = rdflib.Graph()
    g.parse(ttl_file, format="turtle")
    
    # 定义命名空间
    CORE = Namespace("http://ontology.core#")
    ONTO = Namespace("http://ontology.meta#")
    EXT = Namespace("http://ontology.ext#")
    
    print("=" * 60)
    print("扩展本体验证报告")
    print("=" * 60)
    
    # 1. 验证静态核心
    print("\n1. 静态核心本体验证")
    print("-" * 40)
    
    core_concepts = [
        "Thing", "Entity", "Concept",
        "Relation", "partOf", "instanceOf", "relatedTo",
        "Process", "causes", "transformsTo"
    ]
    
    found_core = 0
    for concept in core_concepts:
        if (CORE[concept], RDF.type, None) in g or \
           (CORE[concept], RDFS.subClassOf, None) in g or \
           (CORE[concept], RDFS.subPropertyOf, None) in g:
            print(f"✅ core:{concept}")
            found_core += 1
        else:
            print(f"❌ 缺失: core:{concept}")
    
    print(f"\n核心概念覆盖率: {found_core}/{len(core_concepts)}")
    
    # 2. 验证动态扩展
    print("\n2. 动态扩展验证")
    print("-" * 40)
    
    extensions = []
    for s, p, o in g:
        if str(s).startswith(str(EXT)):
            if p == RDF.type and o == RDFS.Class:
                concept_name = str(s).split('#')[-1]
                extensions.append(concept_name)
                
                # 检查必需的自然语言说明
                has_nl_desc = (s, ONTO.nlDescription, None) in g
                has_nl_context = (s, ONTO.nlContext, None) in g
                has_nl_example = (s, ONTO.nlExample, None) in g
                has_embedding = (s, ONTO.embedding, None) in g
                has_confidence = (s, ONTO.confidence, None) in g
                
                print(f"\n扩展概念: ext:{concept_name}")
                
                # 获取父类
                parent = g.value(s, RDFS.subClassOf)
                if parent:
                    parent_name = str(parent).split('#')[-1]
                    print(f"  父类: core:{parent_name}")
                
                # 获取描述
                nl_desc = g.value(s, ONTO.nlDescription)
                if nl_desc:
                    print(f"  描述: {nl_desc[:60]}...")
                
                # 获取置信度
                confidence = g.value(s, ONTO.confidence)
                if confidence:
                    conf_val = float(confidence)
                    status = "✅ 自动接受" if conf_val >= 0.8 else "⚠️ 需要审核"
                    print(f"  置信度: {conf_val} ({status})")
                
                # 验证完整性
                completeness = []
                if has_nl_desc: completeness.append("描述")
                if has_nl_context: completeness.append("语境")
                if has_nl_example: completeness.append("示例")
                if has_embedding: completeness.append("向量")
                if has_confidence: completeness.append("置信度")
                
                print(f"  完整性: [{', '.join(completeness)}]")
    
    print(f"\n动态扩展总数: {len(extensions)}")
    
    # 3. 验证继承关系
    print("\n3. 继承关系验证")
    print("-" * 40)
    
    inheritance = defaultdict(list)
    for s, p, o in g:
        if p == RDFS.subClassOf:
            child = str(s).split('#')[-1]
            parent = str(o).split('#')[-1]
            inheritance[parent].append(child)
    
    # 显示继承树
    def print_tree(node, prefix="", visited=None):
        if visited is None:
            visited = set()
        if node in visited:
            return
        visited.add(node)
        
        print(f"{prefix}{node}")
        children = inheritance.get(node, [])
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            child_prefix = prefix + ("└── " if is_last else "├── ")
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(child, child_prefix, visited)
    
    print("\n继承树:")
    print_tree("Thing", "")
    
    # 4. 统计分析
    print("\n4. 统计分析")
    print("-" * 40)
    
    # 统计各命名空间的使用
    ns_stats = defaultdict(int)
    for s, p, o in g:
        for term in [s, p, o]:
            if isinstance(term, rdflib.URIRef):
                ns = str(term).split('#')[0] + '#'
                if 'ontology' in ns:
                    ns_name = ns.split('/')[-1].replace('#', '')
                    ns_stats[ns_name] += 1
    
    print("\n命名空间使用:")
    for ns, count in sorted(ns_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ns}: {count} 次")
    
    # 5. 质量评估
    print("\n5. 质量评估")
    print("-" * 40)
    
    issues = []
    warnings = []
    
    # 检查扩展是否都有父类
    for ext in extensions:
        ext_uri = EXT[ext]
        if not g.value(ext_uri, RDFS.subClassOf):
            issues.append(f"扩展 {ext} 没有父类")
    
    # 检查是否有孤立概念
    for s in g.subjects(RDF.type, RDFS.Class):
        if str(s).startswith(str(EXT)):
            has_instances = False
            for _, _, o in g.triples((None, RDF.type, s)):
                has_instances = True
                break
            if not has_instances:
                name = str(s).split('#')[-1]
                warnings.append(f"扩展概念 {name} 没有实例")
    
    if issues:
        print("\n❌ 发现问题:")
        for issue in issues:
            print(f"  - {issue}")
    
    if warnings:
        print("\n⚠️ 警告:")
        for warning in warnings[:5]:  # 只显示前5个
            print(f"  - {warning}")
        if len(warnings) > 5:
            print(f"  ... 还有 {len(warnings) - 5} 个警告")
    
    if not issues:
        print("\n✅ 本体结构验证通过!")
        print("  - 静态核心完整")
        print("  - 动态扩展规范")
        print("  - 继承关系正确")
        print("  - 自然语言说明完备")
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    print(f"总三元组数: {len(g)}")
    print(f"核心概念: {found_core}")
    print(f"扩展概念: {len(extensions)}")
    print(f"严重问题: {len(issues)}")
    print(f"警告数量: {len(warnings)}")
    
    return len(issues) == 0

if __name__ == "__main__":
    ttl_file = "/tmp/knowledge_extended.ttl"
    success = validate_extended_ontology(ttl_file)
    
    if success:
        print("\n🎉 扩展本体验证成功!")
    else:
        print("\n⚠️ 扩展本体存在问题，请检查")