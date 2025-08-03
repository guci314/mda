#!/usr/bin/env python3
"""通用 ReactAgent v4 - 领域无关版本，支持先验知识注入

这是一个基于 LangChain 的通用 React Agent 实现，主要特性：
1. 支持三级记忆系统（无记忆、智能缓冲、持久存储）
2. 支持先验知识注入和 include 机制
3. 领域无关的通用设计
4. 集成文件操作、命令执行等基础工具
5. 支持自定义系统提示词
6. 支持配置任何 OpenAI 兼容的 LLM（默认使用 DeepSeek）

使用示例：
    # 使用默认 DeepSeek
    config = ReactAgentConfig(
        work_dir="output",
        memory_level=MemoryLevel.SMART,
        knowledge_files=["knowledge/综合知识.md"]
    )
    agent = GenericReactAgent(config, name="my_agent")
    agent.execute_task("创建一个用户管理系统")
    
    # 使用自定义 LLM
    config = ReactAgentConfig(
        work_dir="output",
        llm_model="gpt-4",
        llm_base_url="https://api.openai.com/v1",
        llm_api_key_env="OPENAI_API_KEY"
    )
    agent = GenericReactAgent(config, name="gpt4_agent")
    agent.execute_task("创建一个用户管理系统")
"""

import os
import sys
import time
import logging
import re
import warnings
import asyncio
import threading
import atexit
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 过滤 LangChain 弃用警告 - 必须在导入之前设置
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# 设置日志 - 默认只显示警告和错误
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 禁用 httpx 的 INFO 日志
logging.getLogger("httpx").setLevel(logging.WARNING)

# 手动导入必要的内容
from dotenv import load_dotenv
load_dotenv()

# 处理代理设置问题 - 保留代理设置用于 Google 搜索
# 但某些 API 可能需要不同的处理
# os.environ.pop('http_proxy', None)
# os.environ.pop('https_proxy', None)
# os.environ.pop('all_proxy', None)

# 直接复制ReactAgentGenerator的代码，避免导入问题
from enum import Enum

# 在导入 langchain 之前再次设置警告过滤
import warnings as _warnings
_warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 使用 try-except 处理导入，避免 Pylance 错误
try:
    from langgraph.prebuilt import create_react_agent  # type: ignore
except ImportError:
    # 如果导入失败，提供一个回退方案
    raise ImportError(
        "LangGraph is required. Please install it with: pip install langgraph>=0.2.0"
    )
from langchain_core.tools import tool
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
)
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema import get_buffer_string
from langchain_core.runnables import RunnableConfig
from langchain_community.chat_message_histories import (
    SQLChatMessageHistory,
)
from pydantic import BaseModel, Field

# 可选：导入特定 LLM 的 token 计数修复
try:
    from deepseek_token_counter import patch_deepseek_token_counting  # type: ignore
except ImportError:
    patch_deepseek_token_counting = None

# 设置默认缓存 - 使用绝对路径确保缓存生效
# 可以通过环境变量 DISABLE_LANGCHAIN_CACHE=true 来禁用缓存
default_cache_path = os.path.join(os.path.dirname(__file__), ".langchain.db")
if os.environ.get('DISABLE_LANGCHAIN_CACHE', '').lower() != 'true':
    set_llm_cache(SQLiteCache(database_path=default_cache_path))
    
    # 如果启用调试模式，记录缓存路径
    if os.environ.get('DEBUG'):
        logger.info(f"LangChain SQLite cache enabled at: {default_cache_path}")
        if os.path.exists(default_cache_path):
            logger.info(f"Cache file size: {os.path.getsize(default_cache_path)} bytes")
else:
    if os.environ.get('DEBUG'):
        logger.info("LangChain cache disabled by environment variable")

class MemoryLevel(str, Enum):
    """记忆级别枚举
    
    定义 Agent 的记忆管理策略：
    - NONE: 无状态模式，适合简单任务
    - SMART: 摘要缓冲区，自动摘要超出限制的历史对话
    - PRO: SQLite 持久化，支持知识提取
    """
    NONE = "none"              # 无记忆 - 快速简单
    SMART = "summary_buffer"   # 智能摘要缓冲 - 自动摘要旧对话，保留近期原文
    PRO = "sqlite"            # 持久存储 - 专业项目

# 从 tools 模块导入工具创建函数
try:
    # 尝试相对导入（作为包的一部分运行）
    from .tools import create_tools  # type: ignore
except ImportError:
    # 尝试绝对导入（直接运行脚本）
    from tools import create_tools  # type: ignore

# 全局线程跟踪
_memory_update_threads = []
_shutdown_registered = False

def _wait_for_memory_updates():
    """等待所有记忆更新线程完成"""
    if _memory_update_threads:
        active_threads = [t for t in _memory_update_threads if t.is_alive()]
        if active_threads:
            print(f"\n等待 {len(active_threads)} 个知识提取任务完成...")
            for i, thread in enumerate(active_threads, 1):
                if thread.is_alive():
                    print(f"  [{i}/{len(active_threads)}] 等待 {thread.name}...")
                    thread.join(timeout=30)  # 最多等待30秒
                    if thread.is_alive():
                        print(f"  警告：{thread.name} 超时未完成")
                    else:
                        print(f"  [{i}/{len(active_threads)}] {thread.name} 已完成")
            print("所有记忆更新已完成。")
        _memory_update_threads.clear()

# 注册退出处理函数
def _register_shutdown_handler():
    """注册程序退出时的处理函数"""
    global _shutdown_registered
    if not _shutdown_registered:
        atexit.register(_wait_for_memory_updates)
        _shutdown_registered = True

class CustomSummaryBufferMemory(ConversationBufferMemory):
    """自定义的摘要缓冲内存实现
    
    替代已弃用的 ConversationSummaryBufferMemory，实现相似功能：
    - 保留最近的对话在缓冲区
    - 当超过 token 限制时，对旧消息进行摘要
    - 使用 LLM 生成摘要
    """
    
    llm: Any = None
    max_token_limit: int = 2000
    summary: str = ""
    
    def __init__(
        self,
        llm,
        max_token_limit: int = 2000,
        memory_key: str = "chat_history",
        return_messages: bool = True,
        **kwargs
    ):
        super().__init__(memory_key=memory_key, return_messages=return_messages, **kwargs)
        self.llm = llm
        self.max_token_limit = max_token_limit
        self.summary = ""
        
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """保存上下文并在需要时进行摘要"""
        # 先保存新的对话
        super().save_context(inputs, outputs)
        
        # 检查是否需要压缩
        self._prune_memory_if_needed()
        
    def _prune_memory_if_needed(self) -> None:
        """如果超过 token 限制，则修剪内存"""
        # 获取当前消息的 token 数
        buffer_string = get_buffer_string(
            self.chat_memory.messages,
            human_prefix="Human",
            ai_prefix="Assistant"
        )
        
        # 简单的 token 估算（大约 4 个字符 = 1 个 token）
        current_tokens = len(buffer_string) // 4
        
        if current_tokens > self.max_token_limit:
            # 需要进行摘要
            messages_to_summarize = []
            remaining_messages = []
            accumulated_tokens = 0
            
            # 从最新的消息开始累积，直到达到限制
            for message in reversed(self.chat_memory.messages):
                message_tokens = len(message.content) // 4
                if accumulated_tokens + message_tokens < self.max_token_limit * 0.8:  # 保留 80% 空间
                    remaining_messages.insert(0, message)
                    accumulated_tokens += message_tokens
                else:
                    messages_to_summarize.insert(0, message)
            
            if messages_to_summarize:
                # 生成摘要
                self._generate_summary(messages_to_summarize)
                
                # 更新消息历史
                self.chat_memory.messages = remaining_messages
    
    def _generate_summary(self, messages: List[BaseMessage]) -> None:
        """使用 LLM 生成消息摘要"""
        # 构建摘要提示
        conversation = get_buffer_string(messages, human_prefix="Human", ai_prefix="Assistant")
        
        if self.summary:
            prompt = f"""Current summary:
{self.summary}

New conversation to incorporate:
{conversation}

Please provide a concise summary that captures the key points from both the existing summary and the new conversation."""
        else:
            prompt = f"""Please summarize the following conversation concisely:

{conversation}"""
        
        # 生成摘要
        summary_message = self.llm.invoke(prompt)
        self.summary = summary_message.content
        
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """加载内存变量，包括摘要"""
        memory_vars = super().load_memory_variables(inputs)
        
        if self.summary and self.return_messages:
            # 在消息历史前添加摘要作为系统消息
            summary_message = SystemMessage(content=f"Previous conversation summary: {self.summary}")
            if self.memory_key in memory_vars and isinstance(memory_vars[self.memory_key], list):
                memory_vars[self.memory_key] = [summary_message] + memory_vars[self.memory_key]
        elif self.summary and not self.return_messages:
            # 在字符串格式中包含摘要
            if self.memory_key in memory_vars:
                memory_vars[self.memory_key] = f"Summary: {self.summary}\n\nRecent conversation:\n{memory_vars[self.memory_key]}"
        
        return memory_vars

# 默认模型的上下文窗口大小（单位：tokens）
DEFAULT_CONTEXT_WINDOWS = {
    # DeepSeek
    "deepseek-chat": 32768,
    "deepseek-coder": 16384,
    
    # Moonshot (Kimi)
    "kimi-k2-0711-preview": 131072,  # 128k
    "moonshot-v1-8k": 8192,
    "moonshot-v1-32k": 32768,
    "moonshot-v1-128k": 131072,
    
    # OpenAI
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-turbo": 128000,
    "gpt-4-turbo-preview": 128000,
    "gpt-4o": 128000,
    "gpt-3.5-turbo": 16385,
    "gpt-3.5-turbo-16k": 16385,
    
    # Claude (Anthropic)
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "claude-3-haiku-20240307": 200000,
    "claude-2.1": 200000,
    "claude-2": 100000,
    
    # Default for unknown models
    "default": 4096
}

# 默认模型的知识提取文件大小限制（单位：bytes）
DEFAULT_KNOWLEDGE_EXTRACTION_LIMITS = {
    # DeepSeek - 较小的上下文，使用较小的记忆
    "deepseek-chat": 50 * 1024,      # 50KB
    "deepseek-coder": 50 * 1024,     # 50KB
    
    # Gemini - 大上下文，可以有更大的记忆
    "gemini-2.5-flash": 200 * 1024,  # 200KB
    "gemini-1.5-pro": 150 * 1024,    # 150KB
    
    # OpenAI
    "gpt-4": 100 * 1024,             # 100KB
    "gpt-4-turbo": 150 * 1024,       # 150KB
    "gpt-3.5-turbo": 80 * 1024,      # 80KB
    
    # Claude - 大上下文
    "claude-3-opus-20240229": 150 * 1024,    # 150KB
    "claude-3-sonnet-20240229": 150 * 1024,  # 150KB
    "claude-2.1": 150 * 1024,        # 150KB
    
    # Default
    "default": 100 * 1024             # 100KB
}


class ReactAgentConfig:
    """React Agent 配置类
    
    管理 Agent 的所有配置参数，包括：
    - 工作目录和文件路径
    - 记忆系统配置
    - 知识文件配置
    - 系统提示词配置
    - LLM 配置
    
    Args:
        work_dir: 工作目录路径（Agent 的工作空间）
        additional_config: 额外的配置字典
        memory_level: 记忆级别（NONE/SMART/PRO）
        session_id: 会话ID，用于区分不同对话
        max_token_limit: 最大 token 限制（用于 SMART 模式）
        db_path: SQLite 数据库路径（用于 PRO 模式）
        knowledge_file: 单个知识文件路径（已废弃，建议使用 knowledge_files）
        knowledge_files: 知识文件路径列表
        knowledge_strings: 知识字符串列表，直接提供知识内容而非文件路径
        specification: Agent 规范描述
        system_prompt_file: 系统提示词文件路径
        llm_model: LLM 模型名称（默认: "deepseek-chat"）
        llm_base_url: LLM API 基础 URL（默认: "https://api.deepseek.com/v1"）
        llm_api_key_env: LLM API 密钥的环境变量名（默认: "DEEPSEEK_API_KEY"）
        llm_temperature: LLM 温度参数（默认: 0）
        context_window: 模型的上下文窗口大小（单位：tokens）。如果未指定，将根据模型名称自动推断
        cache_path: 自定义缓存路径（默认: None，使用全局缓存）
        enable_cache: 是否启用 LLM 缓存（默认: True）
        knowledge_extraction_limit: 知识提取文件大小限制（单位：bytes）。如果未指定，将根据模型名称自动推断
    """
    def __init__(self, work_dir, additional_config=None, 
                 memory_level=MemoryLevel.SMART, session_id=None, 
                 max_token_limit=30000, db_path=None,
                 knowledge_file=None, knowledge_files=None, knowledge_strings=None, specification=None,
                 system_prompt_file="knowledge/system_prompt.md",
                 llm_model=None,
                 llm_base_url=None,
                 llm_api_key_env=None,
                 llm_temperature=0,
                 context_window=None,
                 cache_path=None,
                 enable_cache=True,
                 knowledge_extraction_limit=None,
                 http_client=None,
                 agent_home=None,
                 enable_world_overview=True,
                 enable_perspective=False):
        self.work_dir = work_dir
        self.additional_config = additional_config or {}
        # Agent 内部存储目录（独立于工作目录）
        self.agent_home = agent_home
        # 记忆配置
        self.memory_level = memory_level
        self.session_id = session_id or f"session_{int(time.time())}"
        self.max_token_limit = max_token_limit
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "memory.db")
        
        # 知识文件路径 - 支持单个文件或多个文件
        if knowledge_files is not None:
            # 优先使用 knowledge_files（列表）
            self.knowledge_files = knowledge_files if isinstance(knowledge_files, list) else [knowledge_files]
        elif knowledge_file is not None:
            # 向后兼容：如果只提供了 knowledge_file，转换为列表
            self.knowledge_files = [knowledge_file]
        else:
            # 默认使用系统提示词作为基础知识
            self.knowledge_files = ["knowledge/system_prompt.md"]
        
        # 知识字符串 - 直接提供知识内容
        if knowledge_strings is not None:
            self.knowledge_strings = knowledge_strings if isinstance(knowledge_strings, list) else [knowledge_strings]
        else:
            self.knowledge_strings = []
        
        # 系统提示词文件路径
        self.system_prompt_file = system_prompt_file
        # 工具规范和用途描述
        self.specification = specification
        
        # LLM 配置 - 如果未提供，使用 DeepSeek 默认值
        self.llm_model = llm_model or "deepseek-chat"
        self.llm_base_url = llm_base_url or "https://api.deepseek.com/v1"
        self.llm_api_key_env = llm_api_key_env or "DEEPSEEK_API_KEY"
        self.llm_temperature = llm_temperature
        self.http_client = http_client
        
        # 设置上下文窗口大小
        if context_window is not None:
            self.context_window = context_window
        else:
            # 根据模型名称自动推断上下文窗口大小
            self.context_window = DEFAULT_CONTEXT_WINDOWS.get(
                self.llm_model, 
                DEFAULT_CONTEXT_WINDOWS["default"]
            )
        
        # 根据上下文窗口自动调整 max_token_limit（如果使用默认值）
        if max_token_limit == 30000 and self.context_window != DEFAULT_CONTEXT_WINDOWS["default"]:
            # 使用上下文窗口的 80% 作为 max_token_limit
            # 预留 20% 给系统提示词、工具输出等
            self.max_token_limit = int(self.context_window * 0.8)
            if os.environ.get('DEBUG'):
                logger.info(f"Auto-adjusted max_token_limit to {self.max_token_limit} based on context window {self.context_window}")
        
        # 缓存配置
        self.cache_path = cache_path
        self.enable_cache = enable_cache
        
        # 知识提取限制
        if knowledge_extraction_limit is not None:
            self.knowledge_extraction_limit = knowledge_extraction_limit
        else:
            # 根据模型名称自动推断知识提取文件大小限制
            self.knowledge_extraction_limit = DEFAULT_KNOWLEDGE_EXTRACTION_LIMITS.get(
                self.llm_model,
                DEFAULT_KNOWLEDGE_EXTRACTION_LIMITS["default"]
            )
        
        # 视图功能开关
        self.enable_world_overview = enable_world_overview
        self.enable_perspective = enable_perspective

class GenericReactAgent:
    """通用 React Agent - 领域无关
    
    基于 LangChain 的 React（Reasoning and Acting）Agent 实现。
    支持文件操作、命令执行、知识注入等功能。
    
    主要组件：
    - LLM: 使用配置的语言模型
    - 工具集: 文件读写、目录操作、命令执行、文件搜索
    - 记忆系统: 支持三级记忆管理
    - 知识系统: 支持多文件和 include 机制
    
    Attributes:
        config: Agent 配置对象
        work_dir: 工作目录路径
        llm: 语言模型实例
        memory: 记忆系统实例
        prior_knowledge: 加载的先验知识
        system_prompt_template: 系统提示词模板
    """
    
    def __init__(self, config: ReactAgentConfig, name: Optional[str] = None, custom_tools: Optional[List[Any]] = None):
        self.config = config
        self.work_dir = Path(config.work_dir)
        self.name = name or f"Agent-{config.llm_model}"  # Agent 名称，如果未提供则使用默认值
        
        # 验证工作目录必须存在
        if not self.work_dir.exists():
            raise ValueError(
                f"工作目录 '{self.work_dir}' 不存在。\n"
                "工作目录代表外部世界（如项目代码库），必须预先存在。\n"
                "Agent 不能创建工作目录，只能在其中操作文件。"
            )
        
        # 检查 world_overview.md（如果启用）
        self._pending_overview_task = None
        if config.enable_world_overview:
            self._check_world_overview()
        
        # 设置 Agent 内部存储目录（独立于工作目录）
        if config.agent_home:
            self.agent_home = Path(config.agent_home).expanduser()
        else:
            # 默认使用项目根目录的 .agents 目录
            self.agent_home = Path(__file__).parent / ".agents"
        
        # 创建 agent 目录
        self.agent_dir = self.agent_home / self.name
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建私有数据目录
        self.data_dir = self.agent_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建知识目录
        self.knowledge_dir = self.agent_dir / "knowledge"
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_file = self.knowledge_dir / "extracted_knowledge.md"
        
        # 注册退出处理函数（确保记忆更新完成）
        _register_shutdown_handler()
        
        # 应用缓存配置
        self._setup_cache()
        
        self.llm = self._create_llm()
        self.memory = self._create_memory()
        self.prior_knowledge = self._load_prior_knowledge()
        self.system_prompt_template = self._load_system_prompt()
        self.specification = config.specification or self._get_default_specification()
        
        # 初始化 agent 和 executor
        self._agent = None
        self._executor = None
        self._tools: Optional[List[Any]] = custom_tools  # 支持自定义工具
        self._system_prompt = None  # 系统提示词
        self._create_and_setup_agent()
        
        # 只在调试模式下显示初始化信息
        if os.environ.get('DEBUG'):
            logger.info(f"[{self.name}] initialized with memory level: {config.memory_level}")
            logger.info(f"[{self.name}] LLM model: {config.llm_model}, context window: {config.context_window} tokens")
            logger.info(f"[{self.name}] Max token limit for memory: {config.max_token_limit}")
            if self.prior_knowledge:
                logger.info(f"Loaded prior knowledge from: {config.knowledge_files}")
            if self.system_prompt_template:
                logger.info(f"Loaded system prompt from: {config.system_prompt_file}")
    
    def _setup_cache(self) -> None:
        """设置缓存配置
        
        根据配置决定是否启用缓存，以及使用哪个缓存路径。
        支持三种模式：
        1. 使用全局默认缓存（默认）
        2. 使用自定义缓存路径
        3. 禁用缓存
        """
        # 如果配置禁用缓存
        if not self.config.enable_cache:
            set_llm_cache(None)
            if os.environ.get('DEBUG'):
                logger.info("LLM cache disabled for this agent")
            return
        
        # 如果指定了自定义缓存路径
        if self.config.cache_path:
            # 确保缓存目录存在
            cache_dir = os.path.dirname(self.config.cache_path)
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
            
            # 设置自定义缓存
            set_llm_cache(SQLiteCache(database_path=self.config.cache_path))
            if os.environ.get('DEBUG'):
                logger.info(f"Using custom cache path: {self.config.cache_path}")
        else:
            # 使用默认全局缓存（已在模块级别设置）
            if os.environ.get('DEBUG'):
                logger.info(f"Using default global cache at: {default_cache_path}")
    
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
        """创建语言模型
        
        初始化语言模型，支持任何 OpenAI 兼容的 API：
        1. 从环境变量加载 API 密钥
        2. 使用配置的模型参数
        
        Returns:
            ChatOpenAI: 配置好的语言模型实例
            
        Raises:
            ValueError: 如果 API 密钥未设置
        """
        # 从配置的环境变量名获取 API 密钥
        api_key = os.getenv(self.config.llm_api_key_env)
        if not api_key:
            raise ValueError(f"{self.config.llm_api_key_env} not set")
        
        # 创建ChatOpenAI实例，支持任何兼容的API
        llm_kwargs = {
            "model": self.config.llm_model,
            "api_key": api_key,  # type: ignore
            "base_url": self.config.llm_base_url,
            "temperature": self.config.llm_temperature
        }
        
        # 如果提供了 http_client，添加到参数中
        if self.config.http_client:
            llm_kwargs["http_client"] = self.config.http_client
            
        llm = ChatOpenAI(**llm_kwargs)
        
        if os.environ.get('DEBUG'):
            logger.info(f"LLM initialized: model={self.config.llm_model}, base_url={self.config.llm_base_url}")
        
        return llm
    
    def _create_memory(self):
        """根据配置创建记忆系统
        
        基于 memory_level 创建不同类型的记忆系统：
        - NONE: 返回 None，无状态对话
        - SMART: 创建窗口缓冲记忆，保持最近 k 轮对话
        - PRO: 创建 SQLite 持久化记忆，支持跨会话
        
        Returns:
            Optional[ConversationBufferMemory]: 记忆系统实例或 None
        """
        if self.config.memory_level == MemoryLevel.NONE:
            if os.environ.get('DEBUG'):
                logger.info("Memory disabled - using stateless mode")
            return None
            
        elif self.config.memory_level == MemoryLevel.SMART:
            # 使用自定义的摘要缓冲记忆，自动管理历史对话
            # 保留最近的对话原文，对超出限制的部分进行摘要
            if os.environ.get('DEBUG'):
                logger.info(f"Using smart memory (custom summary buffer) with max_token_limit={self.config.max_token_limit}")
            
            return CustomSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=self.config.max_token_limit,
                memory_key="chat_history",
                return_messages=True
            )
            
        elif self.config.memory_level == MemoryLevel.PRO:
            if os.environ.get('DEBUG'):
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
        """加载先验知识，支持多个文件和 include 机制
        
        功能：
        1. 支持加载多个知识文件
        2. 支持 @include 语法引入其他文件
        3. 自动处理路径解析（绝对路径、相对路径）
        4. 防止循环引用
        5. 转义大括号避免模板冲突
        
        Returns:
            str: 合并后的所有知识内容
        """
        def load_file_with_includes(file_path: Path, loaded_files: Optional[set] = None) -> str:
            """递归加载文件，处理 include 语句
            
            Args:
                file_path: 要加载的文件路径
                loaded_files: 已加载文件集合，用于防止循环引用
                
            Returns:
                str: 文件内容，include 语句被替换为实际内容
            """
            if loaded_files is None:
                loaded_files = set()
            
            # 防止循环引用
            abs_path = file_path.resolve()
            if abs_path in loaded_files:
                logger.warning(f"Circular reference detected: {file_path}")
                return f"[Circular reference: {file_path}]"
            
            loaded_files.add(abs_path)
            
            if not file_path.exists():
                return f"[File not found: {file_path}]"
            
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                result_lines = []
                
                import re
                # 匹配 include 语句的模式：@include [文件名.md]
                include_pattern = re.compile(r'@include\s*\[([^\]]+\.md)\]')
                
                for line in lines:
                    matches = include_pattern.findall(line)
                    if matches:
                        # 处理 include
                        for match in matches:
                            included_path = Path(match)
                            
                            # 尝试多种路径解析方式
                            paths_to_try = []
                            
                            # 1. 如果是绝对路径，直接使用
                            if included_path.is_absolute():
                                paths_to_try.append(included_path)
                            else:
                                # 2. 相对于当前文件的目录
                                paths_to_try.append(file_path.parent / match)
                                
                                # 3. 相对于脚本目录
                                script_dir = Path(__file__).parent
                                paths_to_try.append(script_dir / match)
                                
                                # 4. 相对于当前工作目录
                                paths_to_try.append(Path.cwd() / match)
                            
                            # 尝试找到文件
                            found_path = None
                            for path in paths_to_try:
                                if path.exists():
                                    found_path = path
                                    break
                            
                            if found_path:
                                # 替换 include 语句为文件内容
                                included_content = load_file_with_includes(found_path, loaded_files)
                                # 添加标记表明这是引入的内容
                                line = line.replace(f'[{match}]', f'\n<!-- Included from {match} -->\n{included_content}\n<!-- End of {match} -->')
                            else:
                                line = line.replace(f'[{match}]', f'[File not found: {match}]')
                    
                    result_lines.append(line)
                
                return '\n'.join(result_lines)
                
            except Exception as e:
                logger.warning(f"Failed to load file {file_path}: {e}")
                return f"[Error loading file: {file_path}]"
        
        # 加载所有知识文件
        all_knowledge = []
        
        for knowledge_file in self.config.knowledge_files:
            knowledge_path = Path(knowledge_file)
            
            # 如果是相对路径，先尝试脚本目录
            if not knowledge_path.is_absolute() and not knowledge_path.exists():
                script_dir = Path(__file__).parent
                knowledge_path = script_dir / knowledge_file
            
            if knowledge_path.exists():
                try:
                    content = load_file_with_includes(knowledge_path)
                    if content:
                        # 添加文件标记
                        all_knowledge.append(f"<!-- Knowledge from {knowledge_file} -->\n{content}")
                        if os.environ.get('DEBUG'):
                            logger.info(f"Loaded knowledge from: {knowledge_file}")
                except Exception as e:
                    logger.warning(f"Failed to load knowledge from {knowledge_file}: {e}")
            else:
                if os.environ.get('DEBUG'):
                    logger.info(f"Knowledge file not found: {knowledge_file}")
        
        # 添加知识字符串
        for i, knowledge_string in enumerate(self.config.knowledge_strings):
            if knowledge_string:
                # 添加字符串标记
                all_knowledge.append(f"<!-- Knowledge from string {i+1} -->\n{knowledge_string}")
                if os.environ.get('DEBUG'):
                    logger.info(f"Loaded knowledge from string {i+1}")
        
        # 合并所有知识内容
        if all_knowledge:
            combined_content = "\n\n".join(all_knowledge)
            
            # 转义单个大括号以避免被误认为是模板变量
            # 只转义未成对的大括号
            import re
            # 先保护已经转义的大括号
            combined_content = combined_content.replace('{{', '\x00DOUBLE_OPEN\x00')
            combined_content = combined_content.replace('}}', '\x00DOUBLE_CLOSE\x00')
            # 转义单个大括号
            combined_content = combined_content.replace('{', '{{')
            combined_content = combined_content.replace('}', '}}')
            # 恢复已经转义的大括号
            combined_content = combined_content.replace('\x00DOUBLE_OPEN\x00', '{{')
            combined_content = combined_content.replace('\x00DOUBLE_CLOSE\x00', '}}')
            
            return combined_content
        else:
            return ""
    
    def _load_system_prompt(self) -> str:
        """加载系统提示词模板
        
        尝试从以下位置加载系统提示词：
        1. 指定的文件路径
        2. 脚本所在目录
        3. 如果都找不到，使用内置默认提示词
        
        Returns:
            str: 系统提示词模板内容
        """
        prompt_path = Path(self.config.system_prompt_file)
        if prompt_path.exists():
            try:
                content = prompt_path.read_text(encoding='utf-8')
                return content
            except Exception as e:
                logger.warning(f"Failed to load system prompt: {e}")
                # 返回默认的系统提示词
                return self._get_default_system_prompt()
        else:
            # 如果文件不存在，尝试从脚本所在目录查找
            script_dir = Path(__file__).parent
            prompt_path = script_dir / self.config.system_prompt_file
            if prompt_path.exists():
                try:
                    content = prompt_path.read_text(encoding='utf-8')
                    return content
                except Exception as e:
                    logger.warning(f"Failed to load system prompt from script dir: {e}")
            
            if os.environ.get('DEBUG'):
                logger.info(f"No system prompt file found, using default")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """获取默认的系统提示词"""
        return """你是一个任务执行助手，能够使用各种工具完成任务。

## 核心原则

1. **立即执行**：收到任务后直接执行，避免过度分析
2. **工具优先**：使用工具完成实际工作，而不是只描述步骤
3. **简洁沟通**：保持回复简洁，重点是执行结果

## 工作流程

1. **理解任务**（1-2句话）
2. **执行操作**（使用相关工具）
3. **报告结果**（简要说明）
4. **处理异常**（遇到错误时分析并重试）

## 问题解决策略

### 遇到困难时
- 尝试多个解决方案（2-3个）
- 如果都失败，重新审视目标
- 考虑替代方案
- 必要时寻求更多信息

## 工作空间

### 外部世界
- 工作目录：{work_dir}
- 代表需要操作的外部环境
- 只能修改内容，不能删除或清理整个目录

### 任务临时区
- 位置：.agents/data/<agent_name>/
- 用于存储任务执行的临时数据
- 每个任务开始时会被清空

## 注意事项

- 保持专注于当前任务
- 避免创建不必要的文件
- 优先修改现有文件而非创建新文件
- 确保产生实际输出"""
    
    def _create_agent(self):
        """创建 Agent
        
        创建 LangGraph React Agent，包括：
        1. 创建所有工具实例
        2. 构建系统提示词（结合模板和知识）
        3. 创建 LangGraph React Agent
        
        Returns:
            Agent: 配置好的 LangGraph Agent
        """
        
        # 使用自定义工具或创建默认工具
        if self._tools is None:
            # 没有提供自定义工具，使用默认工具集
            tools = create_tools(self.config.work_dir)
        else:
            # 使用提供的自定义工具
            tools = self._tools
        
        # 使用加载的系统提示词模板（不再需要 task_description）
        system_prompt = self.system_prompt_template.format(
            work_dir=self.config.work_dir
        )
        
        # 注入数据目录信息
        data_dir_info = f"""
## 工作区域
- 共享工作区：{self.config.work_dir}
- 你的私有数据区：{self.data_dir}
"""
        system_prompt += data_dir_info
        
        # 注入提取的知识
        knowledge_file = self.knowledge_dir / "extracted_knowledge.md"
        if knowledge_file.exists():
            try:
                knowledge_content = knowledge_file.read_text(encoding='utf-8')
                if knowledge_content.strip():
                    system_prompt += f"""
## 提取的知识

以下是你之前积累的经验和知识，请在执行任务时参考：

{knowledge_content}
"""
            except Exception as e:
                print(f"读取提取的知识失败: {e}")
        
        # 如果有先验知识，添加到提示词中
        if self.prior_knowledge:
            system_prompt += f"""
## 领域知识

以下是相关的领域知识，请在执行任务时参考：

{self.prior_knowledge}
"""

        # LangGraph 使用不同的方式处理系统提示词
        # 我们将在执行时将系统提示词作为第一条消息注入
        self._system_prompt = system_prompt
        
        # 创建agent - 使用 LangGraph 的 create_react_agent
        # LangGraph 的 create_react_agent 支持 prompt 参数
        # 可以传入字符串或 SystemMessage，它会被添加到消息列表的开头
        agent = create_react_agent(
            model=self.llm,
            tools=tools,
            prompt=system_prompt if self.prior_knowledge else None,  # 如果有知识，使用自定义提示词
            checkpointer=None  # 暂时不使用 checkpointer
        )
        
        # 保存工具列表到实例属性，供后续使用
        self._tools = tools
        
        return agent
    
    def _create_and_setup_agent(self):
        """创建并设置 agent
        
        在 LangGraph 中，agent 本身就是 executor，不需要额外包装。
        """
        # 创建 agent
        self._agent = self._create_agent()
        
        # 确保工具已初始化
        if self._tools is None:
            raise RuntimeError("Tools not initialized properly in _create_agent")
        
        # 在 LangGraph 中，agent 就是 executor
        self._executor = self._agent
        
        if os.environ.get('DEBUG'):
            logger.info("Created new LangGraph React Agent")
    
    def load_knowledge(self, knowledge_content: str) -> None:
        """动态加载知识内容
        
        将新的知识内容添加到现有的先验知识中。
        加载后会重建 agent 以使新知识生效，但会保留 memory。
        
        Args:
            knowledge_content: 要加载的知识文本
            
        Example:
            agent.load_knowledge("Python 最佳实践：使用虚拟环境管理依赖")
        """
        if self.prior_knowledge:
            # 如果已有知识，追加新内容
            self.prior_knowledge += f"\n\n<!-- 动态加载的知识 -->\n{knowledge_content}"
        else:
            # 如果没有知识，直接设置
            self.prior_knowledge = knowledge_content
        
        # 重新创建 agent（会使用新的知识，但保留 memory）
        self._create_and_setup_agent()
        
        if os.environ.get('DEBUG'):
            logger.info(f"Loaded additional knowledge: {len(knowledge_content)} characters")
    
    def _update_extracted_knowledge_sync(self, messages: List[BaseMessage]) -> None:
        """同步方法：更新提取的知识（在后台线程中运行）"""
        try:
            # 读取现有知识
            existing_knowledge = ""
            if self.knowledge_file.exists():
                existing_knowledge = self.knowledge_file.read_text(encoding='utf-8')
            
            # 构建任务历史
            task_history = self._format_messages_for_memory(messages)
            
            # 构建更新知识的提示词
            knowledge_prompt = self._build_knowledge_extraction_prompt(existing_knowledge, task_history)
            
            # 调用 LLM 提取知识
            extracted_knowledge = self.llm.invoke(knowledge_prompt).content
            
            # 检查知识文件大小
            knowledge_size = len(extracted_knowledge.encode('utf-8'))
            if knowledge_size > self.config.knowledge_extraction_limit:
                # 如果超过限制，要求 LLM 进一步压缩
                compress_prompt = self._build_knowledge_compression_prompt(
                    extracted_knowledge, 
                    knowledge_size, 
                    self.config.knowledge_extraction_limit
                )
                extracted_knowledge = self.llm.invoke(compress_prompt).content
            
            # 保存提取的知识
            self.knowledge_file.write_text(extracted_knowledge, encoding='utf-8')
            
            if os.environ.get('DEBUG'):
                logger.info(f"[{self.name}] Knowledge extracted successfully")
                
        except Exception as e:
            # 知识提取失败不应影响主任务
            if os.environ.get('DEBUG'):
                logger.error(f"[{self.name}] Failed to extract knowledge: {e}")
    
    def _format_messages_for_memory(self, messages: List[BaseMessage]) -> str:
        """格式化消息列表为知识提取所需的格式"""
        formatted = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                continue  # 跳过系统消息
            elif isinstance(msg, HumanMessage):
                formatted.append(f"用户: {msg.content}")
            elif hasattr(msg, 'name') and msg.name:  # 工具消息
                formatted.append(f"工具 {msg.name}: {msg.content[:500]}...")  # 限制工具输出长度
            else:  # AI 消息
                formatted.append(f"AI: {msg.content}")
        return "\n".join(formatted)
    
    def _build_knowledge_extraction_prompt(self, existing_knowledge: str, task_history: str) -> str:
        """构建知识提取的提示词"""
        knowledge_limit_kb = self.config.knowledge_extraction_limit // 1024
        
        prompt = f"""# 长期记忆更新任务

## 你的角色
你是一个知识管理助手，负责从 agent 的任务执行中提取有价值的知识和经验。

## 输入
1. **已有知识**：
{existing_knowledge if existing_knowledge else "（空）"}

2. **本次任务执行历史**：
{task_history}

## 任务
基于本次任务的执行历史，更新长期记忆。你需要：

1. **提取关键经验**：
   - 遇到的问题和解决方案
   - 发现的有效模式和方法
   - 需要记住的特殊情况
   - 用户的偏好和项目特点

2. **整合新旧记忆**：
   - 保留仍然有效的旧经验
   - 更新已过时的信息
   - 合并相似的经验
   - 删除不再重要的细节

3. **保持精炼**：
   - 使用简洁的要点形式
   - 优先保留最有价值的信息
   - 注意输出大小限制：约 {knowledge_limit_kb}KB

## 输出格式
请直接输出提取的知识内容（Markdown 格式），不要有任何解释或元信息。"""
        
        return prompt
    
    def _build_knowledge_compression_prompt(self, knowledge_content: str, 
                                        current_size: int, 
                                        limit: int) -> str:
        """构建知识压缩的提示词（知识精炼系统）"""
        current_kb = current_size / 1024
        limit_kb = limit / 1024
        target_kb = limit_kb * 0.85  # 目标大小为限制的85%，留出余量
        
        prompt = f"""# 知识压缩任务（知识精炼系统）

## 当前状况
- 知识文件大小：{current_kb:.1f}KB ({current_size} 字节)
- 大小限制：{limit_kb:.1f}KB ({limit} 字节)
- 目标大小：{target_kb:.1f}KB 以内

## 知识内容
{knowledge_content}

## 压缩策略

请使用以下精炼策略来压缩知识：

### 1. 时间衰减原则
- 保留最近的经验和教训
- 删除过于久远或已被更新的信息
- 合并重复出现的模式

### 2. 重要性评估
保留以下类型的信息（优先级从高到低）：
- **关键错误和解决方案**：避免重复犯错
- **用户偏好和项目特点**：个性化服务
- **有效的工作模式**：提高效率
- **特殊案例处理**：边界情况
- **常用技术栈信息**：技术偏好

删除以下类型的信息：
- 具体的文件内容和代码细节
- 一次性的临时解决方案
- 已经过时的技术信息
- 冗长的执行过程描述
- 重复的成功经验

### 3. 抽象化原则
- 将具体案例抽象为通用模式
- 合并相似经验为一般性原则
- 保留模式而非实例

### 4. 结构化组织
使用清晰的标题结构，如：
- ## 核心经验
- ## 常见问题与解决方案
- ## 用户偏好
- ## 技术栈特点

## 输出要求
1. 输出压缩后的知识内容
2. 使用Markdown格式
3. 确保大小不超过 {target_kb:.1f}KB
4. 保持内容的连贯性和可读性
5. 不要包含任何解释或元信息

请直接输出压缩后的记忆内容："""
        
        return prompt
    
    def _clean_data_directory(self) -> None:
        """清理工作目录和私有数据区域，为新任务准备干净环境
        
        清理策略：
        - TODO文件：归档到 archive 目录（保留任务计划历史）
        - BPMN文件：归档到 archive 目录（保留流程执行历史）
        - 其他文件：删除
        """
        import shutil
        from datetime import datetime
        
        # 清理私有数据目录
        if self.data_dir.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 创建归档目录
            archive_dir = self.data_dir / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            # 归档工作流相关文件（TODO和BPMN）
            for item in self.data_dir.iterdir():
                # 跳过 archive 目录本身
                if item.is_dir() and item.name == "archive":
                    continue
                    
                if item.is_file():
                    # 归档TODO文件
                    if item.name.upper() == 'TODO.MD' or item.name.upper().startswith('TODO'):
                        archive_name = f"{timestamp}_{item.name}"
                        archive_path = archive_dir / archive_name
                        try:
                            item.rename(archive_path)
                            if os.environ.get('DEBUG'):
                                logger.info(f"[{self.name}] Archived TODO file: {item.name} -> archive/{archive_name}")
                        except Exception as e:
                            logger.warning(f"[{self.name}] Failed to archive {item}: {e}")
                    
                    # 归档BPMN文件
                    elif item.name.endswith('.bpmn'):
                        archive_name = f"{timestamp}_{item.name}"
                        archive_path = archive_dir / archive_name
                        try:
                            item.rename(archive_path)
                            if os.environ.get('DEBUG'):
                                logger.info(f"[{self.name}] Archived BPMN file: {item.name} -> archive/{archive_name}")
                        except Exception as e:
                            logger.warning(f"[{self.name}] Failed to archive {item}: {e}")
                    
                    # 删除其他文件
                    else:
                        try:
                            item.unlink()
                            if os.environ.get('DEBUG'):
                                logger.info(f"[{self.name}] Removed file from data directory: {item}")
                        except Exception as e:
                            logger.warning(f"[{self.name}] Failed to remove {item}: {e}")
                
                # 删除非归档目录
                elif item.is_dir():
                    try:
                        shutil.rmtree(item)
                        if os.environ.get('DEBUG'):
                            logger.info(f"[{self.name}] Removed directory from data directory: {item}")
                    except Exception as e:
                        logger.warning(f"[{self.name}] Failed to remove {item}: {e}")
        
        # 注释掉清理共享工作目录的代码，以支持多 Agent 文件共享
        # 在多 Agent 协作场景下，不应该清理共享工作目录
        # 每个 Agent 应该只管理自己的私有数据目录 (.agent_data/{agent_name})
        
        # # 清理共享工作目录中的文件，但保留隐藏目录（.agent_data, .agent_memory）
        # if self.work_dir.exists():
        #     for item in self.work_dir.iterdir():
        #         # 跳过隐藏目录（.agent_data, .agent_memory）
        #         if item.name.startswith('.'):
        #             continue
        #             
        #         # 删除文件
        #         if item.is_file():
        #             try:
        #                 item.unlink()
        #                 if os.environ.get('DEBUG'):
        #                     logger.info(f"[{self.name}] Removed file: {item}")
        #             except Exception as e:
        #                 logger.warning(f"[{self.name}] Failed to remove {item}: {e}")
        #         
        #         # 删除非隐藏目录
        #         elif item.is_dir():
        #             try:
        #                 shutil.rmtree(item)
        #                 if os.environ.get('DEBUG'):
        #                     logger.info(f"[{self.name}] Removed directory: {item}")
        #             except Exception as e:
        #                 logger.warning(f"[{self.name}] Failed to remove {item}: {e}")
    
    def _check_world_overview(self) -> None:
        """检查并生成 world_overview.md"""
        from world_overview_checker import WorldOverviewChecker
        
        checker = WorldOverviewChecker(self.work_dir)
        if checker.check_and_generate(self.name):
            # 保存生成任务，将在第一次执行任务时处理
            self._pending_overview_task = checker._create_generation_task()
    
    def execute_task(self, task: str) -> str:
        """执行任务
        
        主要执行入口，使用缓存的 executor 执行任务。
        
        Args:
            task: 要执行的任务描述
            
        Returns:
            str: 最后一条AI消息内容
        """
        # 确保 executor 已初始化
        if self._executor is None:
            raise RuntimeError("Executor not initialized. This should not happen.")
        
        # 清理数据目录（保留提取的知识）
        self._clean_data_directory()
        
        # 如果有待处理的 world_overview 生成任务，优先执行
        if self._pending_overview_task:
            print(f"\n[{self.name}] > Generating world_overview.md first...")
            self._execute_internal_task(self._pending_overview_task)  # 忽略返回值
            self._pending_overview_task = None
            print(f"\n[{self.name}] > Now executing main task...")
        
        # 执行主任务
        return self._execute_internal_task(task)
    
    def _execute_internal_task(self, task: str) -> str:
        """执行内部任务的通用方法
        
        Returns:
            str: 最后一条AI消息内容
        """
        # 使用 LangGraph agent 执行任务
        if task != self._pending_overview_task:  # 避免重复打印
            print(f"\n[{self.name}] > Executing task...")
        
        # 准备输入消息
        messages = []
        
        # 添加系统提示词作为第一条消息
        if hasattr(self, '_system_prompt') and self._system_prompt:
            messages.append(SystemMessage(content=self._system_prompt))
        
        # 如果有记忆，加载历史消息
        if self.memory is not None:
            memory_vars = self.memory.load_memory_variables({})
            if "chat_history" in memory_vars:
                # 添加历史消息（但不包括之前的系统消息）
                for msg in memory_vars["chat_history"]:
                    if not isinstance(msg, SystemMessage):
                        messages.append(msg)
        
        # 添加当前任务
        messages.append(HumanMessage(content=task))
        
        inputs = {"messages": messages}
        
        # 执行任务，设置更高的递归限制和配置
        invoke_config = RunnableConfig(
            recursion_limit=100,  # 增加递归限制
            max_concurrency=5,    # 限制并发
            configurable={}
        )
        
        # 使用 stream 方法显示详细的执行过程
        try:
            # 收集所有消息用于最终输出
            all_messages = []
            
            # 使用 stream 方法获取中间步骤
            for event in self._executor.stream(inputs, config=invoke_config, stream_mode="values"):
                messages = event.get("messages", [])
                if messages:
                    # 获取最后一条消息
                    last_message = messages[-1]
                    all_messages = messages
                    
                    # 显示不同类型的消息
                    if hasattr(last_message, 'content'):
                        if isinstance(last_message, HumanMessage):
                            print(f"\n\U0001f464 用户: {last_message.content}")
                        elif isinstance(last_message, SystemMessage):
                            if os.environ.get('DEBUG'):
                                print(f"\n\U0001f4bb 系统: {last_message.content[:100]}...")
                        elif hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                            # AI 决定调用工具
                            print(f"\n\U0001f914 [{self.name}] AI 思考: 需要使用工具来完成任务")
                            for tool_call in last_message.tool_calls:
                                print(f"\U0001f527 调用工具: {tool_call.get('name', 'unknown')}")
                                if 'args' in tool_call:
                                    print(f"   参数: {tool_call['args']}")
                        elif hasattr(last_message, 'name'):
                            # 工具返回结果
                            print(f"\n\U0001f4ac 工具结果 ({last_message.name}):")
                            content = last_message.content
                            # 限制输出长度
                            if len(content) > 500:
                                print(f"   {content[:500]}...")
                                print(f"   [省略 {len(content)-500} 字符]")
                            else:
                                print(f"   {content}")
                        else:
                            # AI 的最终回答
                            if last_message.content:
                                print(f"\n\U0001f916 [{self.name}] AI 回答: {last_message.content}")
            
            # 构建结果
            result = {"messages": all_messages}
            
        except Exception as e:
            # 如果出错，尝试简化输入
            if "recursion" in str(e).lower():
                print("提示：任务可能过于复杂，尝试简化...")
                # 只保留用户消息，去掉系统提示词
                simple_inputs = {"messages": [HumanMessage(content=task)]}
                result = self._executor.invoke(simple_inputs, config=invoke_config)
            else:
                raise
        
        # 获取最终输出
        if "messages" in result:
            # 获取最后一条 AI 消息作为输出
            output_message = result["messages"][-1]
            output = output_message.content if hasattr(output_message, 'content') else str(output_message)
            
            # 如果有记忆，保存对话
            if self.memory is not None:
                self.memory.save_context({"input": task}, {"output": output})
        else:
            output = str(result)
        
        # 打印最终结果
        print(f"\n[{self.name}] > Task completed.")
        print(f"\n=== [{self.name}] 最终结果 ===\n")
        print(output)
        
        # 异步更新提取的知识
        if "messages" in result and self.config.knowledge_extraction_limit > 0:
            # 启动后台线程提取知识（非守护线程）
            knowledge_thread = threading.Thread(
                target=self._update_extracted_knowledge_sync,
                args=(result["messages"],),
                daemon=False,  # 非守护线程，确保完成
                name=f"knowledge_extraction_{self.name}"
            )
            knowledge_thread.start()
            
            # 添加到全局跟踪列表
            global _memory_update_threads
            _memory_update_threads.append(knowledge_thread)
        
        # 返回最后一条AI消息内容
        return output


def main():
    """主函数 - 命令行入口
    
    支持的命令行参数：
    --memory: 记忆级别 (none/smart/pro)
    --session-id: 会话ID（用于持久化记忆）
    --max-tokens: 最大 token 限制
    --knowledge-file: 知识文件路径
    --work-dir: 工作目录
    --task: 要执行的任务
    --llm-model: LLM 模型名称
    --llm-base-url: LLM API 基础 URL
    --llm-api-key-env: LLM API 密钥环境变量名
    --llm-temperature: LLM 温度参数
    
    示例：
        # 使用默认 DeepSeek
        python react_agent.py --task "创建一个博客系统"
        
        # 使用 OpenAI
        python react_agent.py --llm-model gpt-4-turbo-preview --llm-base-url https://api.openai.com/v1 --llm-api-key-env OPENAI_API_KEY --task "创建一个博客系统"
    """
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
    parser.add_argument("--work-dir", type=str, 
                       default="output/generic_agent", 
                       help="Working directory (default: output/generic_agent)")
    parser.add_argument("--task", type=str, 
                       default="创建一个简单的 Hello World 程序",
                       help="Task description (default: 创建一个简单的 Hello World 程序)")
    # LLM 配置参数
    parser.add_argument("--llm-model", type=str, 
                       default="deepseek-chat",
                       help="LLM model name (default: deepseek-chat)")
    parser.add_argument("--llm-base-url", type=str, 
                       default="https://api.deepseek.com/v1",
                       help="LLM API base URL (default: https://api.deepseek.com/v1)")
    parser.add_argument("--llm-api-key-env", type=str, 
                       default="DEEPSEEK_API_KEY",
                       help="Environment variable name for LLM API key (default: DEEPSEEK_API_KEY)")
    parser.add_argument("--llm-temperature", type=float, 
                       default=0,
                       help="LLM temperature (default: 0)")
    parser.add_argument("--context-window", type=int,
                       default=None,
                       help="Context window size in tokens (default: auto-detect based on model)")
    args = parser.parse_args()
    
    # 根据memory参数映射到MemoryLevel
    memory_mapping = {
        "none": MemoryLevel.NONE,
        "smart": MemoryLevel.SMART,
        "pro": MemoryLevel.PRO
    }
    memory_level = memory_mapping[args.memory]
    
    if os.environ.get('DEBUG'):
        logger.info(f"Using Generic ReactAgent v4")
        logger.info(f"Memory level: {args.memory}")
        logger.info(f"Knowledge file: {args.knowledge_file}")
        logger.info(f"Working directory: {args.work_dir}")
        logger.info(f"LLM model: {args.llm_model}")
        logger.info(f"LLM base URL: {args.llm_base_url}")
        logger.info(f"LLM API key env: {args.llm_api_key_env}")
    
    # 不创建工作目录 - 工作目录是外部世界，应该已经存在
    # 如果工作目录不存在，应该报错而不是创建
    if not Path(args.work_dir).exists():
        print(f"错误：工作目录 '{args.work_dir}' 不存在")
        print("工作目录代表外部世界（如项目代码库），必须预先存在")
        sys.exit(1)
    
    # 创建配置
    config = ReactAgentConfig(
        work_dir=args.work_dir,
        additional_config={},
        memory_level=memory_level,
        session_id=args.session_id,
        max_token_limit=args.max_tokens,
        knowledge_file=args.knowledge_file,
        llm_model=args.llm_model,
        llm_base_url=args.llm_base_url,
        llm_api_key_env=args.llm_api_key_env,
        llm_temperature=args.llm_temperature,
        context_window=args.context_window
    )
    
    try:
        # 创建 Agent
        agent = GenericReactAgent(config)
        if os.environ.get('DEBUG'):
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
        print(f"Work Directory: {args.work_dir}")
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
