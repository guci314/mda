#!/usr/bin/env python3
"""独立运行ReactAgent生成器"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# 加载环境变量
load_dotenv()

# 工具定义
class FileInput(BaseModel):
    file_path: str = Field(description="文件路径")
    content: str = Field(description="文件内容")

class DirectoryInput(BaseModel):
    directory_path: str = Field(description="目录路径")

class CommandInput(BaseModel):
    command: str = Field(description="要执行的命令")

# 全局输出目录
output_dir = Path("output/react_agent_enhanced_v2")

@tool("write_file", args_schema=FileInput)
def write_file(file_path: str, content: str) -> str:
    """写入文件"""
    try:
        file_full_path = output_dir / file_path
        file_full_path.parent.mkdir(parents=True, exist_ok=True)
        file_full_path.write_text(content, encoding='utf-8')
        return f"Successfully wrote file: {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool("read_file", args_schema=FileInput)
def read_file(file_path: str) -> str:
    """读取文件"""
    try:
        file_full_path = output_dir / file_path
        if not file_full_path.exists():
            return f"File not found: {file_path}"
        content = file_full_path.read_text(encoding='utf-8')
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool("create_directory", args_schema=DirectoryInput)
def create_directory(directory_path: str) -> str:
    """创建目录"""
    try:
        dir_full_path = output_dir / directory_path
        dir_full_path.mkdir(parents=True, exist_ok=True)
        return f"Successfully created directory: {directory_path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@tool("list_directory", args_schema=DirectoryInput)
def list_directory(directory_path: str = ".") -> str:
    """列出目录内容"""
    try:
        dir_full_path = output_dir / directory_path
        if not dir_full_path.exists():
            return f"Directory not found: {directory_path}"
        items = []
        for item in dir_full_path.iterdir():
            if item.is_dir():
                items.append(f"[DIR] {item.name}")
            else:
                items.append(f"[FILE] {item.name}")
        return "\n".join(items) if items else "Empty directory"
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@tool("run_command", args_schema=CommandInput)
def run_command(command: str) -> str:
    """执行shell命令"""
    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(output_dir),
            timeout=30
        )
        output = result.stdout or result.stderr
        return f"Exit code: {result.returncode}\nOutput:\n{output}"
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error running command: {str(e)}"

def generate_psm(pim_content: str) -> str:
    """生成PSM"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set")
    
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0.7
    )
    
    prompt = f"""你是一个专业的软件架构师，负责生成 PSM（Platform Specific Model）。

目标平台: FastAPI

请根据以下PIM生成详细的PSM文档：

{pim_content}

要求：
1. 包含详细的数据模型定义（字段类型、约束等）
2. API端点设计（RESTful）  
3. 服务层方法定义
4. 认证和权限控制
5. 数据库设计

请使用Markdown格式输出。"""

    response = llm.invoke(prompt)
    return response.content

def generate_code(psm_content: str):
    """使用React Agent生成代码"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set")
    
    # 创建LLM
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0.7
    )
    
    # 工具列表
    tools = [
        write_file,
        read_file,
        create_directory,
        list_directory,
        run_command
    ]
    
    # 系统提示词
    system_prompt = """你是一个专业的 FastAPI 开发专家。

你的任务是根据 PSM（Platform Specific Model）生成完整的 FastAPI 应用代码。

要求：
1. 创建清晰的项目结构
2. 实现所有的数据模型、API端点和服务
3. 包含适当的错误处理和验证
4. 生成 requirements.txt
5. 创建 README.md 文档

请一步步地创建项目结构和文件。"""

    # 创建prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    # 创建agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=30,
        handle_parsing_errors=True
    )
    
    # 执行生成
    input_prompt = f"""请根据以下PSM生成完整的FastAPI应用代码：

{psm_content}

请创建完整的项目结构，包括所有必要的文件。"""

    executor.invoke({"input": input_prompt})

def main():
    """主函数"""
    print("=== ReactAgent Standalone Compilation ===")
    
    # 检查API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not set")
        return
    
    # 读取PIM
    pim_file = Path("../models/domain/用户管理_pim.md")
    if not pim_file.exists():
        print(f"❌ PIM file not found: {pim_file}")
        return
    
    pim_content = pim_file.read_text(encoding='utf-8')
    print(f"✅ Loaded PIM: {pim_file}")
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    try:
        # 生成PSM
        print("\n1. Generating PSM...")
        start_time = time.time()
        psm_content = generate_psm(pim_content)
        psm_time = time.time() - start_time
        
        # 保存PSM
        psm_file = output_dir / "user_management_psm.md"
        psm_file.write_text(psm_content, encoding='utf-8')
        print(f"✅ PSM generated in {psm_time:.2f}s")
        
        # 生成代码
        print("\n2. Generating code with React Agent...")
        start_time = time.time()
        generate_code(psm_content)
        code_time = time.time() - start_time
        print(f"✅ Code generated in {code_time:.2f}s")
        
        print(f"\n✅ Compilation complete!")
        print(f"Total time: {psm_time + code_time:.2f}s")
        print(f"Output directory: {output_dir}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()