#!/usr/bin/env python3
"""
PIM Compiler Chatbot - Bind Tools 版本
使用 LangChain 的 bind_tools 方法，这是最新推荐的方式
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Literal
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field

from pim_compiler_chatbot.chatbot import PIMCompilerTools


# 定义工具的参数模型
class SearchPIMFiles(BaseModel):
    """搜索 PIM 文件的参数"""
    query: str = Field(description="搜索关键词，如'博客'、'博客系统'、'医院'、'用户管理'等")


class CompilePIM(BaseModel):
    """编译 PIM 文件的参数"""
    file_path: str = Field(description="PIM文件路径，如 'examples/blog.md'")


class CheckLog(BaseModel):
    """查看编译日志的参数"""
    system_name: Optional[str] = Field(default=None, description="系统名称，如'blog'、'hospital'。留空显示所有日志")


class StopCompilation(BaseModel):
    """终止编译的参数"""
    system_name: Optional[str] = Field(default=None, description="要终止的系统名称。留空终止所有")


# 初始化工具实例，确保使用正确的路径
# 获取 pim-compiler 目录路径（chatbot.py 的父目录）
pim_compiler_path = Path(__file__).parent.parent
tools_instance = PIMCompilerTools(pim_compiler_path=str(pim_compiler_path))


# 使用 @tool 装饰器定义工具
@tool
def search_pim_files(query: str) -> str:
    """搜索 PIM（平台无关模型）文件。支持中文和英文关键词。"""
    return tools_instance.search_pim_files(query)


@tool
def compile_pim(file_path: str) -> str:
    """编译指定的 PIM 文件，生成可执行代码。"""
    return tools_instance.compile_pim(file_path)


@tool
def check_log(system_name: Optional[str] = None) -> str:
    """查看编译日志和进度。可以指定系统名称，或留空查看所有。"""
    return tools_instance.check_log(system_name)


@tool
def list_projects() -> str:
    """列出所有已编译的项目。"""
    return tools_instance.list_compiled_projects("")


@tool
def stop_compilation(system_name: Optional[str] = None) -> str:
    """终止正在运行的编译进程。"""
    return tools_instance.stop_compilation(system_name)


class PIMCompilerAgent:
    """使用 bind_tools 的 PIM 编译器智能体"""
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        # 配置 LLM
        if llm_config is None:
            llm_config = {"model": "gpt-3.5-turbo", "temperature": 0.3}
        
        # 参数名转换
        if "openai_api_key" in llm_config:
            llm_config["api_key"] = llm_config.pop("openai_api_key")
        if "openai_api_base" in llm_config:
            llm_config["base_url"] = llm_config.pop("openai_api_base")
        
        # 创建 LLM
        self.llm = ChatOpenAI(**llm_config)
        
        # 定义工具
        self.tools = [
            search_pim_files,
            compile_pim,
            check_log,
            list_projects,
            stop_compilation
        ]
        
        # 将工具绑定到 LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 系统提示
        self.system_prompt = """你是 PIM 编译器助手，专门帮助用户编译 PIM（平台无关模型）文件。

你的能力包括：
1. 搜索 PIM 文件 - 支持中文和英文关键词
2. 编译 PIM 文件 - 将模型转换为可执行代码
3. 查看编译日志 - 实时监控编译进度
4. 管理编译项目 - 列出和管理已编译的项目
5. 终止编译进程 - 停止正在运行的编译任务

工作流程：
- 当用户说"编译XX系统"时，先搜索相关文件，找到后再编译
- 编译启动后，提醒用户可以查看日志
- 用户可能使用各种表达方式，要灵活理解意图

注意：
- 总是先搜索文件，确认文件存在后再编译
- 提供清晰、友好的反馈
- 如果操作失败，解释原因并提供建议"""
        
        # 对话历史
        self.messages: List[Any] = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def _execute_tool_calls(self, tool_calls):
        """执行工具调用"""
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # 找到对应的工具
            tool_func = None
            for tool in self.tools:
                if tool.name == tool_name:
                    tool_func = tool
                    break
            
            if tool_func:
                try:
                    # 执行工具
                    result = tool_func.invoke(tool_args)
                    results.append({
                        "tool_call_id": tool_call["id"],
                        "content": result
                    })
                except Exception as e:
                    results.append({
                        "tool_call_id": tool_call["id"],
                        "content": f"工具执行错误: {str(e)}"
                    })
            else:
                results.append({
                    "tool_call_id": tool_call["id"],
                    "content": f"未找到工具: {tool_name}"
                })
        
        return results
    
    def chat(self, message: str) -> str:
        """处理用户消息"""
        # 添加用户消息
        self.messages.append({"role": "user", "content": message})
        
        # 调用 LLM
        response = self.llm_with_tools.invoke(self.messages)
        
        # 检查是否有工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # 添加助手的工具调用消息
            self.messages.append(response)
            
            # 执行工具调用
            tool_results = self._execute_tool_calls(response.tool_calls)
            
            # 添加工具结果
            for result in tool_results:
                tool_message = ToolMessage(
                    content=result["content"],
                    tool_call_id=result["tool_call_id"]
                )
                self.messages.append(tool_message)
            
            # 再次调用 LLM 生成最终响应
            final_response = self.llm_with_tools.invoke(self.messages)
            self.messages.append(final_response)
            
            return final_response.content
        else:
            # 没有工具调用，直接返回响应
            self.messages.append(response)
            return response.content
    
    def clear_history(self):
        """清除对话历史"""
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]


def main():
    """主函数"""
    print("🤖 PIM 编译器助手 - Bind Tools 版本")
    print("=" * 60)
    print("使用最新的 bind_tools API，自动处理参数解析")
    print("支持中文关键词，如：'编译博客系统'、'查看日志' 等")
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
    
    # 创建智能体
    agent = PIMCompilerAgent(llm_config)
    
    print("输入 'exit' 退出，'clear' 清除历史")
    print("=" * 60)
    
    # 启用命令历史
    try:
        import readline
        history_file = Path.home() / ".pim_compiler_history"
        if history_file.exists():
            readline.read_history_file(str(history_file))
        
        import atexit
        atexit.register(readline.write_history_file, str(history_file))
    except ImportError:
        pass
    
    # 交互循环
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 再见！")
                break
            
            if user_input.lower() == 'clear':
                agent.clear_history()
                print("✅ 对话历史已清除")
                continue
            
            if not user_input:
                continue
            
            # 获取响应
            response = agent.chat(user_input)
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