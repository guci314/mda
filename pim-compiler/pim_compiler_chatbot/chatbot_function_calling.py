#!/usr/bin/env python3
"""
PIM Compiler Chatbot - 原生 Function Calling 版本
使用 LangChain 的函数调用功能，避免手动参数清理
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from pim_compiler_chatbot.chatbot import PIMCompilerTools


# 使用 Pydantic 定义参数模型，这样 LangChain 会自动处理参数验证和清理
class SearchInput(BaseModel):
    """搜索输入参数"""
    query: str = Field(description="搜索关键词，如'博客'、'医院'、'用户'等")


class CompileInput(BaseModel):
    """编译输入参数"""
    file_path: str = Field(description="PIM文件路径，如 'examples/blog.md'")


class LogInput(BaseModel):
    """日志查看输入参数"""
    system_name: Optional[str] = Field(default=None, description="系统名称，如'blog'、'hospital'。不提供则显示所有")


class StopInput(BaseModel):
    """停止编译输入参数"""
    system_name: Optional[str] = Field(default=None, description="要终止的系统名称")


# 初始化工具实例，确保使用正确的路径
# 获取 pim-compiler 目录路径（chatbot.py 的父目录）
pim_compiler_path = Path(__file__).parent.parent
tools_instance = PIMCompilerTools(pim_compiler_path=str(pim_compiler_path))


# 使用 @tool 装饰器创建工具，自动处理参数
@tool("search_pim_files", args_schema=SearchInput)
def search_pim_files(query: str) -> str:
    """搜索 PIM 文件"""
    return tools_instance.search_pim_files(query)


@tool("compile_pim", args_schema=CompileInput)
def compile_pim(file_path: str) -> str:
    """编译 PIM 文件"""
    return tools_instance.compile_pim(file_path)


@tool("check_log", args_schema=LogInput)
def check_log(system_name: Optional[str] = None) -> str:
    """查看编译日志"""
    return tools_instance.check_log(system_name)


@tool("list_projects")
def list_projects() -> str:
    """列出所有已编译的项目"""
    return tools_instance.list_compiled_projects("")


@tool("stop_compilation", args_schema=StopInput)
def stop_compilation(system_name: Optional[str] = None) -> str:
    """终止编译进程"""
    return tools_instance.stop_compilation(system_name)


def create_function_calling_agent(llm_config: Optional[Dict[str, Any]] = None):
    """创建使用原生 Function Calling 的 Agent"""
    
    # 工具列表
    tools = [
        search_pim_files,
        compile_pim,
        check_log,
        list_projects,
        stop_compilation
    ]
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是 PIM 编译器助手，专门帮助用户编译 PIM（平台无关模型）文件。

你可以帮助用户：
1. 搜索和编译 PIM 文件
2. 查看编译进度和日志
3. 管理编译输出
4. 终止编译进程

使用工具时请注意：
- 当用户说"编译XX系统"时，先搜索相关文件，然后编译
- 用户可能使用中文或英文，要灵活理解
- 提供清晰、有帮助的响应"""),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 创建 LLM
    if llm_config is None:
        llm_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.3
        }
    
    # 确保使用正确的参数名
    if "openai_api_key" in llm_config:
        llm_config["api_key"] = llm_config.pop("openai_api_key")
    if "openai_api_base" in llm_config:
        llm_config["base_url"] = llm_config.pop("openai_api_base")
    
    llm = ChatOpenAI(**llm_config)
    
    # 创建 OpenAI Tools Agent (支持原生 function calling)
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # 创建 Agent Executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=False
    )
    
    return agent_executor


# 创建一个更简洁的对话式接口
class PIMCompilerChat:
    """PIM 编译器聊天接口"""
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        self.agent = create_function_calling_agent(llm_config)
        self.history: List[Any] = []
    
    def chat(self, message: str) -> str:
        """处理用户消息并返回响应"""
        try:
            result = self.agent.invoke({
                "input": message,
                "chat_history": self.history
            })
            
            # 更新历史
            self.history.append(HumanMessage(content=message))
            self.history.append(AIMessage(content=result["output"]))
            
            # 保持历史记录在合理长度
            if len(self.history) > 20:
                self.history = self.history[-20:]
            
            return result["output"]
        except Exception as e:
            return f"抱歉，处理您的请求时出错了: {str(e)}"


def main():
    """主函数"""
    print("🤖 PIM 编译器助手 - 原生 Function Calling 版本")
    print("=" * 60)
    print("这个版本使用原生的函数调用，无需手动参数清理")
    print()
    
    # 配置 LLM
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        llm_config = {
            "api_key": deepseek_key,
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "temperature": 0.3
        }
        print("✅ 使用 DeepSeek 模型\n")
    else:
        print("⚠️  未设置 DEEPSEEK_API_KEY\n")
        return
    
    # 创建聊天接口
    chat = PIMCompilerChat(llm_config)
    
    print("输入 'exit' 退出")
    print("=" * 60)
    
    # 启用命令历史
    try:
        import readline
        # 设置历史文件
        history_file = Path.home() / ".pim_compiler_history"
        if history_file.exists():
            readline.read_history_file(str(history_file))
        
        # 设置自动保存
        import atexit
        atexit.register(readline.write_history_file, str(history_file))
    except ImportError:
        pass  # Windows 系统可能没有 readline
    
    # 交互循环
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 获取响应
            response = chat.chat(user_input)
            print(f"\n助手: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 出错了: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()