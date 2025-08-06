#!/usr/bin/env python3
"""LangChain 集成的 GenericReactAgent 工具封装"""

import os
import sys
import re
from pathlib import Path
from typing import Type, Optional
from pydantic import BaseModel, Field

# 环境设置
sys.path.insert(0, str(Path(__file__).parent))
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

from langchain_core.tools import BaseTool, StructuredTool
from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


def sanitize_tool_name(name: str) -> str:
    """
    将工具名称转换为符合 OpenAI API 要求的格式
    
    OpenAI API 要求工具名称只能包含字母、数字、下划线和连字符
    
    Args:
        name: 原始名称
        
    Returns:
        符合规范的名称
    """
    # 移除或替换不符合规范的字符
    # 先尝试音译中文到拼音（简单处理）
    name = name.replace("开发者", "developer")
    name = name.replace("测试员", "tester")
    name = name.replace("主管", "manager")
    name = name.replace("代码生成", "code_generator")
    name = name.replace("代码执行", "code_runner")
    name = name.replace("代码审查", "code_reviewer")
    name = name.replace("项目管理", "project_manager")
    
    # 移除所有非字母数字下划线连字符的字符
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    
    # 移除连续的下划线
    name = re.sub(r'_+', '_', name)
    
    # 移除开头和结尾的下划线
    name = name.strip('_')
    
    # 如果名称为空，使用默认值
    if not name:
        name = "generic_agent"
    
    return name


class TeeOutput:
    """同时输出到多个流的类"""
    
    def __init__(self, *streams):
        self.streams = streams
    
    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()
    
    def flush(self):
        for stream in self.streams:
            stream.flush()


class AgentToolWrapper:
    """GenericReactAgent 的工具封装"""
    
    def __init__(self, agent: GenericReactAgent, show_execution: bool = True):
        """
        初始化工具封装
        
        Args:
            agent: GenericReactAgent 实例
            show_execution: 是否显示执行过程
        """
        self.agent = agent
        self.show_execution = show_execution
        self._initial_files = set()  # 记录初始文件
        self._scan_initial_files()
    
    def _scan_initial_files(self):
        """扫描工作目录中的初始文件"""
        output_dir = Path(self.agent.work_dir)
        if output_dir.exists():
            self._initial_files = {str(f.relative_to(output_dir)) 
                                 for f in output_dir.rglob("*") 
                                 if f.is_file() and not str(f).startswith('__pycache__') 
                                 and not str(f).startswith('.')}
    
    def execute(self, task: str) -> str:
        """
        执行任务
        
        Args:
            task: 任务描述
            
        Returns:
            执行结果（最后一条AI消息）
        """
        try:
            import sys
            import io
            
            # 如果需要显示执行过程
            if self.show_execution:
                # 直接执行，不捕获输出
                result = self.agent.execute_task(task)
            else:
                # 捕获输出但不显示
                output_buffer = io.StringIO()
                old_stdout = sys.stdout
                sys.stdout = output_buffer
                try:
                    result = self.agent.execute_task(task)
                finally:
                    sys.stdout = old_stdout
            
            # 直接返回执行结果
            return result
            
        except Exception as e:
            return f"执行出错: {str(e)}"


# Pydantic 模型用于工具参数
class GenericAgentInput(BaseModel):
    task: str = Field(description="要执行的任务描述")


def create_langchain_tool(agent: GenericReactAgent) -> StructuredTool:
    """
    创建 LangChain 工具
    
    Args:
        agent: GenericReactAgent 实例
        
    Returns:
        LangChain StructuredTool
    """
    wrapper = AgentToolWrapper(agent)
    
    # 从 agent 获取接口声明
    interface = agent.interface
    
    # 创建工具描述
    tool_description = f"""{interface}

输入: 任务描述字符串
输出: 执行结果字符串"""
    
    # 获取 agent 名称并清理
    agent_name = agent.name if hasattr(agent, 'name') else "generic_react_agent"
    tool_name = sanitize_tool_name(agent_name)
    
    # 创建 LangChain 工具
    tool = StructuredTool.from_function(
        func=wrapper.execute,
        name=tool_name,
        description=tool_description,
        args_schema=GenericAgentInput,
        return_direct=False
    )
    
    return tool


# 自定义工具类（另一种方式）
class GenericAgentTool(BaseTool):
    """GenericReactAgent 的 LangChain 工具类"""
    
    name: str = "generic_react_agent"
    description: str = "通用任务执行工具"
    args_schema: Type[BaseModel] = GenericAgentInput
    agent: Optional[GenericReactAgent] = None
    wrapper: Optional[AgentToolWrapper] = None
    
    class Config:
        """Pydantic 配置"""
        arbitrary_types_allowed = True
    
    def __init__(self, agent: GenericReactAgent, **kwargs):
        """初始化工具"""
        # 从 agent 获取接口声明
        description = agent.interface
        # 从 agent 获取名称，如果没有传入 name 参数
        if 'name' not in kwargs:
            agent_name = agent.name if hasattr(agent, 'name') else "generic_react_agent"
            kwargs['name'] = sanitize_tool_name(agent_name)
        # 创建 wrapper
        wrapper = AgentToolWrapper(agent)
        super().__init__(
            agent=agent,
            wrapper=wrapper,
            description=description,
            **kwargs
        )
    
    def _run(self, task: str) -> str:
        """执行工具"""
        if self.wrapper:
            return self.wrapper.execute(task)
        else:
            return "Error: Wrapper not initialized"
    
    async def _arun(self, task: str) -> str:
        """异步执行（目前只是同步调用）"""
        return self._run(task)


# 便捷函数：创建带有特定配置的工具
def create_code_generation_tool(output_dir: str = "output/code_gen") -> StructuredTool:
    """创建代码生成专用工具"""
    config = ReactAgentConfig(
        work_dir=output_dir,
        memory_level=MemoryLevel.NONE,
        knowledge_file="先验知识.md",
        llm_model="kimi-k2-0711-preview",
        llm_base_url="https://api.moonshot.cn/v1",
        llm_api_key_env="MOONSHOT_API_KEY",
        llm_temperature=0,
        interface="""代码生成工具
        
专门用于生成各种编程语言的代码，支持：
- Python, JavaScript, Java, C++ 等主流语言
- Web 应用（FastAPI, Django, React, Vue）
- 数据处理脚本
- 算法实现
- 测试代码

特别适合：
- 根据需求快速生成代码框架
- 创建项目模板
- 生成 API 接口
- 实现算法和数据结构"""
    )
    
    agent = GenericReactAgent(config)
    return create_langchain_tool(agent)


def create_file_processing_tool(output_dir: str = "output/file_proc") -> StructuredTool:
    """创建文件处理专用工具"""
    config = ReactAgentConfig(
        work_dir=output_dir,
        memory_level=MemoryLevel.NONE,
        interface="""文件处理工具
        
专门用于批量处理文件，支持：
- 文件格式转换
- 批量重命名
- 内容替换
- 文件整理和归档

适用场景：
- 数据清洗
- 日志处理
- 配置文件生成
- 文档批量处理"""
    )
    
    agent = GenericReactAgent(config)
    return create_langchain_tool(agent)


# 示例：在 LangChain Agent 中使用
def example_langchain_integration():
    """演示如何在 LangChain Agent 中集成"""
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_openai import ChatOpenAI
    
    # 创建多个专用工具
    code_gen_tool = create_code_generation_tool()
    file_proc_tool = create_file_processing_tool()
    
    # 创建自定义工具
    custom_config = ReactAgentConfig(
        work_dir="output/custom",
        memory_level=MemoryLevel.SMART,
        interface="自定义任务执行工具，根据具体需求执行各种任务"
    )
    custom_agent = GenericReactAgent(custom_config)
    custom_tool = GenericAgentTool(custom_agent)
    
    # 工具列表
    tools = [code_gen_tool, file_proc_tool, custom_tool]
    
    # 创建 LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # 创建提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个任务协调助手，可以使用不同的工具来完成用户的请求。"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # 创建 agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # 使用示例
    result = agent_executor.invoke({
        "input": "帮我创建一个 Python 的 Web API，用于管理图书"
    })
    
    return result


if __name__ == "__main__":
    print("=== LangChain Agent Tool 测试 ===\n")
    
    # 1. 创建基本工具
    print("1. 创建基本工具:")
    config = ReactAgentConfig(
        work_dir="output/test",
        memory_level=MemoryLevel.NONE
    )
    agent = GenericReactAgent(config)
    wrapper = AgentToolWrapper(agent)
    result = wrapper.execute("创建一个简单的计算器类")
    print(result)
    
    print("\n" + "="*50 + "\n")
    
    # 2. 创建 LangChain 工具
    print("2. 创建 LangChain 工具:")
    tool = create_langchain_tool(agent)
    print(f"工具名称: {tool.name}")
    print(f"工具描述: {tool.description[:100]}...")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 使用专用工具
    print("3. 使用代码生成工具:")
    code_tool = create_code_generation_tool()
    result = code_tool.run("创建一个 FastAPI 用户认证接口")
    print(result)