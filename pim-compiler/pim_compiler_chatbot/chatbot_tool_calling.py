#!/usr/bin/env python3
"""
PIM Compiler Chatbot - Tool Calling Agent 版本
使用更现代的 Tool Calling Agent 替代 ReAct Agent
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

from pim_compiler_chatbot.chatbot import PIMCompilerTools


def create_tool_calling_pim_agent(llm_config: Optional[Dict[str, Any]] = None):
    """创建使用 Tool Calling 的 PIM 编译器智能体"""
    
    # 初始化工具，确保使用正确的路径
    pim_compiler_path = Path(__file__).parent.parent
    tools_instance = PIMCompilerTools(pim_compiler_path=str(pim_compiler_path))
    
    # 创建通用的参数清理函数
    def clean_param(param: str) -> str:
        """清理 LangChain 传递的参数"""
        if not param:
            return ""
        # 去除首尾空白和引号
        cleaned = param.strip()
        # 去除可能的引号（单引号或双引号）
        while cleaned and cleaned[0] in '"\'':
            cleaned = cleaned[1:]
        while cleaned and cleaned[-1] in '"\'':
            cleaned = cleaned[:-1]
        # 再次去除空白
        cleaned = cleaned.strip()
        return cleaned
    
    # 创建工具列表
    tools = [
        Tool(
            name="search_pim_files",
            func=lambda q: tools_instance.search_pim_files(clean_param(q)),
            description="搜索 PIM 文件。输入搜索关键词。"
        ),
        Tool(
            name="compile_pim",
            func=lambda f: tools_instance.compile_pim(clean_param(f)),
            description="编译 PIM 文件。输入文件路径。"
        ),
        Tool(
            name="check_log",
            func=lambda s: tools_instance.check_log(clean_param(s) if clean_param(s) else None),
            description="查看编译日志。可选输入系统名称。"
        ),
        Tool(
            name="list_projects",
            func=lambda _: tools_instance.list_compiled_projects(""),
            description="列出所有已编译的项目。"
        ),
        Tool(
            name="stop_compilation",
            func=lambda s: tools_instance.stop_compilation(clean_param(s) if clean_param(s) else None),
            description="终止编译进程。可选输入系统名称。"
        )
    ]
    
    # 创建提示模板 - Tool Calling Agent 使用不同的格式
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
    
    # 创建 Tool Calling Agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
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


def create_openai_functions_agent(llm_config: Optional[Dict[str, Any]] = None):
    """创建使用 OpenAI Functions 的 Agent（更适合 GPT 模型）"""
    from langchain.agents import create_openai_functions_agent
    
    # 初始化工具，确保使用正确的路径
    pim_compiler_path = Path(__file__).parent.parent
    tools_instance = PIMCompilerTools(pim_compiler_path=str(pim_compiler_path))
    
    # 创建通用的参数清理函数
    def clean_param(param: str) -> str:
        """清理 LangChain 传递的参数"""
        if not param:
            return ""
        cleaned = param.strip()
        while cleaned and cleaned[0] in '"\'':
            cleaned = cleaned[1:]
        while cleaned and cleaned[-1] in '"\'':
            cleaned = cleaned[:-1]
        cleaned = cleaned.strip()
        return cleaned
    
    # 创建工具列表 - Functions Agent 需要更详细的描述
    tools = [
        Tool(
            name="search_pim_files",
            func=lambda q: tools_instance.search_pim_files(clean_param(q)),
            description="搜索 PIM 文件。参数：query (str) - 搜索关键词，如'医院'、'hospital'、'博客'等。"
        ),
        Tool(
            name="compile_pim",
            func=lambda f: tools_instance.compile_pim(clean_param(f)),
            description="编译 PIM 文件。参数：file_path (str) - PIM文件路径，如 'examples/blog.md'。"
        ),
        Tool(
            name="check_log",
            func=lambda s: tools_instance.check_log(clean_param(s) if clean_param(s) else None),
            description="查看编译日志和进度。参数：system_name (str, optional) - 系统名称，如'blog'、'hospital'。不提供则显示所有。"
        ),
        Tool(
            name="list_projects",
            func=lambda _: tools_instance.list_compiled_projects(""),
            description="列出所有已编译的项目。无需参数。"
        ),
        Tool(
            name="stop_compilation",
            func=lambda s: tools_instance.stop_compilation(clean_param(s) if clean_param(s) else None),
            description="终止编译进程。参数：system_name (str, optional) - 要终止的系统名称。"
        )
    ]
    
    # Functions Agent 的提示更简洁
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是 PIM 编译器助手。帮助用户搜索、编译 PIM 文件，查看日志，管理项目。"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 配置 LLM
    if llm_config is None:
        llm_config = {"model": "gpt-3.5-turbo", "temperature": 0}
    
    llm = ChatOpenAI(**llm_config)
    
    # 创建 OpenAI Functions Agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=3
    )


def create_structured_chat_agent(llm_config: Optional[Dict[str, Any]] = None):
    """创建结构化聊天 Agent（支持复杂的多步骤推理）"""
    from langchain.agents import create_structured_chat_agent
    
    tools_instance = PIMCompilerTools()
    
    # 结构化 Agent 的工具定义
    tools = [
        Tool(
            name="search_pim_files",
            func=lambda q: tools_instance.search_pim_files(q.strip()),
            description=(
                "搜索 PIM 文件。\n"
                "输入格式: 搜索关键词\n"
                "输出格式: 找到的文件列表"
            )
        ),
        Tool(
            name="compile_pim",
            func=lambda f: tools_instance.compile_pim(f.strip()),
            description=(
                "编译 PIM 文件。\n"
                "输入格式: 文件路径 (如 examples/blog.md)\n"
                "输出格式: 编译状态信息"
            )
        ),
        Tool(
            name="check_log",
            func=lambda s: tools_instance.check_log(s.strip() if s and s.strip() else None),
            description=(
                "查看编译日志。\n"
                "输入格式: [可选] 系统名称\n"
                "输出格式: 日志内容和进度"
            )
        ),
        Tool(
            name="list_projects",
            func=lambda _: tools_instance.list_compiled_projects(""),
            description="列出所有已编译的项目。"
        ),
        Tool(
            name="stop_compilation",
            func=lambda s: tools_instance.stop_compilation(s.strip() if s and s.strip() else None),
            description=(
                "终止编译进程。\n"
                "输入格式: [可选] 系统名称\n"
                "输出格式: 终止结果"
            )
        )
    ]
    
    # 结构化 Chat Agent 的提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是 PIM 编译器助手。使用以下格式回答：

思考：分析用户需求
计划：列出需要执行的步骤
执行：使用工具完成任务
总结：简洁地总结结果

可用工具：{tools}
工具名称：{tool_names}"""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    if llm_config is None:
        llm_config = {"model": "gpt-3.5-turbo", "temperature": 0.3}
    
    llm = ChatOpenAI(**llm_config)
    
    agent = create_structured_chat_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )


def main():
    """主函数 - 演示不同类型的 Agent"""
    print("🤖 PIM 编译器助手 - Agent 类型选择")
    print("=" * 60)
    print("1. Tool Calling Agent (推荐)")
    print("2. OpenAI Functions Agent")
    print("3. Structured Chat Agent")
    print("4. ReAct Agent (原版)")
    
    choice = input("\n选择 Agent 类型 [1-4, 默认1]: ").strip() or "1"
    
    # 配置 LLM
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        llm_config = {
            "api_key": deepseek_key,
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "temperature": 0.3
        }
        print(f"\n✅ 使用 DeepSeek 模型")
    else:
        print("\n⚠️  未设置 DEEPSEEK_API_KEY")
        return
    
    # 创建选定的 Agent
    if choice == "1":
        print("使用 Tool Calling Agent...")
        agent = create_tool_calling_pim_agent(llm_config)
    elif choice == "2":
        print("使用 OpenAI Functions Agent...")
        agent = create_openai_functions_agent(llm_config)
    elif choice == "3":
        print("使用 Structured Chat Agent...")
        agent = create_structured_chat_agent(llm_config)
    else:
        print("使用 ReAct Agent...")
        from pim_compiler_chatbot.chatbot import create_pim_compiler_agent
        agent = create_pim_compiler_agent(llm_config)
    
    print("\n输入 'exit' 退出\n")
    
    # 交互循环
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 执行 agent
            result = agent.invoke({"input": user_input})
            print(f"\n助手: {result['output']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 出错了: {str(e)}")


if __name__ == "__main__":
    main()