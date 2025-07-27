#!/usr/bin/env python3
"""演示工具规范如何传递给 LangChain Framework"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

from langchain_core.tools import tool
from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


# 方法1: 使用 @tool 装饰器
def method1_tool_decorator():
    """方法1: 通过 @tool 装饰器传递规范"""
    
    # 创建带规范的 agent
    config = ReactAgentConfig(
        output_dir="output/method1",
        memory_level=MemoryLevel.NONE,
        specification="""FastAPI 代码生成器
        
功能：专门生成 FastAPI 应用代码
支持：RESTful API、数据模型、认证、中间件
输出：完整的 FastAPI 项目结构"""
    )
    agent = GenericReactAgent(config)
    
    # 使用 agent 的规范作为工具描述
    @tool(name="fastapi_generator", description=agent.specification)
    def generate_fastapi_code(task: str) -> str:
        """生成 FastAPI 代码"""
        try:
            agent.execute_task(task)
            return "✅ FastAPI 代码生成成功"
        except Exception as e:
            return f"❌ 生成失败: {str(e)}"
    
    return generate_fastapi_code


# 方法2: 使用 StructuredTool
def method2_structured_tool():
    """方法2: 通过 StructuredTool 传递规范"""
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field
    
    class TaskInput(BaseModel):
        task: str = Field(description="任务描述")
    
    # 创建多个不同规范的 agent
    agents = {
        "frontend": GenericReactAgent(ReactAgentConfig(
            output_dir="output/frontend",
            memory_level=MemoryLevel.NONE,
            specification="""前端代码生成器
            
专注于生成现代前端应用：
- React/Vue/Angular 组件
- TypeScript 支持
- 响应式设计
- 状态管理"""
        )),
        "backend": GenericReactAgent(ReactAgentConfig(
            output_dir="output/backend",
            memory_level=MemoryLevel.NONE,
            specification="""后端服务生成器
            
专注于生成后端服务：
- RESTful/GraphQL API
- 数据库模型
- 认证授权
- 微服务架构"""
        )),
        "devops": GenericReactAgent(ReactAgentConfig(
            output_dir="output/devops",
            memory_level=MemoryLevel.NONE,
            specification="""DevOps 配置生成器
            
专注于生成部署配置：
- Docker/Kubernetes 配置
- CI/CD 管道
- 监控和日志
- 基础设施即代码"""
        ))
    }
    
    # 为每个 agent 创建工具
    tools = []
    for name, agent in agents.items():
        def create_executor(agent_instance):
            def execute(task: str) -> str:
                try:
                    agent_instance.execute_task(task)
                    return f"✅ {name} 任务完成"
                except Exception as e:
                    return f"❌ {name} 执行失败: {str(e)}"
            return execute
        
        tool = StructuredTool.from_function(
            func=create_executor(agent),
            name=f"{name}_generator",
            description=agent.specification,  # 使用 agent 的规范
            args_schema=TaskInput
        )
        tools.append(tool)
    
    return tools


# 方法3: 自定义 BaseTool
def method3_custom_tool():
    """方法3: 通过自定义 BaseTool 类传递规范"""
    from langchain_core.tools import BaseTool
    from pydantic import BaseModel, Field
    from typing import Type, Optional
    
    class GenericAgentTool(BaseTool):
        """自动从 agent 获取规范的工具"""
        
        name: str = "generic_agent_tool"
        description: str = "通用工具"  # 默认描述
        agent: Optional[GenericReactAgent] = None
        
        class Config:
            """Pydantic 配置"""
            arbitrary_types_allowed = True
        
        def __init__(self, agent: GenericReactAgent, name: str = None):
            # 自动从 agent 获取规范作为描述
            super().__init__(
                name=name or "generic_agent_tool",
                description=agent.specification,
                agent=agent
            )
        
        def _run(self, task: str) -> str:
            """执行任务"""
            try:
                self.agent.execute_task(task)
                return "✅ 任务执行成功"
            except Exception as e:
                return f"❌ 执行失败: {str(e)}"
        
        async def _arun(self, task: str) -> str:
            """异步执行"""
            return self._run(task)
    
    # 创建工具实例
    config = ReactAgentConfig(
        output_dir="output/method3",
        memory_level=MemoryLevel.NONE,
        specification="""数据处理工具
        
专门处理各种数据任务：
- 数据清洗和转换
- 格式转换（CSV, JSON, XML）
- 数据分析脚本
- ETL 管道"""
    )
    agent = GenericReactAgent(config)
    tool = GenericAgentTool(agent, name="data_processor")
    
    return tool


# 演示如何在 LangChain Agent 中使用
def demonstrate_in_langchain():
    """演示在 LangChain Agent 中的完整使用"""
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_openai import ChatOpenAI
    
    # 收集所有工具
    tools = []
    
    # 添加方法1的工具
    tools.append(method1_tool_decorator())
    
    # 添加方法2的工具
    tools.extend(method2_structured_tool())
    
    # 添加方法3的工具
    tools.append(method3_custom_tool())
    
    # 打印所有工具的规范
    print("=== 已注册的工具及其规范 ===\n")
    for tool in tools:
        print(f"工具名称: {tool.name}")
        print(f"规范描述:\n{tool.description}\n")
        print("-" * 50 + "\n")
    
    # 创建 Agent（这里只是示例，不实际运行）
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个多功能开发助手，可以使用以下工具：\n" + 
         "\n".join([f"- {t.name}: {t.description.split('\\n')[0]}" for t in tools])),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    """
    
    return tools


if __name__ == "__main__":
    print("=== 工具规范传递演示 ===\n")
    
    # 演示三种方法
    print("方法1: @tool 装饰器")
    tool1 = method1_tool_decorator()
    print(f"工具描述: {tool1.description}\n")
    
    print("\n方法2: StructuredTool")
    tools2 = method2_structured_tool()
    for t in tools2:
        print(f"{t.name}: {t.description.split(chr(10))[0]}...")
    
    print("\n\n方法3: 自定义 BaseTool")
    tool3 = method3_custom_tool()
    print(f"工具描述: {tool3.description}\n")
    
    print("\n" + "="*50 + "\n")
    
    # 演示完整集成
    demonstrate_in_langchain()