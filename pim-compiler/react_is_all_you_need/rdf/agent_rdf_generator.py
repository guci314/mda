#!/usr/bin/env python3
"""
使用Agent智能生成RDF知识图谱
展示Agent如何理解代码并生成语义丰富的知识图谱
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal
from pathlib import Path

class AgentRDFGenerator:
    """使用Agent生成RDF知识图谱"""
    
    def __init__(self, model="x-ai/grok-code-fast-1"):
        """初始化Agent"""
        self.model = model
        self.agent = None
        
    def create_agent(self, knowledge_files):
        """创建配置好的Agent"""
        self.agent = ReactAgentMinimal(
            work_dir="/tmp",
            model=self.model,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            knowledge_files=knowledge_files,
            max_rounds=50
        )
        return self.agent
    
    def generate_code_rdf(self, source_dir, output_file):
        """让Agent分析代码并生成RDF"""
        
        print("🤖 创建代码分析Agent...")
        
        # 使用RDF转换知识
        agent = self.create_agent([
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/universal_to_rdf_knowledge.md",
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/static_core_ontology.md"
        ])
        
        # 构建任务
        task = f"""
        分析Python代码库并生成RDF知识图谱：
        
        1. 调用 构建知识图谱("{source_dir}", "{output_file}")
           重点要求：
           - 提取所有docstring（模块级、类级、方法级）
           - 识别类继承关系
           - 分析函数调用关系
           - 提取导入依赖
        
        2. 对每个发现的概念：
           - 基于静态核心本体进行扩展
           - 生成自然语言描述
           - 计算语义向量
        
        3. 调用 符号主义验证流程("{output_file}")
           确保生成的RDF格式正确
        
        4. 生成分析报告，包括：
           - 发现的核心类和方法
           - 主要的设计模式
           - 模块间依赖关系
        
        最终输出：
        - RDF文件：{output_file}
        - 分析报告：{output_file.replace('.ttl', '_analysis.md')}
        """
        
        print("📊 开始分析代码库...")
        result = agent.execute(task)
        
        print("\n✅ Agent分析完成")
        return result
    
    def generate_knowledge_rdf(self, knowledge_dir, output_file):
        """让Agent分析知识文档并生成RDF"""
        
        print("🤖 创建知识分析Agent...")
        
        # 使用知识本体
        agent = self.create_agent([
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/agent_knowledge_ontology.md",
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/static_core_ontology.md"
        ])
        
        # 构建任务
        task = f"""
        分析知识文档目录并生成RDF知识图谱：
        
        1. 扫描 {knowledge_dir} 目录下的所有.md文件
        
        2. 识别并提取：
           - 自然语言函数（函数：xxx）
           - SOP标准流程
           - 核心概念定义
           - Agent配置
           - 工具使用说明
        
        3. 基于静态核心本体动态扩展：
           - 为每个新概念生成自然语言说明
           - 计算语义向量用于概念对齐
           - 标记置信度
        
        4. 建立知识关联：
           - 函数调用关系
           - SOP实现关系
           - 概念依赖关系
        
        5. 生成知识概览报告
        
        输出文件：{output_file}
        """
        
        print("📚 开始分析知识库...")
        result = agent.execute(task)
        
        print("\n✅ Agent分析完成")
        return result
    
    def analyze_and_compare(self, code_rdf, knowledge_rdf):
        """让Agent对比分析代码和知识的一致性"""
        
        print("🤖 创建对比分析Agent...")
        
        agent = self.create_agent([
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/rdf_semantic_search_knowledge.md"
        ])
        
        task = f"""
        对比分析代码实现和知识定义的一致性：
        
        1. 加载两个RDF文件：
           - 代码RDF：{code_rdf}
           - 知识RDF：{knowledge_rdf}
        
        2. 查找对应关系：
           - 知识中定义的函数 vs 代码中的实现
           - 知识中的Agent配置 vs 代码中的Agent类
           - 知识中的工具说明 vs 代码中的工具实现
        
        3. 识别差异：
           - 知识中有但代码中没有的（待实现）
           - 代码中有但知识中没有的（待文档化）
           - 描述不一致的地方
        
        4. 生成一致性报告
        
        重点关注ReactAgentMinimal的实现是否符合知识文档的描述
        """
        
        print("🔍 开始一致性分析...")
        result = agent.execute(task)
        
        return result

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='使用Agent生成RDF知识图谱')
    parser.add_argument('--mode', choices=['code', 'knowledge', 'both', 'compare'], 
                       default='code', help='生成模式')
    parser.add_argument('--source', default='/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/core',
                       help='源目录')
    parser.add_argument('--output', default='/tmp/agent_generated.ttl',
                       help='输出文件')
    
    args = parser.parse_args()
    
    generator = AgentRDFGenerator()
    
    if args.mode == 'code':
        # 生成代码RDF
        generator.generate_code_rdf(args.source, args.output)
        
    elif args.mode == 'knowledge':
        # 生成知识RDF
        knowledge_dir = '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge'
        generator.generate_knowledge_rdf(knowledge_dir, args.output)
        
    elif args.mode == 'both':
        # 同时生成两种RDF
        code_rdf = '/tmp/agent_code.ttl'
        knowledge_rdf = '/tmp/agent_knowledge.ttl'
        
        generator.generate_code_rdf(args.source, code_rdf)
        
        knowledge_dir = '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge'
        generator.generate_knowledge_rdf(knowledge_dir, knowledge_rdf)
        
    elif args.mode == 'compare':
        # 对比分析
        code_rdf = '/tmp/code_knowledge_graph.ttl'
        knowledge_rdf = '/tmp/knowledge_extended.ttl'
        generator.analyze_and_compare(code_rdf, knowledge_rdf)

if __name__ == "__main__":
    main()