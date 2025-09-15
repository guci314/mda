#!/usr/bin/env python3
"""
根据知识图谱生成高层次概览
使用三层本体结构分析Agent知识体系
"""

import rdflib
from rdflib import Namespace, RDF, RDFS
from collections import defaultdict, Counter
import networkx as nx
from datetime import datetime

def generate_knowledge_overview(ttl_file, output_file):
    """生成知识图谱的高层次概览"""
    
    # 加载RDF图谱
    g = rdflib.Graph()
    g.parse(ttl_file, format="turtle")
    
    # 定义命名空间
    kg = Namespace("http://example.org/knowledge#")
    ag = Namespace("http://example.org/agent#")
    kd = Namespace("http://example.org/knowledge-docs#")
    
    # 创建概览内容
    overview = []
    overview.append("# Agent知识体系高层次概览\n")
    overview.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    overview.append(f"数据源：{ttl_file}\n")
    
    # 1. 执行体系概览
    overview.append("\n## 1. 执行体系架构\n")
    overview.append("```mermaid")
    overview.append("graph TB")
    overview.append("    subgraph 执行层")
    
    # 获取所有自然语言函数
    nl_functions = list(g.subjects(RDF.type, ag.NaturalLanguageFunction))
    for func in nl_functions:
        name = g.value(func, ag.hasName)
        overview.append(f"        NLF_{name}[{name}]")
    
    # 获取所有Agent
    agents = list(g.subjects(RDF.type, ag.Agent))
    for agent in agents:
        name = g.value(agent, ag.hasName)
        agent_type = g.value(agent, ag.hasType)
        overview.append(f"        Agent_{name.replace(' ', '_')}[{name}<br/>{agent_type}]")
    
    overview.append("    end")
    overview.append("    ")
    overview.append("    subgraph 工具层")
    
    # 获取所有工具
    tools = list(g.subjects(RDF.type, kg.Tool))
    for tool in tools:
        name = g.value(tool, kg.hasName)
        overview.append(f"        Tool_{name}[{name}]")
    
    overview.append("    end")
    
    # 添加关系
    for func in nl_functions:
        func_name = g.value(func, ag.hasName)
        # 函数调用关系
        for called in g.objects(func, ag.callsFunction):
            called_name = g.value(called, ag.hasName)
            overview.append(f"    NLF_{func_name} --> NLF_{called_name}")
        
        # 工具使用关系
        for tool in g.objects(func, ag.usesTool):
            tool_name = g.value(tool, kg.hasName) or str(tool).split('#')[-1]
            overview.append(f"    NLF_{func_name} -.->|使用| Tool_{tool_name}")
    
    # Agent的工具关系
    for agent in agents:
        agent_name = g.value(agent, ag.hasName).replace(' ', '_')
        for tool in g.objects(agent, ag.hasTool):
            tool_name = g.value(tool, kg.hasName) or str(tool).split('#')[-1]
            overview.append(f"    Agent_{agent_name} -.->|配备| Tool_{tool_name}")
    
    overview.append("```\n")
    
    # 2. 知识体系结构
    overview.append("## 2. 知识体系结构\n")
    
    # SOP体系
    sops = list(g.subjects(RDF.type, ag.SOP))
    if sops:
        overview.append("### 2.1 标准操作流程（SOP）\n")
        for sop in sops:
            title = g.value(sop, kd.hasTitle)
            steps = g.value(sop, ag.hasSteps)
            overview.append(f"#### {title}\n")
            if steps:
                overview.append("**执行步骤：**\n")
                for step in steps.split():
                    overview.append(f"- {step}\n")
            
            # 找出实现者
            implementers = list(g.subjects(ag.implementsSOP, sop))
            if implementers:
                overview.append("\n**实现函数：**\n")
                for impl in implementers:
                    impl_name = g.value(impl, ag.hasName)
                    params = g.value(impl, ag.hasParameters)
                    overview.append(f"- `{impl_name}({params})`\n")
    
    # 核心概念
    concepts = list(g.subjects(RDF.type, kd.Concept))
    if concepts:
        overview.append("\n### 2.2 核心概念\n")
        for concept in concepts:
            title = g.value(concept, kd.hasTitle)
            desc = g.value(concept, kd.hasDescription)
            overview.append(f"- **{title}**: {desc}\n")
    
    # 3. 记忆体系
    overview.append("\n## 3. 记忆体系架构\n")
    overview.append("```mermaid")
    overview.append("graph LR")
    
    # 记忆类型
    memory_types = [
        (ag.CompactMemory, "CompactMemory"),
        (ag.SemanticMemory, "SemanticMemory"),
        (ag.WorkingMemory, "WorkingMemory")
    ]
    
    for mem_type, mem_label in memory_types:
        memories = list(g.subjects(RDF.type, mem_type))
        for memory in memories:
            name = g.value(memory, ag.hasName)
            if mem_type == ag.CompactMemory:
                threshold = g.value(memory, ag.memoryThreshold)
                if threshold:
                    overview.append(f"    {name}[{name}<br/>阈值: {threshold} tokens]")
                else:
                    overview.append(f"    {name}[{name}]")
            else:
                overview.append(f"    {name}[{name}]")
    
    # Agent记忆关系
    for agent in agents:
        agent_name = g.value(agent, ag.hasName).replace(' ', '_')
        for memory in g.objects(agent, ag.hasMemory):
            mem_name = g.value(memory, ag.hasName) or str(memory).split('#')[-1]
            overview.append(f"    Agent_{agent_name} --> {mem_name}")
    
    overview.append("```\n")
    
    # 4. 函数调用网络
    overview.append("## 4. 函数调用网络分析\n")
    
    # 构建调用图
    call_graph = nx.DiGraph()
    for func in nl_functions:
        func_name = g.value(func, ag.hasName)
        call_graph.add_node(func_name)
        
        for called in g.objects(func, ag.callsFunction):
            called_name = g.value(called, ag.hasName)
            call_graph.add_edge(func_name, called_name)
    
    if call_graph.nodes():
        overview.append("### 4.1 调用关系\n")
        overview.append("```mermaid")
        overview.append("graph TD")
        
        for node in call_graph.nodes():
            # 计算入度和出度
            in_degree = call_graph.in_degree(node)
            out_degree = call_graph.out_degree(node)
            
            if in_degree == 0 and out_degree > 0:
                overview.append(f"    {node}[{node}<br/>入口函数]:::entry")
            elif out_degree == 0 and in_degree > 0:
                overview.append(f"    {node}[{node}<br/>叶子函数]:::leaf")
            else:
                overview.append(f"    {node}[{node}]")
        
        for edge in call_graph.edges():
            overview.append(f"    {edge[0]} --> {edge[1]}")
        
        overview.append("    classDef entry fill:#e1f5fe")
        overview.append("    classDef leaf fill:#f3e5f5")
        overview.append("```\n")
        
        # 统计分析
        overview.append("### 4.2 函数统计\n")
        overview.append(f"- 函数总数：{len(nl_functions)}\n")
        overview.append(f"- 调用关系数：{call_graph.number_of_edges()}\n")
        
        # 最常被调用的函数
        if call_graph.nodes():
            in_degrees = [(node, call_graph.in_degree(node)) for node in call_graph.nodes()]
            in_degrees.sort(key=lambda x: x[1], reverse=True)
            
            if in_degrees[0][1] > 0:
                overview.append(f"- 最常被调用：{in_degrees[0][0]} (被调用 {in_degrees[0][1]} 次)\n")
    
    # 5. 工具使用分析
    overview.append("\n## 5. 工具使用分析\n")
    
    tool_usage = defaultdict(list)
    
    # 函数使用的工具
    for func in nl_functions:
        func_name = g.value(func, ag.hasName)
        for tool in g.objects(func, ag.usesTool):
            tool_name = g.value(tool, kg.hasName) or str(tool).split('#')[-1]
            tool_usage[tool_name].append(f"函数:{func_name}")
    
    # Agent配备的工具
    for agent in agents:
        agent_name = g.value(agent, ag.hasName)
        for tool in g.objects(agent, ag.hasTool):
            tool_name = g.value(tool, kg.hasName) or str(tool).split('#')[-1]
            tool_usage[tool_name].append(f"Agent:{agent_name}")
    
    if tool_usage:
        overview.append("### 工具使用情况\n")
        for tool_name, users in tool_usage.items():
            overview.append(f"- **{tool_name}**\n")
            for user in users:
                overview.append(f"  - {user}\n")
    
    # 6. 知识关联分析
    overview.append("\n## 6. 知识关联网络\n")
    
    # 概念关联
    concept_relations = []
    for concept in concepts:
        concept_name = g.value(concept, kd.hasTitle)
        
        # 查找相关概念
        for related in g.objects(concept, ag.relatedTo):
            related_name = g.value(related, kd.hasTitle)
            if related_name:
                concept_relations.append((concept_name, related_name))
        
        # 反向查找
        for related in g.subjects(ag.relatedTo, concept):
            related_name = g.value(related, kd.hasTitle)
            if related_name and (related_name, concept_name) not in concept_relations:
                concept_relations.append((related_name, concept_name))
    
    if concept_relations:
        overview.append("```mermaid")
        overview.append("graph LR")
        
        # 添加所有概念节点
        added_concepts = set()
        for rel in concept_relations:
            if rel[0] not in added_concepts:
                overview.append(f"    C_{rel[0].replace(' ', '_')}[{rel[0]}]")
                added_concepts.add(rel[0])
            if rel[1] not in added_concepts:
                overview.append(f"    C_{rel[1].replace(' ', '_')}[{rel[1]}]")
                added_concepts.add(rel[1])
        
        # 添加关系
        for rel in concept_relations:
            overview.append(f"    C_{rel[0].replace(' ', '_')} <--> C_{rel[1].replace(' ', '_')}")
        
        overview.append("```\n")
    
    # 7. 架构特征总结
    overview.append("\n## 7. 架构特征总结\n")
    
    # 统计各类实体
    stats = {
        "自然语言函数": len(nl_functions),
        "Agent": len(agents),
        "SOP": len(sops),
        "工具": len(tools),
        "概念": len(concepts),
        "记忆组件": len(list(g.subjects(RDF.type, ag.Memory)))
    }
    
    overview.append("### 7.1 实体统计\n")
    for entity_type, count in stats.items():
        overview.append(f"- {entity_type}: {count} 个\n")
    
    # 架构特点
    overview.append("\n### 7.2 架构特点\n")
    
    if nl_functions:
        overview.append("- ✅ **知识驱动执行**：通过自然语言函数定义行为\n")
    
    if sops:
        overview.append("- ✅ **流程标准化**：SOP定义标准操作流程\n")
    
    if tools:
        overview.append("- ✅ **工具集成**：统一的工具使用接口\n")
    
    compact_mem = list(g.subjects(RDF.type, ag.CompactMemory))
    if compact_mem:
        overview.append("- ✅ **智能记忆管理**：Compact Memory自动压缩机制\n")
    
    if call_graph.number_of_edges() > 0:
        overview.append("- ✅ **函数编排**：函数间存在调用关系\n")
    
    # 8. 核心洞察
    overview.append("\n## 8. 核心洞察\n")
    
    # 分析核心模式
    overview.append("### 8.1 设计模式\n")
    
    # 检查是否有元认知包装
    metacognitive = False
    for agent in agents:
        if "元认知" in str(g.value(agent, ag.hasDescription) or ""):
            metacognitive = True
            break
    
    if metacognitive:
        overview.append("- **元认知模式**：Agent具有自我监控和反思能力\n")
    
    # 检查知识驱动
    if nl_functions and concepts:
        overview.append("- **知识驱动架构**：知识定义行为，代码仅作执行框架\n")
    
    # 检查React模式
    react_agents = [a for a in agents if "React" in str(g.value(a, ag.hasType) or "")]
    if react_agents:
        overview.append("- **React推理模式**：基于React的思考-行动循环\n")
    
    overview.append("\n### 8.2 系统能力\n")
    
    # 根据实体推断能力
    capabilities = []
    
    if any("创建" in str(g.value(f, ag.hasName) or "") for f in nl_functions):
        capabilities.append("- **自举能力**：能够创建新的Agent")
    
    if any("监控" in str(g.value(f, ag.hasName) or "") for f in nl_functions):
        capabilities.append("- **监控能力**：能够监控和管理其他Agent")
    
    if compact_mem:
        threshold = g.value(compact_mem[0], ag.memoryThreshold)
        if threshold:
            capabilities.append(f"- **记忆压缩**：在{threshold} tokens时自动压缩")
    
    for cap in capabilities:
        overview.append(f"{cap}\n")
    
    # 9. 知识图谱特征
    overview.append("\n## 9. 知识图谱特征\n")
    
    # 图谱规模
    overview.append(f"- 三元组总数：{len(g)}\n")
    overview.append(f"- 实体总数：{len(set(g.subjects()))}\n")
    overview.append(f"- 关系类型数：{len(set(g.predicates()))}\n")
    
    # 命名空间使用
    ns_usage = defaultdict(int)
    for s, p, o in g:
        for term in [s, p, o]:
            if isinstance(term, rdflib.URIRef):
                ns = str(term).split('#')[0] + '#'
                if 'example.org' in ns:
                    ns_name = ns.split('/')[-1].replace('#', '')
                    ns_usage[ns_name] += 1
    
    overview.append("\n### 命名空间使用分布\n")
    for ns, count in sorted(ns_usage.items(), key=lambda x: x[1], reverse=True):
        overview.append(f"- {ns}: {count} 次\n")
    
    # 10. 建议和展望
    overview.append("\n## 10. 优化建议\n")
    
    suggestions = []
    
    # 根据分析提供建议
    if len(nl_functions) < 5:
        suggestions.append("- 可以增加更多自然语言函数，丰富执行能力")
    
    if len(concepts) < 10:
        suggestions.append("- 可以提取更多领域概念，完善知识体系")
    
    if not sops or len(sops) < 3:
        suggestions.append("- 可以定义更多SOP，标准化操作流程")
    
    if call_graph.number_of_edges() == 0:
        suggestions.append("- 可以增加函数间的协作，构建更复杂的工作流")
    
    if not concept_relations:
        suggestions.append("- 可以建立概念间的关联，形成知识网络")
    
    for suggestion in suggestions:
        overview.append(f"{suggestion}\n")
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(overview)
    
    print(f"✅ 高层次概览已生成：{output_file}")
    
    # 打印概览预览
    print("\n" + "=" * 60)
    print("概览预览（前50行）")
    print("=" * 60)
    for i, line in enumerate(overview[:50]):
        print(line.rstrip())
    
    if len(overview) > 50:
        print(f"\n... 还有 {len(overview) - 50} 行内容")
    
    return output_file

if __name__ == "__main__":
    ttl_file = "/tmp/knowledge_integrated.ttl"
    output_file = "/tmp/knowledge_overview.md"
    
    generate_knowledge_overview(ttl_file, output_file)