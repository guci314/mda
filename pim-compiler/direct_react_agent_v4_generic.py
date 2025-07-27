#!/usr/bin/env python3
"""通用 ReactAgent v4 - 领域无关版本，支持先验知识注入"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 手动导入必要的内容
from dotenv import load_dotenv
load_dotenv()

# 处理代理设置问题 - 临时禁用
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

# 直接复制ReactAgentGenerator的代码，避免导入问题
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryBufferMemory,
    ConversationBufferWindowMemory,
)
from langchain_community.chat_message_histories import (
    SQLChatMessageHistory,
)
from pydantic import BaseModel, Field

# 导入 DeepSeek token 计数修复
try:
    from deepseek_token_counter import patch_deepseek_token_counting  # type: ignore
except ImportError:
    logger.warning("deepseek_token_counter not found, token counting may fail")
    patch_deepseek_token_counting = None

# 设置缓存 - 使用绝对路径确保缓存生效
cache_path = os.path.join(os.path.dirname(__file__), ".langchain.db")
set_llm_cache(SQLiteCache(database_path=cache_path))

# 记忆级别枚举
class MemoryLevel(str, Enum):
    """记忆级别"""
    NONE = "none"              # 无记忆 - 快速简单
    SMART = "summary_buffer"   # 智能缓冲 - 平衡方案
    PRO = "sqlite"            # 持久存储 - 专业项目

# 工具定义
class FileInput(BaseModel):
    file_path: str = Field(description="文件路径")
    content: str = Field(description="文件内容")

class DirectoryInput(BaseModel):
    directory_path: str = Field(description="目录路径")

class CommandInput(BaseModel):
    command: str = Field(description="要执行的命令")
    working_dir: Optional[str] = Field(default=".", description="工作目录")

class SearchInput(BaseModel):
    pattern: str = Field(description="搜索模式")
    directory: str = Field(default=".", description="搜索目录")
    file_type: Optional[str] = Field(default=None, description="文件类型过滤")

class ReactAgentConfig:
    def __init__(self, output_dir, additional_config=None, 
                 memory_level=MemoryLevel.SMART, session_id=None, 
                 max_token_limit=30000, db_path=None,
                 knowledge_file="先验知识.md", specification=None):
        self.output_dir = output_dir
        self.additional_config = additional_config or {}
        # 记忆配置
        self.memory_level = memory_level
        self.session_id = session_id or f"session_{int(time.time())}"
        self.max_token_limit = max_token_limit
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "memory.db")
        # 知识文件路径
        self.knowledge_file = knowledge_file
        # 工具规范和用途描述
        self.specification = specification

class GenericReactAgent:
    """通用 React Agent - 领域无关"""
    
    def __init__(self, config: ReactAgentConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.llm = self._create_llm()
        self.memory = self._create_memory()
        self.prior_knowledge = self._load_prior_knowledge()
        self.specification = config.specification or self._get_default_specification()
        logger.info(f"GenericReactAgent initialized with memory level: {config.memory_level}")
        if self.prior_knowledge:
            logger.info(f"Loaded prior knowledge from: {config.knowledge_file}")
    
    def _get_default_specification(self) -> str:
        """获取默认的工具规范描述"""
        return """GenericReactAgent - 通用任务执行工具
        
用途：
- 执行各种编程和文件操作任务
- 创建、读取、修改文件和目录
- 执行系统命令
- 根据先验知识生成特定领域的代码

能力：
- 文件系统操作（创建、读取、写入文件）
- 目录管理（创建、列出目录内容）
- 命令执行（运行系统命令）
- 文件搜索（按模式搜索文件）

适用场景：
- 代码生成
- 项目初始化
- 文件批量处理
- 自动化脚本编写
"""
        
    def _create_llm(self):
        """创建语言模型"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")
        
        # 创建ChatOpenAI实例  
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,  # type: ignore
            base_url="https://api.deepseek.com/v1",
            temperature=0,
            # max_tokens=4000  # DeepSeek 使用 model_kwargs 传递
            model_kwargs={"max_tokens": 4000}
        )
        
        # 应用 DeepSeek token 计数修复（可通过环境变量禁用）
        if patch_deepseek_token_counting and not os.environ.get('DISABLE_TOKEN_PATCH'):
            try:
                llm = patch_deepseek_token_counting(llm)
                logger.info("Applied DeepSeek token counting patch")
            except Exception as e:
                logger.warning(f"Failed to apply token counting patch: {e}")
        
        return llm
    
    def _create_memory(self):
        """根据配置创建记忆系统"""
        if self.config.memory_level == MemoryLevel.NONE:
            logger.info("Memory disabled - using stateless mode")
            return None
            
        elif self.config.memory_level == MemoryLevel.SMART:
            # 在虚拟环境中使用窗口记忆避免token计数问题
            k = min(50, self.config.max_token_limit // 600)
            logger.info(f"Using smart memory (window buffer) with k={k} messages")
            return ConversationBufferWindowMemory(
                k=k,
                memory_key="chat_history",
                return_messages=True
            )
            
        elif self.config.memory_level == MemoryLevel.PRO:
            logger.info(f"Using persistent memory (SQLite) - session: {self.config.session_id}")
            # 确保数据库目录存在
            db_dir = os.path.dirname(self.config.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
                
            message_history = SQLChatMessageHistory(
                session_id=self.config.session_id,
                connection_string=f"sqlite:///{self.config.db_path}"
            )
            return ConversationBufferMemory(
                memory_key="chat_history",
                chat_memory=message_history,
                return_messages=True
            )
    
    def _load_prior_knowledge(self) -> str:
        """加载先验知识"""
        knowledge_path = Path(self.config.knowledge_file)
        if knowledge_path.exists():
            try:
                content = knowledge_path.read_text(encoding='utf-8')
                # 转义单个大括号以避免被误认为是模板变量
                # 只转义未成对的大括号
                import re
                # 先保护已经转义的大括号
                content = content.replace('{{', '\x00DOUBLE_OPEN\x00')
                content = content.replace('}}', '\x00DOUBLE_CLOSE\x00')
                # 转义单个大括号
                content = content.replace('{', '{{')
                content = content.replace('}', '}}')
                # 恢复已经转义的大括号
                content = content.replace('\x00DOUBLE_OPEN\x00', '{{')
                content = content.replace('\x00DOUBLE_CLOSE\x00', '}}')
                return content
            except Exception as e:
                logger.warning(f"Failed to load prior knowledge: {e}")
                return ""
        else:
            logger.info(f"No prior knowledge file found at: {knowledge_path}")
            return ""
    
    def create_agent_executor(self, task_description: str) -> AgentExecutor:
        """创建 Agent 执行器"""
        
        # 创建工具
        @tool("write_file", args_schema=FileInput)
        def write_file(file_path: str, content: str) -> str:
            """写入文件到指定路径"""
            try:
                file_full_path = Path(self.config.output_dir) / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                file_full_path.write_text(content, encoding='utf-8')
                return f"Successfully wrote file: {file_path}"
            except Exception as e:
                return f"Error writing file: {str(e)}"

        @tool("read_file")
        def read_file(file_path: str) -> str:
            """读取文件内容"""
            try:
                file_full_path = Path(self.config.output_dir) / file_path
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
                dir_full_path = Path(self.config.output_dir) / directory_path
                dir_full_path.mkdir(parents=True, exist_ok=True)
                return f"Successfully created directory: {directory_path}"
            except Exception as e:
                return f"Error creating directory: {str(e)}"

        @tool("list_directory", args_schema=DirectoryInput)
        def list_directory(directory_path: str = ".") -> str:
            """列出目录内容"""
            try:
                dir_full_path = Path(self.config.output_dir) / directory_path
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

        @tool("execute_command", args_schema=CommandInput)
        def execute_command(command: str, working_dir: str = ".") -> str:
            """执行系统命令"""
            try:
                import subprocess
                work_path = Path(self.config.output_dir) / working_dir
                
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(work_path),
                    timeout=60
                )
                
                output = f"Exit code: {result.returncode}\n"
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                    
                return output
                
            except subprocess.TimeoutExpired:
                return "Command timed out after 60 seconds"
            except Exception as e:
                return f"Error executing command: {str(e)}"

        @tool("search_files", args_schema=SearchInput)
        def search_files(pattern: str, directory: str = ".", file_type: Optional[str] = None) -> str:
            """在目录中搜索文件"""
            try:
                search_dir = Path(self.config.output_dir) / directory
                if not search_dir.exists():
                    return f"Directory not found: {directory}"
                
                results = []
                for file_path in search_dir.rglob("*"):
                    if file_path.is_file():
                        if file_type and not file_path.suffix == file_type:
                            continue
                        if pattern.lower() in file_path.name.lower():
                            results.append(str(file_path.relative_to(search_dir)))
                
                return "\n".join(results) if results else "No matching files found"
            except Exception as e:
                return f"Error searching files: {str(e)}"

        # 工具列表
        tools = [
            write_file,
            read_file,
            create_directory,
            list_directory,
            execute_command,
            search_files
        ]
        
        # 通用系统提示词 - 领域无关
        system_prompt = f"""你是一个通用的任务执行助手。

## 你的能力

你可以使用以下工具来完成任务：
- write_file: 创建或修改文件
- read_file: 读取文件内容
- create_directory: 创建目录结构
- list_directory: 查看目录内容
- execute_command: 执行系统命令
- search_files: 搜索文件

## 工作原则

1. 理解任务要求，制定执行计划
2. 按步骤执行，确保每步成功
3. 遇到错误时分析原因并尝试修复
4. 完成任务后验证结果

## 当前任务

{task_description}

## 输出目录

所有文件操作都相对于: {self.config.output_dir}
"""

        # 如果有先验知识，添加到提示词中
        if self.prior_knowledge:
            system_prompt += f"""
## 领域知识

以下是相关的领域知识，请在执行任务时参考：

{self.prior_knowledge}
"""

        # 创建prompt - 根据是否有记忆调整
        messages = [("system", system_prompt)]
        
        # 如果启用了记忆，添加记忆占位符
        if self.memory is not None:
            messages.append(MessagesPlaceholder(variable_name="chat_history"))  # type: ignore
            
        messages.extend([
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        prompt = ChatPromptTemplate.from_messages(messages)
        
        # 创建agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        
        # 创建executor - 根据是否有记忆配置
        executor_config = {
            "agent": agent,
            "tools": tools,
            "verbose": True,
            "max_iterations": 50,
            "handle_parsing_errors": True
        }
        
        # 如果有记忆，添加到executor
        if self.memory is not None:
            executor_config["memory"] = self.memory
            
        return AgentExecutor(**executor_config)
    
    def execute_task(self, task: str) -> None:
        """执行任务"""
        # 创建执行器
        executor = self.create_agent_executor(task)
        
        # 执行任务
        print("\n[1m> Starting task execution...[0m")
        executor.invoke({"input": task})
        print("[1m> Task completed.[0m")


def main():
    """主函数 - 支持三级记忆配置和先验知识"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Generic ReactAgent with Prior Knowledge Support")
    parser.add_argument("--memory", choices=["none", "smart", "pro"], 
                       default="smart", help="Memory level: none, smart, or pro (default: smart)")
    parser.add_argument("--session-id", type=str, 
                       default=None, help="Session ID for persistent memory")
    parser.add_argument("--max-tokens", type=int, default=30000,
                       help="Max token limit for smart memory (default: 30000)")
    parser.add_argument("--knowledge-file", type=str, 
                       default="先验知识.md", 
                       help="Path to prior knowledge file (default: 先验知识.md)")
    parser.add_argument("--output-dir", type=str, 
                       default="output/generic_agent", 
                       help="Output directory (default: output/generic_agent)")
    parser.add_argument("--task", type=str, 
                       default="创建一个简单的 Hello World 程序",
                       help="Task description (default: 创建一个简单的 Hello World 程序)")
    args = parser.parse_args()
    
    # 根据memory参数映射到MemoryLevel
    memory_mapping = {
        "none": MemoryLevel.NONE,
        "smart": MemoryLevel.SMART,
        "pro": MemoryLevel.PRO
    }
    memory_level = memory_mapping[args.memory]
    
    logger.info(f"Using Generic ReactAgent v4")
    logger.info(f"Memory level: {args.memory}")
    logger.info(f"Knowledge file: {args.knowledge_file}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # 创建输出目录
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # 创建配置
    config = ReactAgentConfig(
        output_dir=args.output_dir,
        additional_config={},
        memory_level=memory_level,
        session_id=args.session_id,
        max_token_limit=args.max_tokens,
        knowledge_file=args.knowledge_file
    )
    
    try:
        # 创建 Agent
        agent = GenericReactAgent(config)
        logger.info("Initialized Generic ReactAgent v4")
        logger.info(f"Starting task execution...")
        
        start_time = time.time()
        
        # 执行任务
        agent.execute_task(args.task)
        
        execution_time = time.time() - start_time
        
        # 统计
        print("\n" + "=" * 50)
        print("✅ Task Execution Complete!")
        print("=" * 50)
        print(f"Agent: Generic ReactAgent v4")
        print(f"Output: {args.output_dir}")
        print(f"\nMemory Configuration:")
        print(f"  - Level: {args.memory}")
        if args.memory == "smart":
            print(f"  - Token limit: {config.max_token_limit}")
        elif args.memory == "pro":
            print(f"  - Session ID: {config.session_id}")
            print(f"  - Database: {config.db_path}")
        print(f"\nExecution time: {execution_time:.2f}s")
        
        return 0
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())