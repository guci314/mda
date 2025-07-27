#!/usr/bin/env python3
"""
LangChain Plan-and-Execute Agent 演示

展示如何使用 LangChain 的 Plan-and-Execute 架构来处理复杂任务。
这种架构将任务分解为两个阶段：
1. Planning: 创建执行计划
2. Execution: 按步骤执行计划
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# 添加 pim-compiler 到 Python 路径
pim_compiler_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(pim_compiler_path))

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# LangChain 导入
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import Tool, StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field, SecretStr

# Agent CLI 工具导入
from agent_cli.tools import get_all_tools
from agent_cli.core import LLMConfig


class Step(BaseModel):
    """计划中的单个步骤"""
    step_number: int = Field(description="步骤编号")
    description: str = Field(description="步骤描述")
    tools_needed: List[str] = Field(description="需要的工具")
    expected_outcome: str = Field(description="预期结果")
    status: str = Field(default="pending", description="状态: pending/completed/failed")
    result: Optional[str] = Field(default=None, description="执行结果")


class ExecutionPlan(BaseModel):
    """执行计划"""
    task: str = Field(description="任务描述")
    steps: List[Step] = Field(description="执行步骤列表")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "steps": [step.dict() for step in self.steps],
            "created_at": self.created_at
        }


class PlanAndExecuteAgent:
    """Plan-and-Execute Agent 实现"""
    
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        self.llm = self._create_llm()
        self.tools = get_all_tools()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.planner = self._create_planner()
        self.executor = self._create_executor()
        
    def _create_llm(self) -> ChatOpenAI:
        """创建 LLM 实例"""
        if self.llm_config.provider == "openrouter":
            return ChatOpenAI(
                api_key=SecretStr(self.llm_config.api_key) if self.llm_config.api_key else None,
                base_url=self.llm_config.base_url,
                model=self.llm_config.model,
                temperature=0.1,
                default_headers={
                    "HTTP-Referer": "https://github.com/pim-compiler",
                    "X-Title": "LangChain Plan-Execute Demo"
                }
            )
        else:
            return ChatOpenAI(
                api_key=SecretStr(self.llm_config.api_key) if self.llm_config.api_key else None,
                base_url=self.llm_config.base_url,
                model=self.llm_config.model,
                temperature=0.1
            )
    
    def _create_planner(self) -> Any:
        """创建规划器"""
        planner_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个任务规划专家。给定一个任务，你需要创建一个详细的执行计划。

每个步骤应该包含：
1. 步骤编号
2. 清晰的描述
3. 需要使用的工具
4. 预期结果

可用的工具：
{tools}

请以 JSON 格式返回计划：
{{
    "task": "任务描述",
    "steps": [
        {{
            "step_number": 1,
            "description": "步骤描述",
            "tools_needed": ["tool1", "tool2"],
            "expected_outcome": "预期结果"
        }}
    ]
}}

重要提示：
- 每个步骤应该是原子性的、可独立执行的
- 步骤之间的依赖关系应该清晰
- 工具名称必须与可用工具列表中的名称完全匹配"""),
            ("human", "{task}")
        ])
        
        # 获取工具描述
        tools_desc = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
        
        chain = planner_prompt | self.llm
        
        def plan(task: str) -> ExecutionPlan:
            """创建执行计划"""
            response = chain.invoke({
                "task": task,
                "tools": tools_desc
            })
            
            # 解析 JSON 响应
            try:
                # 提取 JSON 内容
                content = response.content
                # 查找 JSON 块
                import re
                json_match = re.search(r'\{[\s\S]*\}', str(content))
                if json_match:
                    plan_data = json.loads(json_match.group())
                else:
                    raise ValueError("未找到有效的 JSON 计划")
                
                # 创建 Step 对象
                steps = []
                for step_data in plan_data.get("steps", []):
                    step = Step(
                        step_number=step_data["step_number"],
                        description=step_data["description"],
                        tools_needed=step_data.get("tools_needed", []),
                        expected_outcome=step_data["expected_outcome"]
                    )
                    steps.append(step)
                
                return ExecutionPlan(
                    task=plan_data.get("task", task),
                    steps=steps
                )
                
            except Exception as e:
                print(f"解析计划失败: {e}")
                print(f"原始响应: {content}")
                # 返回一个简单的默认计划
                return ExecutionPlan(
                    task=task,
                    steps=[
                        Step(
                            step_number=1,
                            description="执行任务",
                            tools_needed=[],
                            expected_outcome="完成任务"
                        )
                    ]
                )
        
        return plan
    
    def _create_executor(self) -> AgentExecutor:
        """创建执行器"""
        # 创建执行提示 - 使用 create_structured_chat_agent 需要的格式
        executor_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个任务执行专家。你需要执行给定的步骤并使用适当的工具。

你可以使用以下工具：
{tools}

工具名称列表：{tool_names}

请使用提供的工具来完成任务。记住：
1. 仔细阅读任务描述
2. 选择合适的工具
3. 验证结果是否符合预期
4. 如果遇到错误，尝试其他方法

使用工具的格式：
```
Action: 工具名称
Action Input: 输入参数
```

{agent_scratchpad}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # 创建代理
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=executor_prompt
        )
        
        # 创建执行器
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def execute_task(self, task: str) -> Dict[str, Any]:
        """执行任务"""
        print(f"\n{'='*60}")
        print(f"任务: {task}")
        print(f"{'='*60}\n")
        
        # 1. 创建计划
        print("📋 创建执行计划...")
        plan = self.planner(task)
        
        print(f"\n✅ 计划创建完成，共 {len(plan.steps)} 个步骤：")
        for step in plan.steps:
            print(f"   步骤 {step.step_number}: {step.description}")
            if step.tools_needed:
                print(f"      工具: {', '.join(step.tools_needed)}")
        
        # 2. 执行计划
        print(f"\n{'='*60}")
        print("🚀 开始执行计划...")
        print(f"{'='*60}\n")
        
        results = []
        for step in plan.steps:
            print(f"\n{'─'*50}")
            print(f"执行步骤 {step.step_number}: {step.description}")
            print(f"{'─'*50}")
            
            try:
                # 构建执行输入
                step_input = {
                    "input": step.description,
                    "step_number": step.step_number,
                    "description": step.description,
                    "tools_needed": ", ".join(step.tools_needed) if step.tools_needed else "任意合适的工具",
                    "expected_outcome": step.expected_outcome
                }
                
                # 执行步骤
                result = self.executor.invoke(step_input)
                
                # 更新步骤状态
                step.status = "completed"
                step.result = result.get("output", "")
                
                print(f"✅ 步骤 {step.step_number} 完成")
                print(f"结果: {step.result[:200]}..." if len(step.result) > 200 else f"结果: {step.result}")
                
                results.append({
                    "step": step.step_number,
                    "status": "success",
                    "result": step.result
                })
                
            except Exception as e:
                step.status = "failed"
                step.result = str(e)
                
                print(f"❌ 步骤 {step.step_number} 失败: {e}")
                
                results.append({
                    "step": step.step_number,
                    "status": "failed",
                    "error": str(e)
                })
                
                # 决定是否继续
                if input("\n是否继续执行后续步骤？(y/n): ").lower() != 'y':
                    break
        
        # 3. 总结执行结果
        print(f"\n{'='*60}")
        print("📊 执行总结")
        print(f"{'='*60}")
        
        completed_steps = sum(1 for step in plan.steps if step.status == "completed")
        print(f"✅ 完成步骤: {completed_steps}/{len(plan.steps)}")
        
        failed_steps = [step for step in plan.steps if step.status == "failed"]
        if failed_steps:
            print(f"❌ 失败步骤:")
            for step in failed_steps:
                print(f"   - 步骤 {step.step_number}: {step.result}")
        
        return {
            "task": task,
            "plan": plan.to_dict(),
            "results": results,
            "summary": {
                "total_steps": len(plan.steps),
                "completed_steps": completed_steps,
                "failed_steps": len(failed_steps)
            }
        }


def main():
    """主函数 - 演示 Plan-and-Execute Agent"""
    
    # 设置 LLM 提供商
    os.environ['LLM_PROVIDER'] = 'deepseek'
    
    # 创建配置
    config = LLMConfig.from_env('deepseek')
    
    print("🤖 LangChain Plan-and-Execute Agent 演示")
    print("=" * 60)
    
    # 创建 Agent
    agent = PlanAndExecuteAgent(llm_config=config)
    
    # 演示任务列表
    demo_tasks = [
        {
            "name": "代码分析任务",
            "task": "分析 /home/guci/aiProjects/mda/pim-compiler/agent_cli/core.py 文件，理解其主要功能和架构"
        },
        {
            "name": "文件创建任务",
            "task": "创建一个简单的 TODO 应用，包含添加、删除和列出任务的功能，保存为 todo_app.py"
        },
        {
            "name": "项目理解任务",
            "task": "理解 pim-compiler 项目的整体架构和主要组件"
        }
    ]
    
    print("\n可用的演示任务：")
    for i, demo in enumerate(demo_tasks, 1):
        print(f"{i}. {demo['name']}: {demo['task'][:50]}...")
    
    # 选择任务
    choice = input("\n选择一个任务 (1-3) 或输入自定义任务: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(demo_tasks):
        task = demo_tasks[int(choice) - 1]["task"]
    else:
        task = choice
    
    # 执行任务
    try:
        result = agent.execute_task(task)
        
        # 保存结果
        output_file = f"plan_execute_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()