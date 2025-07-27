#!/usr/bin/env python3
"""ReactAgent with Memory - 带记忆功能的ReactAgent"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory,
    CombinedMemory,
    ConversationSummaryBufferMemory
)
from langchain.memory.chat_message_histories import (
    SQLChatMessageHistory,
    FileChatMessageHistory
)
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from pydantic import BaseModel, Field

# 设置缓存
set_llm_cache(SQLiteCache(database_path=".langchain_cache.db"))


class ReactAgentWithMemory:
    """带记忆功能的ReactAgent"""
    
    def __init__(self, config: Dict[str, Any], session_id: str = None):
        self.config = config
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.llm = self._create_llm()
        self.memory = self._create_memory()
        
    def _create_llm(self):
        """创建LLM实例"""
        return ChatOpenAI(
            model="deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
            temperature=0,
            max_tokens=4000
        )
    
    def _create_memory(self):
        """创建记忆系统"""
        # 选择记忆类型
        memory_type = self.config.get("memory_type", "buffer_window")
        
        if memory_type == "buffer":
            # 1. 简单缓冲记忆 - 保存所有对话
            return ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
        elif memory_type == "summary":
            # 2. 摘要记忆 - 保存对话摘要
            return ConversationSummaryMemory(
                llm=self.llm,
                memory_key="chat_history",
                return_messages=True
            )
            
        elif memory_type == "buffer_window":
            # 3. 窗口缓冲记忆 - 只保存最近K轮对话
            return ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=10  # 保存最近10轮对话
            )
            
        elif memory_type == "summary_buffer":
            # 4. 摘要缓冲记忆 - 结合摘要和缓冲
            return ConversationSummaryBufferMemory(
                llm=self.llm,
                memory_key="chat_history",
                return_messages=True,
                max_token_limit=2000
            )
            
        elif memory_type == "persistent":
            # 5. 持久化记忆 - 保存到文件或数据库
            message_history = FileChatMessageHistory(
                file_path=f"./memory/chat_history_{self.session_id}.json"
            )
            return ConversationBufferMemory(
                memory_key="chat_history",
                chat_memory=message_history,
                return_messages=True
            )
            
        elif memory_type == "sqlite":
            # 6. SQLite数据库记忆
            message_history = SQLChatMessageHistory(
                session_id=self.session_id,
                connection_string="sqlite:///memory.db"
            )
            return ConversationBufferMemory(
                memory_key="chat_history",
                chat_memory=message_history,
                return_messages=True
            )
    
    def _create_tools_with_context(self, output_dir: str):
        """创建带上下文的工具"""
        
        # 记录已生成文件的上下文
        generated_files = []
        
        @tool("write_file")
        def write_file(file_path: str, content: str) -> str:
            """写入文件并记录到上下文"""
            try:
                full_path = Path(output_dir) / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                
                # 记录到上下文
                generated_files.append(file_path)
                
                # 保存到记忆
                self.memory.chat_memory.add_ai_message(
                    f"Created file: {file_path}"
                )
                
                return f"Successfully wrote file: {file_path}"
            except Exception as e:
                return f"Error writing file: {str(e)}"
        
        @tool("recall_context")
        def recall_context() -> str:
            """回忆之前的操作和上下文"""
            context = {
                "generated_files": generated_files,
                "session_id": self.session_id,
                "memory_summary": self.memory.chat_memory.messages[-5:] if hasattr(self.memory, 'chat_memory') else []
            }
            return f"Current context: {json.dumps(context, indent=2, default=str)}"
        
        @tool("save_checkpoint")
        def save_checkpoint(name: str, description: str) -> str:
            """保存检查点以便后续恢复"""
            checkpoint = {
                "name": name,
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "generated_files": generated_files,
                "session_id": self.session_id
            }
            
            checkpoint_dir = Path("./memory/checkpoints")
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            checkpoint_file = checkpoint_dir / f"{self.session_id}_{name}.json"
            checkpoint_file.write_text(json.dumps(checkpoint, indent=2))
            
            return f"Checkpoint saved: {name}"
        
        # 其他必要的工具...
        return [write_file, recall_context, save_checkpoint]
    
    def create_agent_with_memory(self, output_dir: str):
        """创建带记忆的Agent"""
        tools = self._create_tools_with_context(output_dir)
        
        # 创建带记忆占位符的提示词
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的代码生成助手。
            
你可以记住之前的对话和操作，使用 recall_context 工具查看上下文。

重要：
- 你可以引用之前生成的文件
- 你可以基于之前的对话继续工作
- 使用 save_checkpoint 保存重要进度
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # 创建agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        
        # 创建带记忆的executor
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return executor
    
    def generate(self, prompt: str, output_dir: str):
        """执行生成任务"""
        agent = self.create_agent_with_memory(output_dir)
        result = agent.invoke({"input": prompt})
        
        # 保存会话历史
        self._save_session()
        
        return result
    
    def _save_session(self):
        """保存会话信息"""
        session_info = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "memory_type": self.config.get("memory_type", "buffer_window"),
            "messages_count": len(self.memory.chat_memory.messages) if hasattr(self.memory, 'chat_memory') else 0
        }
        
        session_file = Path(f"./memory/sessions/{self.session_id}_info.json")
        session_file.parent.mkdir(parents=True, exist_ok=True)
        session_file.write_text(json.dumps(session_info, indent=2))
    
    def continue_session(self, session_id: str):
        """继续之前的会话"""
        self.session_id = session_id
        # 重新加载记忆
        if self.config.get("memory_type") == "sqlite":
            message_history = SQLChatMessageHistory(
                session_id=session_id,
                connection_string="sqlite:///memory.db"
            )
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                chat_memory=message_history,
                return_messages=True
            )
        print(f"Continuing session: {session_id}")


# 使用示例
if __name__ == "__main__":
    # 1. 创建新会话
    agent = ReactAgentWithMemory(
        config={"memory_type": "sqlite"},  # 使用SQLite持久化
        session_id="project_user_management"
    )
    
    # 2. 第一次生成
    result1 = agent.generate(
        "创建用户管理系统的基础模型",
        "./output/with_memory"
    )
    
    # 3. 基于记忆继续生成
    result2 = agent.generate(
        "基于之前创建的模型，添加认证功能",
        "./output/with_memory"
    )
    
    # 4. 恢复之前的会话
    agent2 = ReactAgentWithMemory(
        config={"memory_type": "sqlite"}
    )
    agent2.continue_session("project_user_management")
    
    result3 = agent2.generate(
        "检查之前生成的所有文件，并创建测试",
        "./output/with_memory"
    )