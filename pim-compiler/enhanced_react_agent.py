#!/usr/bin/env python3
"""增强版 ReactAgent - 整合多种知识注入方法"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from pydantic import BaseModel, Field

# 设置缓存
set_llm_cache(SQLiteCache(database_path=".langchain_cache.db"))


class KnowledgeInjector:
    """知识注入管理器"""
    
    def __init__(self, knowledge_dir: str = "./knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_cache = {}
        
    def load_knowledge_files(self) -> Dict[str, str]:
        """加载所有知识文件"""
        knowledge = {}
        
        # 加载不同类型的知识
        categories = [
            "best_practices",
            "error_solutions", 
            "code_templates",
            "design_patterns",
            "api_examples"
        ]
        
        for category in categories:
            category_path = self.knowledge_dir / category
            if category_path.exists():
                knowledge[category] = {}
                for file in category_path.glob("*.md"):
                    content = file.read_text(encoding='utf-8')
                    knowledge[category][file.stem] = content
                    
        return knowledge
    
    def get_relevant_knowledge(self, context: str) -> str:
        """根据上下文获取相关知识"""
        relevant_knowledge = []
        
        # 关键词匹配
        keywords = {
            "fastapi": ["fastapi_patterns", "api_examples"],
            "error": ["error_solutions", "troubleshooting"],
            "test": ["testing_best_practices", "test_templates"],
            "auth": ["authentication_patterns", "security_best_practices"],
            "database": ["database_patterns", "orm_best_practices"]
        }
        
        for keyword, knowledge_files in keywords.items():
            if keyword.lower() in context.lower():
                for file in knowledge_files:
                    if file in self.knowledge_cache:
                        relevant_knowledge.append(self.knowledge_cache[file])
                        
        return "\n\n".join(relevant_knowledge)


class ProjectContext:
    """项目上下文管理"""
    
    def __init__(self):
        self.context = {
            "generated_files": [],
            "errors_encountered": [],
            "fixes_applied": [],
            "dependencies": set(),
            "test_results": []
        }
    
    def add_file(self, file_path: str, content: str):
        """记录生成的文件"""
        self.context["generated_files"].append({
            "path": file_path,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_error(self, error: str, solution: str = None):
        """记录遇到的错误"""
        self.context["errors_encountered"].append({
            "error": error,
            "solution": solution,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        return f"""
当前项目状态：
- 已生成文件: {len(self.context['generated_files'])}
- 遇到的错误: {len(self.context['errors_encountered'])}
- 应用的修复: {len(self.context['fixes_applied'])}
- 项目依赖: {', '.join(self.context['dependencies'])}
"""


class EnhancedReactAgentGenerator:
    """增强版 React Agent 生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.knowledge_injector = KnowledgeInjector()
        self.project_context = ProjectContext()
        self.llm = self._create_llm()
        
        # 加载所有知识
        self.knowledge_base = self.knowledge_injector.load_knowledge_files()
        
    def _create_llm(self):
        """创建 LLM 实例"""
        return ChatOpenAI(
            model="deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
            temperature=0,
            max_tokens=4000
        )
    
    def _create_enhanced_tools(self, output_dir: str):
        """创建增强的工具集"""
        
        # 原有工具
        @tool("write_file")
        def write_file(file_path: str, content: str) -> str:
            """写入文件"""
            try:
                full_path = Path(output_dir) / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                
                # 记录到上下文
                self.project_context.add_file(file_path, content)
                
                return f"Successfully wrote file: {file_path}"
            except Exception as e:
                return f"Error writing file: {str(e)}"
        
        # 知识搜索工具
        @tool("search_knowledge")
        def search_knowledge(query: str) -> str:
            """搜索项目知识库"""
            relevant = self.knowledge_injector.get_relevant_knowledge(query)
            if relevant:
                return f"找到相关知识：\n{relevant}"
            return "未找到相关知识，建议查看最佳实践文档"
        
        # 错误诊断工具
        @tool("diagnose_error")
        def diagnose_error(error_message: str) -> str:
            """诊断错误并提供解决方案"""
            solutions = {
                "regex is removed": "使用 pattern 替代 regex 参数",
                "BaseSettings": "从 pydantic_settings 导入 BaseSettings",
                "orm_mode": "使用 from_attributes 替代 orm_mode",
                "ModuleNotFoundError": "确保所有目录都有 __init__.py 文件",
                "email-validator": "添加 pydantic[email] 到依赖"
            }
            
            for error_key, solution in solutions.items():
                if error_key in error_message:
                    self.project_context.add_error(error_message, solution)
                    return f"错误诊断：{solution}"
                    
            return "请检查错误信息，可能需要更新依赖或修改代码"
        
        # 依赖管理工具
        @tool("manage_dependencies")
        def manage_dependencies(action: str, package: str = None) -> str:
            """管理项目依赖"""
            if action == "add" and package:
                self.project_context.context["dependencies"].add(package)
                return f"已添加依赖: {package}"
            elif action == "list":
                deps = self.project_context.context["dependencies"]
                return f"当前依赖: {', '.join(deps)}" if deps else "暂无依赖"
            return "未知操作"
        
        return [write_file, search_knowledge, diagnose_error, manage_dependencies]
    
    def _create_enhanced_prompt(self) -> ChatPromptTemplate:
        """创建增强的提示词模板"""
        system_prompt = f"""你是一个专业的代码生成助手，拥有丰富的知识库和智能诊断能力。

## 你的能力：
1. 访问项目知识库 - 使用 search_knowledge 工具
2. 智能错误诊断 - 使用 diagnose_error 工具
3. 依赖管理 - 使用 manage_dependencies 工具
4. 文件生成 - 使用 write_file 工具

## 工作流程：
1. 分析需求，搜索相关知识
2. 生成代码，遵循最佳实践
3. 如遇错误，立即诊断并修复
4. 持续优化直到测试通过

## 可用知识类别：
{json.dumps(list(self.knowledge_base.keys()), ensure_ascii=False)}

## 当前项目状态：
{self.project_context.get_context_summary()}

记住：充分利用知识库，生成高质量、可维护的代码。
"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
    
    def generate(self, pim_content: str, output_dir: str):
        """生成代码"""
        # 创建工具
        tools = self._create_enhanced_tools(output_dir)
        
        # 创建提示词
        prompt = self._create_enhanced_prompt()
        
        # 创建 agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=50,
            handle_parsing_errors=True
        )
        
        # 执行生成
        input_prompt = f"""
基于以下 PIM 内容生成完整的 FastAPI 应用：

{pim_content}

要求：
1. 首先搜索相关的最佳实践
2. 生成符合规范的代码结构
3. 包含完整的错误处理
4. 添加适当的测试用例
5. 确保所有依赖都被正确管理
"""
        
        result = executor.invoke({"input": input_prompt})
        
        # 生成项目报告
        self._generate_report(output_dir)
        
        return result
    
    def _generate_report(self, output_dir: str):
        """生成项目报告"""
        report = {
            "generation_time": datetime.now().isoformat(),
            "files_generated": len(self.project_context.context["generated_files"]),
            "errors_fixed": len(self.project_context.context["errors_encountered"]),
            "dependencies": list(self.project_context.context["dependencies"]),
            "context": self.project_context.context
        }
        
        report_path = Path(output_dir) / "generation_report.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))


# 使用示例
if __name__ == "__main__":
    config = {
        "platform": "fastapi",
        "output_dir": "./output/enhanced_agent"
    }
    
    generator = EnhancedReactAgentGenerator(config)
    
    # 这里可以调用 generator.generate(pim_content, output_dir)