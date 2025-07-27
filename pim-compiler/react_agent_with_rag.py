#!/usr/bin/env python3
"""ReactAgent with RAG (Retrieval Augmented Generation)"""

import os
from pathlib import Path
from typing import List, Dict, Any
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader, MarkdownTextLoader
from langchain.schema import Document
from langchain.tools import Tool

class KnowledgeBase:
    """知识库管理类"""
    
    def __init__(self, persist_directory="./knowledge_db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com/v1"
        )
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def load_documents(self, directory: str, glob_pattern: str = "**/*.md"):
        """从目录加载文档"""
        loader = DirectoryLoader(
            directory,
            glob=glob_pattern,
            loader_cls=MarkdownTextLoader
        )
        documents = loader.load()
        return self.text_splitter.split_documents(documents)
    
    def create_vector_store(self, documents: List[Document]):
        """创建向量存储"""
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """搜索相关文档"""
        if not self.vector_store:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        return self.vector_store.similarity_search(query, k=k)


def create_knowledge_search_tool(knowledge_base: KnowledgeBase):
    """创建知识搜索工具"""
    def search_knowledge(query: str) -> str:
        """搜索项目知识库中的相关信息"""
        results = knowledge_base.search(query, k=3)
        if not results:
            return "未找到相关知识"
        
        context = "\n\n".join([
            f"来源: {doc.metadata.get('source', 'unknown')}\n内容: {doc.page_content}"
            for doc in results
        ])
        return f"找到以下相关知识：\n\n{context}"
    
    return Tool(
        name="search_knowledge",
        description="搜索项目知识库，包括最佳实践、设计模式、常见问题等",
        func=search_knowledge
    )


# 使用示例
def setup_knowledge_base():
    """设置知识库"""
    kb = KnowledgeBase()
    
    # 加载不同类型的知识
    knowledge_dirs = {
        "best_practices": "./knowledge/best_practices",
        "design_patterns": "./knowledge/design_patterns", 
        "troubleshooting": "./knowledge/troubleshooting",
        "api_examples": "./knowledge/api_examples"
    }
    
    all_documents = []
    for category, directory in knowledge_dirs.items():
        if Path(directory).exists():
            docs = kb.load_documents(directory)
            # 添加元数据
            for doc in docs:
                doc.metadata["category"] = category
            all_documents.extend(docs)
    
    # 创建向量存储
    kb.create_vector_store(all_documents)
    return kb


# 集成到ReactAgent
def enhance_react_agent_with_knowledge(agent_executor, knowledge_base):
    """增强ReactAgent with知识库"""
    # 添加知识搜索工具
    knowledge_tool = create_knowledge_search_tool(knowledge_base)
    
    # 将工具添加到agent
    agent_executor.tools.append(knowledge_tool)
    
    # 修改系统提示词
    enhanced_prompt = """
你是一个专业的代码生成助手，拥有丰富的项目知识库。

在生成代码时：
1. 首先使用 search_knowledge 工具搜索相关的最佳实践和示例
2. 参考知识库中的设计模式和代码规范
3. 如果遇到错误，搜索故障排除指南
4. 生成的代码应该遵循知识库中的标准

记住：知识库是你的重要资源，充分利用它来生成高质量的代码。
"""
    
    return agent_executor