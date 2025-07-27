#!/usr/bin/env python3
"""独立的编译脚本，直接使用LangChain"""

import os
import time
from pathlib import Path
from datetime import datetime
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from pydantic import BaseModel, Field

# 设置缓存
set_llm_cache(SQLiteCache(database_path=".langchain_cache.db"))

class FileWriteInput(BaseModel):
    """写入文件的输入参数"""
    file_path: str = Field(description="要写入的文件路径")
    content: str = Field(description="文件内容")

def compile_user_management():
    """编译用户管理PIM"""
    print("=== Standalone Compilation with LangChain ===")
    print(f"Working directory: {os.getcwd()}")
    
    # 读取PIM
    pim_file = Path("examples/user_management.md")
    if not pim_file.exists():
        print(f"❌ PIM file not found: {pim_file}")
        return
    
    pim_content = pim_file.read_text(encoding='utf-8')
    print(f"✅ Loaded PIM: {pim_file}")
    
    # 设置输出目录
    output_dir = Path("output/standalone_compile")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化LLM
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not set")
        return
    
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com",
        temperature=0.7
    )
    
    print("\n1. Generating PSM...")
    
    # 生成PSM
    psm_prompt = f"""你是一个专业的软件架构师，负责生成 PSM（Platform Specific Model）。

目标平台: FastAPI
技术栈:
- 框架: FastAPI
- ORM: SQLAlchemy
- 验证库: Pydantic

请根据以下PIM生成详细的PSM文档：

{pim_content}

要求：
1. 包含详细的数据模型定义（字段类型、约束等）
2. API端点设计（RESTful）
3. 服务层方法定义
4. 配置说明
"""
    
    start_time = time.time()
    response = llm.invoke([
        SystemMessage(content="你是一个专业的软件架构师"),
        HumanMessage(content=psm_prompt)
    ])
    
    psm_content = response.content
    psm_time = time.time() - start_time
    
    # 保存PSM
    psm_file = output_dir / "user_management_psm.md"
    psm_file.write_text(psm_content, encoding='utf-8')
    print(f"✅ PSM generated in {psm_time:.2f}s")
    
    print("\n2. Generating code with agent...")
    
    # 创建代理工具
    @tool("write_file", args_schema=FileWriteInput)
    def write_file(file_path: str, content: str) -> str:
        """写入文件到指定路径"""
        try:
            full_path = output_dir / "generated" / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            return f"Successfully wrote file: {file_path}"
        except Exception as e:
            return f"Error writing file {file_path}: {str(e)}"
    
    # 创建代理
    tools = [write_file]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的代码生成助手，负责根据PSM生成高质量的FastAPI应用代码。

你需要：
1. 生成完整的项目结构
2. 包含所有必要的文件
3. 使用FastAPI、SQLAlchemy、Pydantic
4. 生成requirements.txt
5. 生成README.md

记住：每个Python包都需要__init__.py文件。"""),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=15
    )
    
    # 执行代码生成
    code_prompt = f"""请根据以下PSM生成完整的FastAPI应用代码：

{psm_content}

要求：
1. 创建正确的目录结构
2. 生成所有必要的代码文件
3. 包含__init__.py文件
4. 生成requirements.txt和README.md
"""
    
    start_time = time.time()
    result = agent_executor.invoke({"input": code_prompt})
    code_time = time.time() - start_time
    
    print(f"\n✅ Code generated in {code_time:.2f}s")
    
    # 统计生成的文件
    generated_dir = output_dir / "generated"
    if generated_dir.exists():
        py_files = list(generated_dir.rglob("*.py"))
        print(f"Generated {len(py_files)} Python files")
    
    print(f"\n✅ Compilation complete!")
    print(f"Output directory: {output_dir}")
    
    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "psm_generation_time": psm_time,
        "code_generation_time": code_time,
        "total_time": psm_time + code_time,
        "output_directory": str(output_dir)
    }
    
    report_file = output_dir / "compilation_report.json"
    report_file.write_text(json.dumps(report, indent=2), encoding='utf-8')

if __name__ == "__main__":
    compile_user_management()