#!/usr/bin/env python3
"""
PIM Compiler Chatbot - LangGraph 版本
使用 LangGraph 实现更复杂的工作流和状态管理
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.tools import Tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.graph.message import add_messages

from pim_compiler_chatbot.chatbot import PIMCompilerTools


# 定义状态
class AgentState(TypedDict):
    """Agent 的状态定义"""
    messages: Annotated[List[BaseMessage], add_messages]
    current_task: str
    compilation_status: Dict[str, Any]
    error_count: int


class PIMCompilerGraph:
    """基于 LangGraph 的 PIM 编译器助手"""
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        self.tools_instance = PIMCompilerTools()
        self.setup_tools()
        self.setup_llm(llm_config)
        self.build_graph()
    
    def setup_tools(self):
        """设置工具"""
        self.tools = [
            Tool(
                name="search_pim_files",
                func=lambda q: self.tools_instance.search_pim_files(q.strip()),
                description="搜索 PIM 文件"
            ),
            Tool(
                name="compile_pim",
                func=lambda f: self.tools_instance.compile_pim(f.strip()),
                description="编译 PIM 文件"
            ),
            Tool(
                name="check_log",
                func=lambda s: self.tools_instance.check_log(s.strip() if s and s.strip() else None),
                description="查看编译日志"
            ),
            Tool(
                name="list_projects",
                func=lambda _: self.tools_instance.list_compiled_projects(""),
                description="列出项目"
            ),
            Tool(
                name="stop_compilation",
                func=lambda s: self.tools_instance.stop_compilation(s.strip() if s and s.strip() else None),
                description="终止编译"
            )
        ]
        
        self.tool_executor = ToolExecutor(self.tools)
        self.tools_by_name = {tool.name: tool for tool in self.tools}
    
    def setup_llm(self, llm_config: Optional[Dict[str, Any]]):
        """设置 LLM"""
        if llm_config is None:
            llm_config = {"model": "gpt-3.5-turbo", "temperature": 0.3}
        
        # 参数名转换
        if "openai_api_key" in llm_config:
            llm_config["api_key"] = llm_config.pop("openai_api_key")
        if "openai_api_base" in llm_config:
            llm_config["base_url"] = llm_config.pop("openai_api_base")
        
        self.llm = ChatOpenAI(**llm_config)
    
    def build_graph(self):
        """构建 LangGraph 工作流"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("analyze", self.analyze_request)
        workflow.add_node("plan", self.plan_actions)
        workflow.add_node("execute", self.execute_tools)
        workflow.add_node("check_result", self.check_result)
        workflow.add_node("respond", self.generate_response)
        
        # 设置入口
        workflow.set_entry_point("analyze")
        
        # 添加边
        workflow.add_edge("analyze", "plan")
        workflow.add_conditional_edges(
            "plan",
            self.should_execute,
            {
                "execute": "execute",
                "respond": "respond"
            }
        )
        workflow.add_edge("execute", "check_result")
        workflow.add_conditional_edges(
            "check_result",
            self.should_continue,
            {
                "plan": "plan",
                "respond": "respond"
            }
        )
        workflow.add_edge("respond", END)
        
        # 编译图
        self.app = workflow.compile()
    
    def analyze_request(self, state: AgentState) -> AgentState:
        """分析用户请求"""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        # 使用 LLM 分析意图
        analysis_prompt = f"""分析用户请求并识别任务类型：

用户请求：{last_message}

任务类型包括：
1. search - 搜索文件
2. compile - 编译系统
3. check_log - 查看日志
4. list - 列出项目
5. stop - 终止编译
6. complex - 需要多步骤

返回格式：任务类型|关键信息
例如：compile|博客系统"""
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        task_info = response.content.strip()
        
        state["current_task"] = task_info
        return state
    
    def plan_actions(self, state: AgentState) -> AgentState:
        """计划要执行的动作"""
        task_info = state["current_task"]
        messages = state["messages"]
        
        # 根据任务类型计划动作
        task_type = task_info.split("|")[0] if "|" in task_info else "unknown"
        
        planning_prompt = f"""基于任务类型 '{task_type}'，计划需要调用的工具。

可用工具：
- search_pim_files: 搜索文件
- compile_pim: 编译文件
- check_log: 查看日志
- list_projects: 列出项目
- stop_compilation: 终止编译

用户请求：{messages[-1].content if messages else ''}

返回格式：工具名|参数
如果不需要工具，返回：none|none"""
        
        response = self.llm.invoke([HumanMessage(content=planning_prompt)])
        plan = response.content.strip()
        
        messages.append(AIMessage(content=f"计划执行：{plan}"))
        state["messages"] = messages
        return state
    
    def should_execute(self, state: AgentState) -> str:
        """判断是否需要执行工具"""
        last_message = state["messages"][-1].content
        if "none|none" in last_message:
            return "respond"
        return "execute"
    
    def execute_tools(self, state: AgentState) -> AgentState:
        """执行工具"""
        messages = state["messages"]
        last_message = messages[-1].content
        
        # 解析工具调用
        if "|" in last_message:
            parts = last_message.split("|")
            tool_name = parts[0].split("：")[-1].strip()
            tool_input = parts[1].strip() if len(parts) > 1 else ""
            
            if tool_name in self.tools_by_name:
                # 执行工具
                tool = self.tools_by_name[tool_name]
                try:
                    result = tool.func(tool_input)
                    messages.append(AIMessage(content=f"工具执行结果：\n{result}"))
                except Exception as e:
                    messages.append(AIMessage(content=f"工具执行错误：{str(e)}"))
                    state["error_count"] = state.get("error_count", 0) + 1
        
        state["messages"] = messages
        return state
    
    def check_result(self, state: AgentState) -> AgentState:
        """检查执行结果"""
        # 这里可以添加结果验证逻辑
        return state
    
    def should_continue(self, state: AgentState) -> str:
        """判断是否继续执行"""
        # 如果有错误且错误次数过多，停止
        if state.get("error_count", 0) > 3:
            return "respond"
        
        # 检查是否需要继续执行
        messages = state["messages"]
        if any("编译已启动" in msg.content for msg in messages[-3:]):
            return "respond"
        
        return "respond"  # 默认响应
    
    def generate_response(self, state: AgentState) -> AgentState:
        """生成最终响应"""
        messages = state["messages"]
        
        # 提取关键信息生成响应
        summary_prompt = f"""基于以下对话历史，生成简洁的响应：

{chr(10).join([f"{msg.type}: {msg.content}" for msg in messages[-5:]])}

生成用户友好的响应："""
        
        response = self.llm.invoke([HumanMessage(content=summary_prompt)])
        messages.append(AIMessage(content=response.content))
        
        state["messages"] = messages
        return state
    
    def chat(self, user_input: str, history: List[BaseMessage] = None) -> str:
        """处理用户输入"""
        if history is None:
            history = []
        
        # 添加用户消息
        history.append(HumanMessage(content=user_input))
        
        # 初始状态
        initial_state = {
            "messages": history,
            "current_task": "",
            "compilation_status": {},
            "error_count": 0
        }
        
        # 运行工作流
        final_state = self.app.invoke(initial_state)
        
        # 返回最后的 AI 响应
        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage) and not msg.content.startswith("计划执行："):
                return msg.content
        
        return "抱歉，我无法处理您的请求。"


def create_langgraph_agent(llm_config: Optional[Dict[str, Any]] = None):
    """创建 LangGraph Agent"""
    graph = PIMCompilerGraph(llm_config)
    
    # 创建一个兼容 AgentExecutor 接口的包装器
    class GraphWrapper:
        def __init__(self, graph):
            self.graph = graph
            self.history = []
        
        def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
            user_input = inputs.get("input", "")
            response = self.graph.chat(user_input, self.history)
            self.history.append(HumanMessage(content=user_input))
            self.history.append(AIMessage(content=response))
            return {"output": response}
    
    return GraphWrapper(graph)


def main():
    """主函数"""
    print("🤖 PIM 编译器助手 - LangGraph 版本")
    print("=" * 60)
    print("这是一个基于 LangGraph 的高级版本，提供：")
    print("- 更好的状态管理")
    print("- 错误处理和重试")
    print("- 工作流可视化")
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
    
    # 创建 agent
    agent = create_langgraph_agent(llm_config)
    
    print("输入 'exit' 退出\n")
    
    # 交互循环
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 执行
            result = agent.invoke({"input": user_input})
            print(f"\n助手: {result['output']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 出错了: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()