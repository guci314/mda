#!/usr/bin/env python3
"""
代码生成 Agent - 注入软件工程知识版本
使用 Function Calling Agent 从 PSM 生成代码
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

# 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
OUTPUT_DIR = Path("generated_code_with_knowledge")

# 软件工程知识注入
SOFTWARE_ENGINEERING_KNOWLEDGE = """
你是一个专业的软件工程师，精通软件架构和设计模式。以下是核心的软件工程原则和知识：

## 1. 分层架构原则
- **表现层 (Presentation Layer)**: 处理 HTTP 请求，包括路由、控制器、API 端点
- **业务逻辑层 (Business Logic Layer)**: 包含服务类、业务规则、工作流
- **数据访问层 (Data Access Layer)**: 包含仓储、数据映射、数据库交互
- **领域模型层 (Domain Model Layer)**: 核心实体、值对象、领域逻辑

## 2. 依赖关系规则
- **单向依赖**: 上层依赖下层，下层不依赖上层
- **依赖顺序**: API → Service → Repository → Domain Model
- **横向隔离**: 同层组件之间应该松耦合

## 3. 具体依赖关系
- **API/Controller** 依赖:
  - Service (注入服务处理业务逻辑)
  - Schema/DTO (请求/响应模型)
  - 不应直接依赖 Domain Model 或 Database

- **Service** 依赖:
  - Domain Model (操作领域对象)
  - Repository/DAO (数据持久化)
  - 其他 Service (业务协作)
  - Schema/DTO (数据转换)

- **Repository/DAO** 依赖:
  - Domain Model (持久化实体)
  - Database Connection (数据库连接)

- **Domain Model** 依赖:
  - 仅依赖其他 Domain Model
  - 不依赖任何基础设施代码

## 4. 文件组织最佳实践
- 每个 Python 包必须包含 __init__.py 文件
- 配置文件应该独立管理 (config.py, settings.py)
- 数据库配置应该集中管理 (database.py)
- 使用相对导入保持包的可移植性

## 5. 测试依赖关系
- **单元测试** 依赖:
  - 被测试的模块
  - Mock 对象（模拟外部依赖）
  
- **集成测试** 依赖:
  - Service 层
  - Domain Model
  - Test Database

- **API 测试** 依赖:
  - 完整的应用栈
  - Test Client
  - Test Database

## 6. 代码生成顺序（重要）
正确的生成顺序可以避免循环依赖：
1. 配置文件 (config.py, settings.py)
2. 数据库配置 (database.py)
3. Domain Model (models/*.py)
4. Schema/DTO (schemas/*.py)
5. Repository/DAO (repositories/*.py 或 crud/*.py)
6. Service Layer (services/*.py)
7. API/Controller (api/*.py, routers/*.py)
8. Main Application (main.py, app.py)
9. 测试文件 (tests/*.py)

## 7. FastAPI 特定知识
- 使用 Pydantic 进行数据验证
- 依赖注入通过 Depends() 实现
- 数据库会话通过依赖注入管理
- 路由应该分组并使用 prefix
- 使用 response_model 确保类型安全

## 8. 导入语句最佳实践
- 标准库导入放在最前
- 第三方库导入其次
- 本地导入最后
- 使用相对导入 (from . import xxx)
- 避免循环导入

记住：良好的架构是可测试、可维护、可扩展的。每个组件应该有单一职责，依赖关系应该清晰明确。
"""

class TaskLogger:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed = time.time() - self.start_time
        log_entry = f"[{timestamp}] [{level}] [+{elapsed:.1f}s] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # 同时打印到控制台
        print(log_entry.strip())

# Pydantic 模型
class FileWriteInput(BaseModel):
    """写入文件的输入参数"""
    file_path: str = Field(description="要写入的文件路径")
    content: str = Field(description="文件内容")

class FileReadInput(BaseModel):
    """读取文件的输入参数"""
    file_path: str = Field(description="要读取的文件路径")

class DirectoryListInput(BaseModel):
    """列出目录内容的输入参数"""
    directory_path: str = Field(description="要列出的目录路径")

class CreateDirectoryInput(BaseModel):
    """创建目录的输入参数"""
    directory_path: str = Field(description="要创建的目录路径")

def create_code_generation_agent(output_dir: Path, logger: TaskLogger):
    """创建具有软件工程知识的代码生成 Agent"""
    
    # 创建工具
    @tool("write_file", args_schema=FileWriteInput)
    def write_file(file_path: str, content: str) -> str:
        """写入文件到指定路径"""
        try:
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            full_path.write_text(content, encoding='utf-8')
            
            file_size = len(content)
            logger.log(f"Writing file: {file_path} ({file_size} characters)")
            
            return f"Successfully wrote file: {file_path}"
        except Exception as e:
            error_msg = f"Error writing file {file_path}: {str(e)}"
            logger.log(error_msg, "ERROR")
            return error_msg
    
    @tool("read_file", args_schema=FileReadInput)
    def read_file(file_path: str) -> str:
        """读取文件内容"""
        try:
            full_path = output_dir / file_path
            if not full_path.exists():
                return f"File not found: {file_path}"
            
            content = full_path.read_text(encoding='utf-8')
            logger.log(f"Reading file: {file_path} ({len(content)} characters)")
            return content
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {str(e)}"
            logger.log(error_msg, "ERROR")
            return error_msg
    
    @tool("list_directory", args_schema=DirectoryListInput)
    def list_directory(directory_path: str = ".") -> str:
        """列出目录中的文件和子目录"""
        try:
            full_path = output_dir / directory_path
            if not full_path.exists():
                return f"Directory not found: {directory_path}"
            
            items = []
            for item in sorted(full_path.iterdir()):
                if item.is_file():
                    items.append(f"📄 {item.name}")
                else:
                    items.append(f"📁 {item.name}/")
            
            result = "\n".join(items) if items else "Empty directory"
            logger.log(f"Listing directory: {directory_path}")
            return result
        except Exception as e:
            error_msg = f"Error listing directory {directory_path}: {str(e)}"
            logger.log(error_msg, "ERROR")
            return error_msg
    
    @tool("create_directory", args_schema=CreateDirectoryInput)
    def create_directory(directory_path: str) -> str:
        """创建目录"""
        try:
            full_path = output_dir / directory_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.log(f"Creating directory: {directory_path}")
            return f"Successfully created directory: {directory_path}"
        except Exception as e:
            error_msg = f"Error creating directory {directory_path}: {str(e)}"
            logger.log(error_msg, "ERROR")
            return error_msg
    
    # 创建 LLM
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        
    llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=DEEPSEEK_API_KEY,
        openai_api_base=DEEPSEEK_BASE_URL,
        temperature=0.1,
        max_tokens=4000
    )
    
    # 创建工具列表
    tools = [write_file, read_file, list_directory, create_directory]
    
    # 创建系统消息，注入软件工程知识
    system_prompt = f"""你是一个专业的代码生成助手，负责根据 Platform Specific Model (PSM) 生成高质量的 FastAPI 应用代码。

{SOFTWARE_ENGINEERING_KNOWLEDGE}

## 你的任务
1. 仔细阅读提供的 PSM 文档
2. 理解系统需求和架构设计
3. 按照正确的顺序生成所有必要的代码文件
4. 确保所有依赖关系正确
5. 生成可以直接运行的完整应用

## 重要提醒
- 始终遵循依赖关系规则，避免循环依赖
- 每个 Python 包都必须包含 __init__.py 文件
- 使用类型注解提高代码质量
- 添加必要的错误处理
- 生成清晰的 README.md 文档

请开始你的工作！"""
    
    # 创建 prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    
    # 创建 agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # 创建 executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=50,
        handle_parsing_errors=True
    )
    
    return agent_executor

def run_experiment(psm_file: str, experiment_name: str, logger: TaskLogger):
    """运行单个实验"""
    logger.log(f"Starting experiment: {experiment_name}")
    logger.log("=" * 60)
    
    # 创建输出目录
    output_dir = OUTPUT_DIR / experiment_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取 PSM 内容
    try:
        with open(psm_file, 'r', encoding='utf-8') as f:
            psm_content = f.read()
        logger.log(f"Loaded PSM file: {psm_file} ({len(psm_content)} characters)")
    except Exception as e:
        logger.log(f"Failed to read PSM file: {e}", "ERROR")
        return
    
    # 创建 agent
    agent = create_code_generation_agent(output_dir, logger)
    
    # 生成提示
    prompt = f"""请根据以下 PSM（Platform Specific Model）文档生成完整的 FastAPI 应用代码。

PSM 文档内容：
```markdown
{psm_content}
```

请注意：
1. 仔细分析 PSM 中定义的所有实体、服务和 API
2. 按照软件工程最佳实践组织代码结构
3. 确保所有文件都正确创建，包括 __init__.py
4. 生成可以直接运行的完整应用
5. 最后生成一个 README.md 说明如何运行项目

开始生成代码！"""
    
    logger.log("Invoking agent with PSM content")
    
    try:
        # 调用 agent
        result = agent.invoke({
            "input": prompt
        })
        
        logger.log("Agent execution completed")
        
        # 记录最终输出
        if result.get("output"):
            logger.log(f"Final output: {result['output'][:200]}...")
            
    except Exception as e:
        logger.log(f"Agent execution failed: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
    
    logger.log("=" * 60)
    logger.log(f"Experiment completed")

def main():
    """主函数"""
    # 创建带时间戳的日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 运行三个实验
    experiments = [
        {
            "psm_file": "test_psm_simple.md",
            "name": "simple_with_knowledge",
            "log_file": f"code_gen_simple_knowledge_{timestamp}.log"
        },
        {
            "psm_file": "test_psm_detailed.md", 
            "name": "detailed_with_knowledge",
            "log_file": f"code_gen_detailed_knowledge_{timestamp}.log"
        }
    ]
    
    for exp in experiments:
        logger = TaskLogger(exp["log_file"])
        logger.log(f"Starting code generation experiment with software engineering knowledge")
        logger.log(f"PSM file: {exp['psm_file']}")
        logger.log(f"Output directory: {OUTPUT_DIR / exp['name']}")
        
        run_experiment(exp["psm_file"], exp["name"], logger)
        
        # 等待一下再开始下一个实验
        time.sleep(2)

if __name__ == "__main__":
    main()