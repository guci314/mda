#!/usr/bin/env python3
"""
验证知识图谱RDF的三层本体结构
确保正确区分三种Function类型：
1. kg:Function - 代码中的基类
2. ag:NaturalLanguageFunction - Agent的自然语言函数
3. kd:Function - 通用知识本体的函数概念（如果存在）
"""

import rdflib
from rdflib import Namespace, RDF, RDFS
from collections import defaultdict
import sys

def validate_knowledge_rdf(ttl_file):
    """验证知识图谱的RDF结构"""
    
    # 创建图并加载文件
    g = rdflib.Graph()
    try:
        g.parse(ttl_file, format="turtle")
        print(f"✅ 成功加载RDF文件：{ttl_file}")
        print(f"   包含 {len(g)} 个三元组\n")
    except Exception as e:
        print(f"❌ 加载RDF文件失败：{e}")
        return False
    
    # 定义命名空间
    kg = Namespace("http://example.org/knowledge#")
    ag = Namespace("http://example.org/agent#")
    kd = Namespace("http://example.org/knowledge-docs#")
    
    # 1. 验证命名空间使用
    print("=" * 60)
    print("1. 命名空间验证")
    print("=" * 60)
    
    namespaces_found = set()
    for prefix, ns in g.namespaces():
        namespaces_found.add(str(ns))
        print(f"   {prefix}: {ns}")
    
    required_namespaces = [
        "http://example.org/agent#",
        "http://example.org/knowledge#",
        "http://example.org/knowledge-docs#"
    ]
    
    for ns in required_namespaces:
        if ns in namespaces_found:
            print(f"✅ 找到必需的命名空间：{ns}")
        else:
            print(f"⚠️  缺少命名空间：{ns}")
    
    # 2. 验证三种Function的正确区分
    print("\n" + "=" * 60)
    print("2. Function类型区分验证")
    print("=" * 60)
    
    # 查找ag:NaturalLanguageFunction（自然语言函数）
    nl_functions = list(g.subjects(RDF.type, ag.NaturalLanguageFunction))
    print(f"\n✅ ag:NaturalLanguageFunction（自然语言函数）: {len(nl_functions)} 个")
    for func in nl_functions:
        name = g.value(func, ag.hasName)
        params = g.value(func, ag.hasParameters)
        print(f"   - {name}: 参数({params})")
        
        # 检查调用关系
        calls = list(g.objects(func, ag.callsFunction))
        if calls:
            for called in calls:
                called_name = g.value(called, ag.hasName)
                print(f"     → 调用: {called_name}")
        
        # 检查工具使用
        tools = list(g.objects(func, ag.usesTool))
        if tools:
            for tool in tools:
                tool_name = g.value(tool, kg.hasName) or str(tool).split('#')[-1]
                print(f"     🔧 使用工具: {tool_name}")
    
    # 查找ag:Function（如果错误使用）
    wrong_functions = list(g.subjects(RDF.type, ag.Function))
    if wrong_functions:
        print(f"\n⚠️  发现错误的ag:Function使用: {len(wrong_functions)} 个")
        print("   应该使用ag:NaturalLanguageFunction")
        for func in wrong_functions:
            print(f"   - {func}")
    
    # 查找kg:Function相关（代码基类）
    code_functions = list(g.subjects(RDF.type, kg.Function))
    if code_functions:
        print(f"\n✅ kg:Function（代码基类）: {len(code_functions)} 个")
        for func in code_functions:
            print(f"   - {func}")
    
    # 3. 验证Agent特定实体
    print("\n" + "=" * 60)
    print("3. Agent特定实体验证")
    print("=" * 60)
    
    # Agent实体
    agents = list(g.subjects(RDF.type, ag.Agent))
    print(f"\n✅ Agent实体: {len(agents)} 个")
    for agent in agents:
        name = g.value(agent, ag.hasName)
        agent_type = g.value(agent, ag.hasType)
        desc = g.value(agent, ag.hasDescription)
        print(f"   - {name} ({agent_type}): {desc}")
        
        # 检查工具
        tools = list(g.objects(agent, ag.hasTool))
        if tools:
            print(f"     工具: {', '.join([str(t).split('#')[-1] for t in tools])}")
        
        # 检查记忆
        memories = list(g.objects(agent, ag.hasMemory))
        if memories:
            print(f"     记忆: {', '.join([str(m).split('#')[-1] for m in memories])}")
    
    # SOP实体
    sops = list(g.subjects(RDF.type, ag.SOP))
    print(f"\n✅ SOP（标准操作流程）: {len(sops)} 个")
    for sop in sops:
        title = g.value(sop, kd.hasTitle)
        steps = g.value(sop, ag.hasSteps)
        print(f"   - {title}")
        if steps:
            print(f"     步骤: {steps}")
        
        # 查找实现此SOP的函数
        implementers = list(g.subjects(ag.implementsSOP, sop))
        if implementers:
            for impl in implementers:
                impl_name = g.value(impl, ag.hasName)
                print(f"     ← 被实现: {impl_name}")
    
    # 工具实体
    tools = list(g.subjects(RDF.type, kg.Tool))
    print(f"\n✅ Tool（工具）: {len(tools)} 个")
    for tool in tools:
        name = g.value(tool, kg.hasName)
        desc = g.value(tool, kg.hasDescription)
        print(f"   - {name}: {desc}")
    
    # 4. 验证知识文档实体
    print("\n" + "=" * 60)
    print("4. 知识文档实体验证")
    print("=" * 60)
    
    # Concept实体
    concepts = list(g.subjects(RDF.type, kd.Concept))
    print(f"\n✅ Concept（概念）: {len(concepts)} 个")
    for concept in concepts:
        title = g.value(concept, kd.hasTitle)
        desc = g.value(concept, kd.hasDescription)
        print(f"   - {title}: {desc}")
    
    # Procedure实体
    procedures = list(g.subjects(RDF.type, kd.Procedure))
    print(f"\n✅ Procedure（流程）: {len(procedures)} 个")
    for proc in procedures:
        title = g.value(proc, kd.hasTitle)
        print(f"   - {title}")
    
    # 5. 验证记忆系统
    print("\n" + "=" * 60)
    print("5. 记忆系统验证")
    print("=" * 60)
    
    # 各种记忆类型
    memory_types = [
        (ag.CompactMemory, "CompactMemory（压缩记忆）"),
        (ag.SemanticMemory, "SemanticMemory（语义记忆）"),
        (ag.WorkingMemory, "WorkingMemory（工作记忆）"),
        (ag.Memory, "Memory（通用记忆）")
    ]
    
    for mem_type, mem_name in memory_types:
        memories = list(g.subjects(RDF.type, mem_type))
        if memories:
            print(f"\n✅ {mem_name}: {len(memories)} 个")
            for memory in memories:
                name = g.value(memory, ag.hasName)
                print(f"   - {name}")
                
                # 特殊属性
                if mem_type == ag.CompactMemory:
                    threshold = g.value(memory, ag.memoryThreshold)
                    if threshold:
                        print(f"     阈值: {threshold} tokens")
    
    # 6. 验证关系完整性
    print("\n" + "=" * 60)
    print("6. 关系完整性验证")
    print("=" * 60)
    
    # 统计各种关系
    relations = defaultdict(int)
    for s, p, o in g:
        if not str(p).startswith("http://www.w3.org"):
            relations[str(p).split('#')[-1]] += 1
    
    print("\n关系使用统计：")
    for rel, count in sorted(relations.items(), key=lambda x: x[1], reverse=True):
        print(f"   {rel}: {count} 次")
    
    # 7. 验证本体定义
    print("\n" + "=" * 60)
    print("7. 本体类定义验证")
    print("=" * 60)
    
    # 检查类定义
    classes = list(g.subjects(RDF.type, RDFS.Class))
    print(f"\n✅ 定义的类: {len(classes)} 个")
    
    class_by_ns = defaultdict(list)
    for cls in classes:
        ns = str(cls).split('#')[0] + '#'
        name = str(cls).split('#')[-1]
        class_by_ns[ns].append(name)
    
    for ns, names in class_by_ns.items():
        prefix = ns.split('/')[-1].replace('#', '')
        print(f"\n   {prefix}: ({len(names)} 个)")
        for name in sorted(names):
            # 检查子类关系
            full_uri = rdflib.URIRef(ns + name)
            parent = g.value(full_uri, RDFS.subClassOf)
            if parent:
                parent_name = str(parent).split('#')[-1]
                print(f"     - {name} → {parent_name}")
            else:
                print(f"     - {name}")
    
    # 8. 总结验证结果
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    issues = []
    
    # 检查关键问题
    if wrong_functions:
        issues.append("发现错误使用ag:Function，应使用ag:NaturalLanguageFunction")
    
    if not nl_functions:
        issues.append("未找到ag:NaturalLanguageFunction实体")
    
    if not agents:
        issues.append("未找到Agent实体")
    
    if issues:
        print("\n⚠️  发现以下问题：")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ 验证通过！三层本体结构正确：")
        print("   1. kg: 用于代码实体（基类、工具等）")
        print("   2. ag: 用于Agent特定概念（NaturalLanguageFunction、Agent、SOP等）")
        print("   3. kd: 用于知识文档概念（Concept、Procedure等）")
        print("\n✅ Function类型正确区分：")
        print("   - ag:NaturalLanguageFunction 用于自然语言函数")
        print("   - kg:Function 用于代码基类（如需要）")
        print("   - 未混淆使用ag:Function")
    
    return len(issues) == 0

if __name__ == "__main__":
    ttl_file = "/tmp/knowledge_integrated.ttl"
    if len(sys.argv) > 1:
        ttl_file = sys.argv[1]
    
    print(f"验证知识图谱：{ttl_file}")
    print("=" * 60)
    
    success = validate_knowledge_rdf(ttl_file)
    
    if success:
        print("\n🎉 知识图谱验证完成，结构正确！")
    else:
        print("\n⚠️  知识图谱存在问题，请检查并修正")
        sys.exit(1)