#!/usr/bin/env python3
"""
使用静态核心本体 + 动态扩展生成Knowledge目录的RDF图谱
Agent可以基于10个核心概念自主扩展本体，并生成自然语言说明
"""

import os
import re
import rdflib
from rdflib import Namespace, RDF, RDFS, Literal, URIRef
from pathlib import Path
import hashlib
import numpy as np
from datetime import datetime

# 定义命名空间
CORE = Namespace("http://ontology.core#")  # 静态核心本体
ONTO = Namespace("http://ontology.meta#")  # 元本体（描述本体的本体）
EXT = Namespace("http://ontology.ext#")    # Agent扩展的本体

# 原有命名空间保留兼容
KG = Namespace("http://example.org/knowledge#")
AG = Namespace("http://example.org/agent#")
KD = Namespace("http://example.org/knowledge-docs#")

class DynamicOntologyExtender:
    """动态本体扩展器 - Agent自主扩展本体"""
    
    def __init__(self, graph):
        self.graph = graph
        self.extensions = {}
        self.confidence_threshold = 0.8
        self.agent_name = "KnowledgeAnalysisAgent"
        
        # 初始化静态核心本体
        self.init_static_core()
    
    def init_static_core(self):
        """初始化10个核心概念"""
        # 存在层
        self.graph.add((CORE.Thing, RDF.type, RDFS.Class))
        self.graph.add((CORE.Thing, RDFS.comment, Literal("Root of all concepts")))
        
        self.graph.add((CORE.Entity, RDF.type, RDFS.Class))
        self.graph.add((CORE.Entity, RDFS.subClassOf, CORE.Thing))
        self.graph.add((CORE.Entity, RDFS.comment, Literal("Concrete identifiable things")))
        
        self.graph.add((CORE.Concept, RDF.type, RDFS.Class))
        self.graph.add((CORE.Concept, RDFS.subClassOf, CORE.Thing))
        self.graph.add((CORE.Concept, RDFS.comment, Literal("Abstract mental constructs")))
        
        # 关系层
        self.graph.add((CORE.Relation, RDF.type, RDF.Property))
        self.graph.add((CORE.Relation, RDFS.comment, Literal("Base class for all relations")))
        
        self.graph.add((CORE.partOf, RDF.type, RDF.Property))
        self.graph.add((CORE.partOf, RDFS.subPropertyOf, CORE.Relation))
        
        self.graph.add((CORE.instanceOf, RDF.type, RDF.Property))
        self.graph.add((CORE.instanceOf, RDFS.subPropertyOf, CORE.Relation))
        
        self.graph.add((CORE.relatedTo, RDF.type, RDF.Property))
        self.graph.add((CORE.relatedTo, RDFS.subPropertyOf, CORE.Relation))
        
        # 过程层
        self.graph.add((CORE.Process, RDF.type, RDFS.Class))
        self.graph.add((CORE.Process, RDFS.subClassOf, CORE.Thing))
        self.graph.add((CORE.Process, RDFS.comment, Literal("Dynamic behaviors and changes")))
        
        self.graph.add((CORE.causes, RDF.type, RDF.Property))
        self.graph.add((CORE.causes, RDFS.subPropertyOf, CORE.Relation))
        
        self.graph.add((CORE.transformsTo, RDF.type, RDF.Property))
        self.graph.add((CORE.transformsTo, RDFS.subPropertyOf, CORE.Relation))
    
    def generate_embedding(self, text):
        """生成语义向量（模拟）"""
        # 实际应用中使用sentence-transformers
        # 这里用哈希模拟768维向量
        hash_obj = hashlib.sha256(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # 将哈希转换为768维向量
        np.random.seed(int(hash_hex[:8], 16))
        embedding = np.random.randn(768)
        embedding = embedding / np.linalg.norm(embedding)  # 归一化
        
        return embedding.tolist()
    
    def extend_concept(self, concept_name, parent_class, nl_description, nl_context, nl_example, confidence=0.9):
        """扩展新概念并添加自然语言说明"""
        
        # 创建概念URI
        concept_uri = EXT[concept_name]
        
        # 添加类定义
        self.graph.add((concept_uri, RDF.type, RDFS.Class))
        self.graph.add((concept_uri, RDFS.subClassOf, parent_class))
        
        # 添加必需的自然语言说明
        self.graph.add((concept_uri, ONTO.nlDescription, Literal(nl_description)))
        self.graph.add((concept_uri, ONTO.nlContext, Literal(nl_context)))
        self.graph.add((concept_uri, ONTO.nlExample, Literal(nl_example)))
        
        # 生成并添加语义向量
        full_text = f"{nl_description} {nl_context} {nl_example}"
        embedding = self.generate_embedding(full_text)
        embedding_str = ",".join([f"{x:.4f}" for x in embedding[:10]])  # 只存储前10维作为示例
        self.graph.add((concept_uri, ONTO.embedding, Literal(f"[{embedding_str}...]")))
        
        # 添加元数据
        self.graph.add((concept_uri, ONTO.createdBy, Literal(self.agent_name)))
        self.graph.add((concept_uri, ONTO.createdAt, Literal(datetime.now().isoformat())))
        self.graph.add((concept_uri, ONTO.confidence, Literal(confidence)))
        
        # 记录扩展
        self.extensions[concept_name] = {
            "parent": parent_class,
            "description": nl_description,
            "confidence": confidence
        }
        
        return concept_uri
    
    def analyze_and_extend(self, text, filename):
        """分析文本并动态扩展本体"""
        
        # 分析：识别自然语言函数
        if "函数：" in text or "def " in text or "function " in text:
            if "NaturalLanguageFunction" not in self.extensions:
                self.extend_concept(
                    "NaturalLanguageFunction",
                    CORE.Process,
                    "A function defined in natural language that describes a process or procedure to be executed",
                    "Used in knowledge-driven development where behavior is defined by markdown files",
                    "函数：监控agent(agent_name, task) with steps defined in natural language",
                    0.93
                )
        
        # 分析：识别SOP
        if "SOP" in text or "标准操作流程" in text or "步骤：" in text:
            if "SOP" not in self.extensions:
                self.extend_concept(
                    "SOP",
                    CORE.Concept,
                    "Standard Operating Procedure that defines a repeatable sequence of steps",
                    "Used to standardize complex workflows in agent systems",
                    "Agent监控SOP: 1.编写知识 2.创建Agent 3.测试 4.分析",
                    0.91
                )
        
        # 分析：识别Agent概念
        if "Agent" in text or "代理" in text:
            if "Agent" not in self.extensions:
                self.extend_concept(
                    "Agent",
                    CORE.Entity,
                    "An autonomous software entity that can perceive, think, and act",
                    "Core concept in multi-agent systems and AI",
                    "ReactAgentMinimal - an agent that uses React pattern for reasoning",
                    0.95
                )
        
        # 分析：识别Tool概念
        if "Tool" in text or "工具" in text:
            if "Tool" not in self.extensions:
                self.extend_concept(
                    "Tool",
                    CORE.Entity,
                    "A reusable component that provides specific functionality",
                    "Used by agents to perform actions in the environment",
                    "CreateAgentTool - creates new agent instances",
                    0.89
                )
        
        # 分析：识别Memory概念
        if "Memory" in text or "记忆" in text or "memory" in text:
            if "Memory" not in self.extensions:
                self.extend_concept(
                    "Memory",
                    CORE.Concept,
                    "A system for storing and retrieving information over time",
                    "Essential component for agent learning and context preservation",
                    "CompactMemory - compresses context when reaching 70k tokens",
                    0.92
                )
        
        # 分析：识别Knowledge概念
        if "Knowledge" in text or "知识" in text:
            if "Knowledge" not in self.extensions:
                self.extend_concept(
                    "Knowledge",
                    CORE.Concept,
                    "Structured information that guides agent behavior and decision-making",
                    "Stored in markdown files and used for knowledge-driven development",
                    "agent_builder_knowledge.md - contains agent construction patterns",
                    0.94
                )

def extract_knowledge_from_file(file_path, graph, extender):
    """从知识文件提取信息并动态扩展本体"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 让Agent分析并扩展本体
    extender.analyze_and_extend(content, file_path.name)
    
    # 提取自然语言函数
    nl_function_pattern = r'###?\s*函数[：:]\s*([^(]+)\(([^)]*)\)'
    for match in re.finditer(nl_function_pattern, content):
        func_name = match.group(1).strip()
        params = match.group(2).strip()
        
        # 清理函数名（移除特殊字符）
        clean_name = re.sub(r'[^\w\u4e00-\u9fff]+', '_', func_name)
        clean_name = clean_name.strip('_')
        
        # 创建函数实体（使用扩展的概念）
        func_uri = AG[clean_name]
        
        if "NaturalLanguageFunction" in extender.extensions:
            graph.add((func_uri, RDF.type, EXT.NaturalLanguageFunction))
        else:
            graph.add((func_uri, RDF.type, CORE.Process))  # 降级到核心概念
        
        graph.add((func_uri, AG.hasName, Literal(func_name)))
        graph.add((func_uri, AG.hasParameters, Literal(params)))
        
        # 添加自然语言说明
        graph.add((func_uri, ONTO.nlDescription, 
                  Literal(f"Natural language function that {func_name.lower().replace('_', ' ')}")))
        graph.add((func_uri, ONTO.nlContext, 
                  Literal(f"Defined in {file_path.name}")))
        
        # 提取函数调用关系
        call_pattern = r'调用\s+([^(]+)\('
        for call_match in re.finditer(call_pattern, content[match.end():match.end()+2000]):
            called_func = call_match.group(1).strip()
            # 清理被调用函数名
            clean_called = re.sub(r'[^\w\u4e00-\u9fff]+', '_', called_func)
            clean_called = clean_called.strip('_')
            called_uri = AG[clean_called]
            graph.add((func_uri, CORE.causes, called_uri))
    
    # 提取SOP
    sop_pattern = r'##\s*SOP[：:]\s*(.+)'
    for match in re.finditer(sop_pattern, content):
        sop_name = match.group(1).strip()
        sop_uri = AG[sop_name.replace(' ', '_')]
        
        if "SOP" in extender.extensions:
            graph.add((sop_uri, RDF.type, EXT.SOP))
        else:
            graph.add((sop_uri, RDF.type, CORE.Concept))
        
        graph.add((sop_uri, KD.hasTitle, Literal(sop_name)))
        
        # 添加自然语言说明
        graph.add((sop_uri, ONTO.nlDescription, 
                  Literal(f"Standard operating procedure for {sop_name.lower()}")))
    
    # 提取概念
    concept_pattern = r'##\s*概念[：:]\s*(.+)'
    for match in re.finditer(concept_pattern, content):
        concept_name = match.group(1).strip()
        concept_uri = KD[concept_name.replace(' ', '_')]
        graph.add((concept_uri, RDF.type, CORE.Concept))
        graph.add((concept_uri, KD.hasTitle, Literal(concept_name)))

def generate_extension_report(extender, output_file):
    """生成本体扩展报告"""
    
    report = []
    report.append("# 本体动态扩展报告\n")
    report.append(f"扩展Agent: {extender.agent_name}\n")
    report.append(f"扩展时间: {datetime.now().isoformat()}\n\n")
    
    report.append("## 静态核心本体（人类定义）\n")
    report.append("- **存在层**: Thing, Entity, Concept\n")
    report.append("- **关系层**: Relation, partOf, instanceOf, relatedTo\n")
    report.append("- **过程层**: Process, causes, transformsTo\n\n")
    
    report.append("## 动态扩展概念（Agent发现）\n")
    for name, info in extender.extensions.items():
        parent_name = str(info['parent']).split('#')[-1]
        report.append(f"\n### {name}\n")
        report.append(f"- **父类**: core:{parent_name}\n")
        report.append(f"- **描述**: {info['description']}\n")
        report.append(f"- **置信度**: {info['confidence']:.2f}\n")
        
        if info['confidence'] < extender.confidence_threshold:
            report.append(f"- **状态**: ⚠️ 需要人类审核\n")
        else:
            report.append(f"- **状态**: ✅ 自动接受\n")
    
    report.append("\n## 扩展统计\n")
    report.append(f"- 总扩展数: {len(extender.extensions)}\n")
    high_conf = sum(1 for x in extender.extensions.values() if x['confidence'] >= 0.9)
    report.append(f"- 高置信度: {high_conf}\n")
    need_review = sum(1 for x in extender.extensions.values() if x['confidence'] < extender.confidence_threshold)
    report.append(f"- 需要审核: {need_review}\n")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(report)
    
    print(f"✅ 扩展报告已生成: {output_file}")

def main():
    # 创建RDF图
    g = rdflib.Graph()
    
    # 绑定命名空间
    g.bind("core", CORE)
    g.bind("onto", ONTO)
    g.bind("ext", EXT)
    g.bind("kg", KG)
    g.bind("ag", AG)
    g.bind("kd", KD)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    
    # 创建动态扩展器
    extender = DynamicOntologyExtender(g)
    
    # 扫描Knowledge目录
    knowledge_dir = Path("/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge")
    
    print("开始分析Knowledge目录...")
    print(f"使用静态核心 + 动态扩展模式")
    
    # 只处理.md文件
    md_files = list(knowledge_dir.glob("*.md"))
    
    for file_path in md_files:
        if file_path.name not in ['README.md', 'static_core_ontology.md']:  # 跳过说明文件
            print(f"  处理: {file_path.name}")
            extract_knowledge_from_file(file_path, g, extender)
    
    # 保存RDF图谱
    output_file = "/tmp/knowledge_extended.ttl"
    g.serialize(destination=output_file, format="turtle")
    print(f"\n✅ 扩展的知识图谱已生成: {output_file}")
    
    # 生成扩展报告
    report_file = "/tmp/ontology_extension_report.md"
    generate_extension_report(extender, report_file)
    
    # 统计信息
    print(f"\n统计信息:")
    print(f"  - 核心概念: 10个")
    print(f"  - Agent扩展: {len(extender.extensions)}个")
    print(f"  - 总三元组: {len(g)}个")
    print(f"  - 需要审核: {sum(1 for x in extender.extensions.values() if x['confidence'] < 0.8)}个")
    
    return output_file, report_file

if __name__ == "__main__":
    main()