#!/usr/bin/env python3
"""LangChain 集成的 GenericReactAgent 工具封装"""

import os
import sys
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


class AgentToolWrapper:
    """GenericReactAgent 的工具封装"""
    
    def __init__(self, agent: GenericReactAgent):
        """
        初始化工具封装
        
        Args:
            agent: GenericReactAgent 实例
        """
        self.agent = agent
    
    def execute(self, task: str) -> str:
        """
        执行任务
        
        Args:
            task: 任务描述
            
        Returns:
            执行结果
        """
        try:
            self.agent.execute_task(task)
            
            # 收集输出信息
            output_dir = Path(self.agent.output_dir)
            files = list(output_dir.rglob("*"))
            file_count = sum(1 for f in files if f.is_file())
            
            file_list = []
            for f in files:
                if f.is_file():
                    file_list.append(str(f.relative_to(output_dir)))
            
            result = f"✅ 任务完成！生成了 {file_count} 个文件。"
            if file_list:
                result += f"\n文件列表: {', '.join(file_list[:5])}"
                if len(file_list) > 5:
                    result += f" ... (还有 {len(file_list)-5} 个文件)"
            
            return result
            
        except Exception as e:
            return f"❌ 执行失败: {str(e)}"


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
    
    # 从 agent 获取规范描述
    specification = agent.specification
    
    # 创建工具描述
    tool_description = f"""{specification}

输入: 任务描述字符串
输出: 执行结果字符串"""
    
    # 创建 LangChain 工具
    tool = StructuredTool.from_function(
        func=wrapper.execute,
        name="generic_react_agent",
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
    
    def __init__(self, agent: GenericReactAgent, **kwargs):
        """初始化工具"""
        # 从 agent 获取规范描述
        description = agent.specification
        super().__init__(
            agent=agent,
            description=description,
            **kwargs
        )
        self.wrapper = AgentToolWrapper(agent)
    
    def _run(self, task: str) -> str:
        """执行工具"""
        return self.wrapper.execute(task)
    
    async def _arun(self, task: str) -> str:
        """异步执行（目前只是同步调用）"""
        return self._run(task)


# 便捷函数：创建带有特定配置的工具
def create_code_generation_tool(output_dir: str = "output/code_gen") -> StructuredTool:
    """创建代码生成专用工具"""
    config = ReactAgentConfig(
        output_dir=output_dir,
        memory_level=MemoryLevel.NONE,
        knowledge_file="先验知识.md",
        specification="""代码生成工具
        
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
        output_dir=output_dir,
        memory_level=MemoryLevel.NONE,
        specification="""文件处理工具
        
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
        output_dir="output/custom",
        memory_level=MemoryLevel.SMART,
        specification="自定义任务执行工具，根据具体需求执行各种任务"
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
        output_dir="output/test",
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