#!/usr/bin/env python3
"""
将Python代码库转换为RDF知识图谱
使用静态核心 + 动态扩展模式
"""

import os
import ast
import rdflib
from rdflib import Namespace, RDF, RDFS, Literal, URIRef
from pathlib import Path
import hashlib
import numpy as np
from datetime import datetime

# 定义命名空间
CORE = Namespace("http://ontology.core#")  # 静态核心本体
ONTO = Namespace("http://ontology.meta#")  # 元本体
EXT = Namespace("http://ontology.ext#")    # 动态扩展
KG = Namespace("http://example.org/knowledge#")  # 代码实体

class CodeToRDFConverter:
    """将Python代码转换为RDF图谱"""
    
    def __init__(self):
        self.graph = rdflib.Graph()
        self.init_namespaces()
        self.init_static_core()
        self.extensions = {}
        self.agent_name = "CodeAnalysisAgent"
        
    def init_namespaces(self):
        """初始化命名空间"""
        self.graph.bind("core", CORE)
        self.graph.bind("onto", ONTO)
        self.graph.bind("ext", EXT)
        self.graph.bind("kg", KG)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
    
    def init_static_core(self):
        """初始化10个核心概念"""
        # 存在层
        self.graph.add((CORE.Thing, RDF.type, RDFS.Class))
        self.graph.add((CORE.Entity, RDFS.subClassOf, CORE.Thing))
        self.graph.add((CORE.Concept, RDFS.subClassOf, CORE.Thing))
        
        # 关系层
        self.graph.add((CORE.Relation, RDF.type, RDF.Property))
        self.graph.add((CORE.partOf, RDFS.subPropertyOf, CORE.Relation))
        self.graph.add((CORE.instanceOf, RDFS.subPropertyOf, CORE.Relation))
        self.graph.add((CORE.relatedTo, RDFS.subPropertyOf, CORE.Relation))
        
        # 过程层
        self.graph.add((CORE.Process, RDFS.subClassOf, CORE.Thing))
        self.graph.add((CORE.causes, RDFS.subPropertyOf, CORE.Relation))
        self.graph.add((CORE.transformsTo, RDFS.subPropertyOf, CORE.Relation))
    
    def generate_embedding(self, text):
        """生成语义向量（模拟）"""
        hash_obj = hashlib.sha256(text.encode())
        hash_hex = hash_obj.hexdigest()
        np.random.seed(int(hash_hex[:8], 16))
        embedding = np.random.randn(768)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()
    
    def extend_concept(self, concept_name, parent_class, nl_description, nl_context, nl_example, confidence=0.9):
        """动态扩展概念"""
        if concept_name in self.extensions:
            return EXT[concept_name]
        
        concept_uri = EXT[concept_name]
        
        # 添加类定义
        self.graph.add((concept_uri, RDF.type, RDFS.Class))
        self.graph.add((concept_uri, RDFS.subClassOf, parent_class))
        
        # 添加自然语言说明
        self.graph.add((concept_uri, ONTO.nlDescription, Literal(nl_description)))
        self.graph.add((concept_uri, ONTO.nlContext, Literal(nl_context)))
        self.graph.add((concept_uri, ONTO.nlExample, Literal(nl_example)))
        
        # 生成语义向量
        full_text = f"{nl_description} {nl_context} {nl_example}"
        embedding = self.generate_embedding(full_text)
        embedding_str = ",".join([f"{x:.4f}" for x in embedding[:10]])
        self.graph.add((concept_uri, ONTO.embedding, Literal(f"[{embedding_str}...]")))
        
        # 添加元数据
        self.graph.add((concept_uri, ONTO.createdBy, Literal(self.agent_name)))
        self.graph.add((concept_uri, ONTO.confidence, Literal(confidence)))
        
        self.extensions[concept_name] = True
        return concept_uri
    
    def ensure_code_concepts(self):
        """确保代码相关概念已扩展"""
        # Module概念
        self.extend_concept(
            "Module",
            CORE.Entity,
            "A Python module that contains definitions and statements",
            "Basic unit of code organization in Python",
            "react_agent_minimal.py - a module containing agent implementation",
            0.95
        )
        
        # Class概念
        self.extend_concept(
            "Class",
            CORE.Entity,
            "A template for creating objects with attributes and methods",
            "Object-oriented programming construct for encapsulation",
            "class ReactAgentMinimal: defines an agent class",
            0.94
        )
        
        # Method概念
        self.extend_concept(
            "Method",
            CORE.Process,
            "A function defined inside a class that operates on instances",
            "Behavior definition for objects",
            "def execute(self, task): method that executes a task",
            0.93
        )
        
        # Function概念
        self.extend_concept(
            "Function",
            CORE.Process,
            "A reusable block of code that performs a specific task",
            "Basic unit of procedural programming",
            "def process_data(input): standalone function",
            0.92
        )
        
        # Import概念
        self.extend_concept(
            "Import",
            CORE.Relation,
            "A dependency relationship where one module uses another",
            "Module dependency mechanism in Python",
            "import numpy as np - imports numpy module",
            0.91
        )
    
    def process_python_file(self, file_path):
        """处理单个Python文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"  ⚠️ 语法错误，跳过: {file_path}")
            return
        
        # 创建模块实体
        module_name = file_path.stem
        module_uri = KG[f"module_{module_name}"]
        
        self.graph.add((module_uri, RDF.type, EXT.Module))
        self.graph.add((module_uri, KG.hasName, Literal(module_name)))
        self.graph.add((module_uri, KG.hasPath, Literal(str(file_path))))
        
        # 提取模块docstring
        module_doc = ast.get_docstring(tree)
        if module_doc:
            self.graph.add((module_uri, KG.hasModuleDocstring, Literal(module_doc)))
            # 添加自然语言描述
            self.graph.add((module_uri, ONTO.nlDescription, 
                          Literal(module_doc[:200] if len(module_doc) > 200 else module_doc)))
        
        # 处理导入
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_name = alias.name
                    import_uri = KG[f"import_{import_name}"]
                    self.graph.add((module_uri, EXT.Import, import_uri))
                    self.graph.add((import_uri, KG.hasName, Literal(import_name)))
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_uri = KG[f"import_{node.module}"]
                    self.graph.add((module_uri, EXT.Import, import_uri))
                    self.graph.add((import_uri, KG.hasName, Literal(node.module)))
        
        # 处理类
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_uri = KG[f"class_{module_name}_{node.name}"]
                
                self.graph.add((class_uri, RDF.type, EXT.Class))
                self.graph.add((class_uri, KG.hasName, Literal(node.name)))
                self.graph.add((class_uri, CORE.partOf, module_uri))
                
                # 提取类docstring
                class_doc = ast.get_docstring(node)
                if class_doc:
                    self.graph.add((class_uri, KG.hasClassDocstring, Literal(class_doc)))
                    self.graph.add((class_uri, ONTO.nlDescription,
                                  Literal(class_doc[:200] if len(class_doc) > 200 else class_doc)))
                
                # 处理继承
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_uri = KG[f"class_{base.id}"]
                        self.graph.add((class_uri, KG.inheritsFrom, base_uri))
                
                # 处理方法
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_uri = KG[f"method_{module_name}_{node.name}_{item.name}"]
                        
                        self.graph.add((method_uri, RDF.type, EXT.Method))
                        self.graph.add((method_uri, KG.hasName, Literal(item.name)))
                        self.graph.add((method_uri, CORE.partOf, class_uri))
                        
                        # 提取方法docstring
                        method_doc = ast.get_docstring(item)
                        if method_doc:
                            self.graph.add((method_uri, KG.hasMethodDocstring, Literal(method_doc)))
                            self.graph.add((method_uri, ONTO.nlDescription,
                                          Literal(method_doc[:200] if len(method_doc) > 200 else method_doc)))
                        
                        # 参数信息
                        params = [arg.arg for arg in item.args.args]
                        if params:
                            self.graph.add((method_uri, KG.hasParameters, 
                                          Literal(", ".join(params))))
        
        # 处理模块级函数
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                func_uri = KG[f"function_{module_name}_{node.name}"]
                
                self.graph.add((func_uri, RDF.type, EXT.Function))
                self.graph.add((func_uri, KG.hasName, Literal(node.name)))
                self.graph.add((func_uri, CORE.partOf, module_uri))
                
                # 提取函数docstring
                func_doc = ast.get_docstring(node)
                if func_doc:
                    self.graph.add((func_uri, KG.hasFunctionDocstring, Literal(func_doc)))
                    self.graph.add((func_uri, ONTO.nlDescription,
                                  Literal(func_doc[:200] if len(func_doc) > 200 else func_doc)))
    
    def convert_directory(self, directory_path):
        """转换整个目录的Python代码"""
        directory = Path(directory_path)
        
        # 确保代码概念已定义
        self.ensure_code_concepts()
        
        print(f"开始转换目录: {directory}")
        print("使用静态核心 + 动态扩展模式")
        
        # 收集所有Python文件
        py_files = list(directory.rglob("*.py"))
        
        for py_file in py_files:
            if '__pycache__' not in str(py_file):
                print(f"  处理: {py_file.relative_to(directory)}")
                self.process_python_file(py_file)
        
        print(f"\n转换完成:")
        print(f"  - 文件数: {len(py_files)}")
        print(f"  - 三元组数: {len(self.graph)}")
        print(f"  - 扩展概念: {len(self.extensions)}")
    
    def save(self, output_file):
        """保存RDF图谱"""
        self.graph.serialize(destination=output_file, format="turtle")
        print(f"\n✅ RDF图谱已保存: {output_file}")
    
    def generate_report(self):
        """生成转换报告"""
        report = []
        report.append("# 代码库RDF转换报告\n")
        report.append(f"生成时间: {datetime.now().isoformat()}\n\n")
        
        report.append("## 扩展概念\n")
        for concept in self.extensions:
            report.append(f"- ext:{concept}\n")
        
        report.append("\n## 统计信息\n")
        
        # 统计各类实体
        modules = len(list(self.graph.subjects(RDF.type, EXT.Module)))
        classes = len(list(self.graph.subjects(RDF.type, EXT.Class)))
        methods = len(list(self.graph.subjects(RDF.type, EXT.Method)))
        functions = len(list(self.graph.subjects(RDF.type, EXT.Function)))
        
        report.append(f"- 模块数: {modules}\n")
        report.append(f"- 类数: {classes}\n")
        report.append(f"- 方法数: {methods}\n")
        report.append(f"- 函数数: {functions}\n")
        report.append(f"- 总三元组: {len(self.graph)}\n")
        
        return "".join(report)

def main():
    import sys
    
    # 默认转换core目录
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/core"
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = "/tmp/code_knowledge_graph.ttl"
    
    # 创建转换器
    converter = CodeToRDFConverter()
    
    # 转换目录
    converter.convert_directory(source_dir)
    
    # 保存结果
    converter.save(output_file)
    
    # 生成报告
    report = converter.generate_report()
    report_file = output_file.replace('.ttl', '_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 转换报告已保存: {report_file}")

if __name__ == "__main__":
    main()