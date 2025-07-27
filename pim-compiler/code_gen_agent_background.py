#!/usr/bin/env python3
"""
代码生成 Agent - 后台运行版本
设计为可以在后台长时间运行，完成整个代码生成任务
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field


# 日志记录器
class TaskLogger:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed = time.time() - self.start_time
        log_entry = f"[{timestamp}] [{level}] [+{elapsed:.1f}s] {message}\n"
        
        # 打印到控制台
        print(log_entry.strip())
        
        # 写入日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


# 定义工具参数模型
class ReadFileInput(BaseModel):
    """读取文件的参数"""
    file_path: str = Field(description="要读取的文件路径")


class WriteFileInput(BaseModel):
    """写入文件的参数"""
    file_path: str = Field(description="要写入的文件路径")
    content: str = Field(description="要写入的内容")


class ListDirectoryInput(BaseModel):
    """列出目录的参数"""
    directory: str = Field(description="要列出的目录路径")


class CreateDirectoryInput(BaseModel):
    """创建目录的参数"""
    directory: str = Field(description="要创建的目录路径")


# 全局日志记录器（在创建工具之前初始化）
logger = None


# 工具实现
@tool("read_file", args_schema=ReadFileInput)
def read_file(file_path: str) -> str:
    """读取文件内容"""
    try:
        if logger:
            logger.log(f"Reading file: {file_path}")
        
        path = Path(file_path)
        if not path.exists():
            return f"错误：文件 {file_path} 不存在"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if logger:
            logger.log(f"Successfully read {len(content)} characters from {file_path}")
        
        return f"文件 {file_path} 的内容：\n{content}"
    except Exception as e:
        error_msg = f"读取文件错误：{str(e)}"
        if logger:
            logger.log(error_msg, "ERROR")
        return error_msg


@tool("write_file", args_schema=WriteFileInput)
def write_file(file_path: str, content: str) -> str:
    """写入文件内容"""
    try:
        if logger:
            logger.log(f"Writing file: {file_path} ({len(content)} characters)")
        
        path = Path(file_path)
        # 创建父目录
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if logger:
            logger.log(f"Successfully wrote file: {file_path}")
        
        return f"成功写入文件：{file_path}"
    except Exception as e:
        error_msg = f"写入文件错误：{str(e)}"
        if logger:
            logger.log(error_msg, "ERROR")
        return error_msg


@tool("list_directory", args_schema=ListDirectoryInput)
def list_directory(directory: str) -> str:
    """列出目录内容"""
    try:
        if logger:
            logger.log(f"Listing directory: {directory}")
        
        path = Path(directory)
        if not path.exists():
            return f"错误：目录 {directory} 不存在"
        
        if not path.is_dir():
            return f"错误：{directory} 不是目录"
        
        items = []
        for item in sorted(path.iterdir()):
            if item.is_dir():
                items.append(f"[目录] {item.name}/")
            else:
                items.append(f"[文件] {item.name}")
        
        if not items:
            return f"目录 {directory} 是空的"
        
        if logger:
            logger.log(f"Found {len(items)} items in {directory}")
        
        return f"目录 {directory} 的内容：\n" + "\n".join(items)
    except Exception as e:
        error_msg = f"列出目录错误：{str(e)}"
        if logger:
            logger.log(error_msg, "ERROR")
        return error_msg


@tool("create_directory", args_schema=CreateDirectoryInput)
def create_directory(directory: str) -> str:
    """创建目录"""
    try:
        if logger:
            logger.log(f"Creating directory: {directory}")
        
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        
        if logger:
            logger.log(f"Successfully created directory: {directory}")
        
        return f"成功创建目录：{directory}"
    except Exception as e:
        error_msg = f"创建目录错误：{str(e)}"
        if logger:
            logger.log(error_msg, "ERROR")
        return error_msg


def create_code_gen_agent(llm_config: Optional[Dict[str, Any]] = None):
    """创建代码生成 Agent"""
    
    # 工具列表
    tools = [
        read_file,
        write_file,
        list_directory,
        create_directory
    ]
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的代码生成助手。你的任务是根据 PSM（平台特定模型）文档生成完整的代码实现。

工作流程：
1. 仔细阅读 PSM 文档，理解系统架构和模块结构
2. 分析文件之间的依赖关系
3. 创建必要的目录结构
4. 按照正确的顺序生成代码文件
5. 确保模块之间的依赖关系正确
6. 生成完成后，创建一个 README.md 文件说明如何运行项目

注意事项：
- 生成的代码要完整、可运行
- 遵循 Python/FastAPI 最佳实践
- 正确处理导入和依赖关系
- 使用类型注解
- 添加必要的错误处理
- 考虑文件生成顺序，避免循环依赖

你可以使用以下工具：
- read_file: 读取文件内容
- write_file: 写入文件
- list_directory: 列出目录内容
- create_directory: 创建目录

请逐步完成代码生成任务，不要着急，确保质量。"""),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 创建 LLM
    if llm_config is None:
        llm_config = {"model": "gpt-3.5-turbo", "temperature": 0.3}
    
    # 参数名转换
    if "openai_api_key" in llm_config:
        llm_config["api_key"] = llm_config.pop("openai_api_key")
    if "openai_api_base" in llm_config:
        llm_config["base_url"] = llm_config.pop("openai_api_base")
    
    llm = ChatOpenAI(**llm_config)
    
    # 创建 Agent
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # 创建 AgentExecutor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=50,  # 增加迭代次数，确保能完成任务
        handle_parsing_errors=True,
        max_execution_time=1800  # 30分钟超时
    )
    
    return agent_executor


def run_code_generation(psm_file: str, output_dir: str, scenario: str):
    """运行代码生成任务"""
    global logger
    
    # 创建日志文件
    log_file = f"code_gen_{scenario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = TaskLogger(log_file)
    
    logger.log("=" * 60)
    logger.log(f"Starting code generation experiment: {scenario}")
    logger.log(f"PSM file: {psm_file}")
    logger.log(f"Output directory: {output_dir}")
    logger.log("=" * 60)
    
    # 配置 LLM
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        logger.log("DEEPSEEK_API_KEY not set", "ERROR")
        return
    
    llm_config = {
        "api_key": deepseek_key,
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "temperature": 0.3
    }
    logger.log("Using DeepSeek model")
    
    # 创建 agent
    logger.log("Creating code generation agent...")
    agent = create_code_gen_agent(llm_config)
    
    # 构建任务提示
    prompt = f"""请阅读 {psm_file} 文件中的 PSM 文档，并在 {output_dir} 目录下生成完整的 FastAPI 项目代码。

要求：
1. 创建完整的项目结构
2. 生成所有必要的代码文件
3. 确保代码可以运行
4. 遵循 FastAPI 最佳实践
5. 生成完成后，创建 README.md 说明如何安装和运行项目

请仔细分析 PSM 文档，理解所有的依赖关系，然后开始生成代码。"""
    
    logger.log("Starting agent execution...")
    
    try:
        # 执行代码生成
        result = agent.invoke({"input": prompt})
        
        logger.log("=" * 60)
        logger.log("Code generation completed successfully")
        logger.log(f"Final response: {result['output']}")
        
        # 保存结果摘要
        summary = {
            "scenario": scenario,
            "psm_file": psm_file,
            "output_dir": output_dir,
            "status": "success",
            "log_file": log_file,
            "completion_time": time.time() - logger.start_time,
            "final_response": result['output']
        }
        
        with open(f"{output_dir}_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logger.log(f"Error during code generation: {str(e)}", "ERROR")
        logger.log("Stack trace:", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
        
        # 保存错误摘要
        summary = {
            "scenario": scenario,
            "psm_file": psm_file,
            "output_dir": output_dir,
            "status": "error",
            "log_file": log_file,
            "error": str(e),
            "completion_time": time.time() - logger.start_time
        }
        
        with open(f"{output_dir}_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    
    logger.log("=" * 60)
    logger.log("Experiment completed")


def main():
    """主函数 - 设置实验参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Code Generation Agent')
    parser.add_argument('--scenario', type=str, required=True, 
                        choices=['simple', 'detailed'],
                        help='Scenario to run: simple or detailed')
    
    args = parser.parse_args()
    
    if args.scenario == 'simple':
        psm_file = "test_psm_simple.md"
        output_dir = "generated_code_simple"
    else:
        psm_file = "test_psm_detailed.md"
        output_dir = "generated_code_detailed"
    
    # 运行代码生成
    run_code_generation(psm_file, output_dir, args.scenario)


if __name__ == "__main__":
    main()