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
    agent = GenericReactAgent(config)
    agent.execute_task("创建一个用户管理系统")
    
    # 使用自定义 LLM
    config = ReactAgentConfig(
        work_dir="output",
        llm_model="gpt-4",
        llm_base_url="https://api.openai.com/v1",
        llm_api_key_env="OPENAI_API_KEY"
    )
    agent = GenericReactAgent(config)
    agent.execute_task("创建一个用户管理系统")
"""

import os
import sys
import time
import logging
import re
import warnings
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
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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
from langchain_community.chat_message_histories import (
    SQLChatMessageHistory,
)
from pydantic import BaseModel, Field

# 可选：导入特定 LLM 的 token 计数修复
try:
    from deepseek_token_counter import patch_deepseek_token_counting  # type: ignore
except ImportError:
    patch_deepseek_token_counting = None

# 设置缓存 - 使用绝对路径确保缓存生效
cache_path = os.path.join(os.path.dirname(__file__), ".langchain.db")
set_llm_cache(SQLiteCache(database_path=cache_path))

class MemoryLevel(str, Enum):
    """记忆级别枚举
    
    定义 Agent 的记忆管理策略：
    - NONE: 无状态模式，适合简单任务
    - SMART: 摘要缓冲区，自动摘要超出限制的历史对话
    - PRO: SQLite 持久化，支持长期记忆
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
        specification: Agent 规范描述
        system_prompt_file: 系统提示词文件路径
        llm_model: LLM 模型名称（默认: "deepseek-chat"）
        llm_base_url: LLM API 基础 URL（默认: "https://api.deepseek.com/v1"）
        llm_api_key_env: LLM API 密钥的环境变量名（默认: "DEEPSEEK_API_KEY"）
        llm_temperature: LLM 温度参数（默认: 0）
        context_window: 模型的上下文窗口大小（单位：tokens）。如果未指定，将根据模型名称自动推断
    """
    def __init__(self, work_dir, additional_config=None, 
                 memory_level=MemoryLevel.SMART, session_id=None, 
                 max_token_limit=30000, db_path=None,
                 knowledge_file=None, knowledge_files=None, specification=None,
                 system_prompt_file="system_prompt.md",
                 llm_model=None,
                 llm_base_url=None,
                 llm_api_key_env=None,
                 llm_temperature=0,
                 context_window=None):
        self.work_dir = work_dir
        self.additional_config = additional_config or {}
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
            # 默认使用综合知识文件
            self.knowledge_files = ["knowledge/综合知识.md"]
        
        # 系统提示词文件路径
        self.system_prompt_file = system_prompt_file
        # 工具规范和用途描述
        self.specification = specification
        
        # LLM 配置 - 如果未提供，使用 DeepSeek 默认值
        self.llm_model = llm_model or "deepseek-chat"
        self.llm_base_url = llm_base_url or "https://api.deepseek.com/v1"
        self.llm_api_key_env = llm_api_key_env or "DEEPSEEK_API_KEY"
        self.llm_temperature = llm_temperature
        
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
    
    def __init__(self, config: ReactAgentConfig):
        self.config = config
        self.work_dir = Path(config.work_dir)
        self.llm = self._create_llm()
        self.memory = self._create_memory()
        self.prior_knowledge = self._load_prior_knowledge()
        self.system_prompt_template = self._load_system_prompt()
        self.specification = config.specification or self._get_default_specification()
        
        # 初始化 agent 和 executor
        self._agent = None
        self._executor = None
        self._tools: Optional[List[Any]] = None  # 工具列表
        self._initialize_executor()
        
        # 只在调试模式下显示初始化信息
        if os.environ.get('DEBUG'):
            logger.info(f"GenericReactAgent initialized with memory level: {config.memory_level}")
            logger.info(f"LLM model: {config.llm_model}, context window: {config.context_window} tokens")
            logger.info(f"Max token limit for memory: {config.max_token_limit}")
            if self.prior_knowledge:
                logger.info(f"Loaded prior knowledge from: {config.knowledge_files}")
            if self.system_prompt_template:
                logger.info(f"Loaded system prompt from: {config.system_prompt_file}")
    
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
        llm = ChatOpenAI(
            model=self.config.llm_model,
            api_key=api_key,  # type: ignore
            base_url=self.config.llm_base_url,
            temperature=self.config.llm_temperature
        )
        
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
        return """你是一个通用的任务执行助手。

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

## 工作目录

所有文件操作都相对于: {work_dir}

## 任务执行说明

你将通过用户输入接收具体的任务。请仔细分析任务需求，选择合适的工具来完成任务。"""
    
    def _create_agent(self):
        """创建 Agent
        
        创建 LangChain Agent，包括：
        1. 创建所有工具实例
        2. 构建系统提示词（结合模板和知识）
        3. 创建 LangChain Agent
        
        Returns:
            Agent: 配置好的 Agent
        """
        
        # 从 tools 模块创建工具（已包含 apply_diff）
        tools = create_tools(self.config.work_dir)
        
        # 使用加载的系统提示词模板（不再需要 task_description）
        system_prompt = self.system_prompt_template.format(
            work_dir=self.config.work_dir
        )
        
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
        
        # 保存工具列表到实例属性，供后续使用
        self._tools = tools
        
        return agent
    
    def _initialize_executor(self):
        """初始化或更新 executor
        
        创建新的 agent 并更新 executor。
        如果是首次调用，创建新的 executor；
        如果已存在 executor，只更新其 agent 属性。
        """
        # 创建新的 agent（这会设置 self._tools）
        self._agent = self._create_agent()
        
        # 确保 tools 已经被初始化
        if self._tools is None:
            raise RuntimeError("Tools not initialized properly in _create_agent")
        
        if self._executor is None:
            # 首次创建 executor
            executor_config = {
                "agent": self._agent,
                "tools": self._tools,
                "verbose": True,
                "max_iterations": 50,
                "handle_parsing_errors": True
            }
            
            # 如果有记忆，添加到 executor
            if self.memory is not None:
                executor_config["memory"] = self.memory
                
            self._executor = AgentExecutor(**executor_config)
            
            if os.environ.get('DEBUG'):
                logger.info("Created new AgentExecutor with memory")
        else:
            # 更新已有 executor 的 agent（保留 memory）
            self._executor.agent = self._agent
            self._executor.tools = self._tools
            
            if os.environ.get('DEBUG'):
                logger.info("Updated existing AgentExecutor's agent (memory preserved)")
    
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
        
        # 重新初始化 executor（会重建 agent，但保留 memory）
        self._initialize_executor()
        
        if os.environ.get('DEBUG'):
            logger.info(f"Loaded additional knowledge: {len(knowledge_content)} characters")
    
    def execute_task(self, task: str) -> None:
        """执行任务
        
        主要执行入口，使用缓存的 executor 执行任务。
        
        Args:
            task: 要执行的任务描述
            
        Note:
            执行结果会直接打印到控制台
        """
        # 确保 executor 已初始化
        if self._executor is None:
            raise RuntimeError("Executor not initialized. This should not happen.")
            
        # 使用缓存的 executor 执行任务
        print("\n> Executing task...")
        result = self._executor.invoke({"input": task})
        
        # 打印结果
        print("> Task completed.")
        print(f"\nResult:\n{result['output']}")


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
    
    # 创建工作目录
    Path(args.work_dir).mkdir(parents=True, exist_ok=True)
    
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
