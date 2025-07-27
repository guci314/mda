#!/usr/bin/env python3
"""
PSM 代码生成器 - 使用真正的 LangChain Plan-and-Execute Agent

展示如何使用 LangChain 的 Plan-and-Execute 架构进行代码生成
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime

# 添加 pim-compiler 到 Python 路径
pim_compiler_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(pim_compiler_path))

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# 设置 LLM
os.environ['LLM_PROVIDER'] = 'deepseek'

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool, StructuredTool
from langchain.chains import LLMChain
from pydantic import SecretStr, BaseModel, Field

# Agent CLI 工具
from agent_cli.tools import get_all_tools
from agent_cli.core import LLMConfig


class CodeGenerationPlan(BaseModel):
    """代码生成计划"""
    steps: List[str] = Field(description="计划步骤列表")
    context: Dict[str, Any] = Field(description="执行上下文")


class PlanAndExecuteCodeGenerator:
    """使用 Plan-and-Execute 模式的代码生成器"""
    
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        self.llm = self._create_llm()
        self.tools = self._setup_tools()
        self.planner = self._create_planner()
        self.executor = self._create_executor()
        
    def _create_llm(self):
        """创建LLM实例"""
        return ChatOpenAI(
            api_key=SecretStr(self.llm_config.api_key) if self.llm_config.api_key else None,
            base_url=self.llm_config.base_url,
            model=self.llm_config.model,
            temperature=0.1
        )
    
    def _setup_tools(self) -> List[Tool]:
        """设置工具集"""
        agent_cli_tools = get_all_tools()
        tools = []
        
        # 1. 文件操作工具
        read_tool = next((t for t in agent_cli_tools if t.name == "read_file"), None)
        if read_tool:
            tools.append(Tool(
                name="read_file",
                description="Read file contents. Input: file path",
                func=lambda path: read_tool.run({"path": path.strip()})
            ))
        
        write_tool = next((t for t in agent_cli_tools if t.name == "write_file"), None)
        if write_tool:
            tools.append(Tool(
                name="write_file",
                description="Write content to file. Input: 'path|content'",
                func=lambda x: self._write_file_wrapper(write_tool, x)
            ))
        
        list_tool = next((t for t in agent_cli_tools if t.name == "list_files"), None)
        if list_tool:
            tools.append(Tool(
                name="list_files",
                description="List files in directory. Input: directory path",
                func=lambda path: list_tool.run({"path": path.strip()})
            ))
        
        # 2. Python 执行工具
        python_tool = next((t for t in agent_cli_tools if t.name == "python_repl"), None)
        if python_tool:
            tools.append(Tool(
                name="execute_python",
                description="Execute Python code. Input: Python code",
                func=lambda code: python_tool.run({"code": code})
            ))
        
        # 3. PSM 分析工具
        tools.append(Tool(
            name="analyze_psm",
            description="Analyze PSM model to extract entities, services, and platform. Input: PSM content",
            func=self._analyze_psm_tool
        ))
        
        # 4. 代码生成工具
        tools.append(Tool(
            name="generate_code",
            description="Generate code based on template. Input: 'type|context' where type is models/services/api/tests",
            func=self._generate_code_tool
        ))
        
        # 5. 验证工具
        tools.append(Tool(
            name="validate_code",
            description="Validate generated code. Input: file path",
            func=self._validate_code_tool
        ))
        
        return tools
    
    def _write_file_wrapper(self, write_tool, input_str: str) -> str:
        """写文件工具的包装器"""
        try:
            if "|" not in input_str:
                return "Error: Input must be in format 'path|content'"
            
            parts = input_str.split("|", 1)
            if len(parts) != 2:
                return "Error: Invalid input format"
            
            path, content = parts
            return write_tool.run({
                "path": path.strip(),
                "content": content
            })
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def _analyze_psm_tool(self, psm_content: str) -> str:
        """分析PSM模型"""
        prompt = PromptTemplate.from_template("""
分析以下PSM模型并提取关键信息：

{psm_content}

返回JSON格式：
{{
    "platform": "平台名称",
    "entities": ["实体列表"],
    "services": ["服务列表"],
    "apis": ["API端点列表"]
}}
""")
        
        chain = prompt | self.llm
        response = chain.invoke({"psm_content": psm_content})
        
        return response.content
    
    def _generate_code_tool(self, input_str: str) -> str:
        """生成代码工具"""
        try:
            if "|" not in input_str:
                return "Error: Input must be in format 'type|context'"
            
            code_type, context = input_str.split("|", 1)
            
            prompts = {
                "models": """生成 FastAPI 的数据模型代码：
实体: {context}
要求：使用 SQLAlchemy ORM 和 Pydantic schemas""",
                
                "services": """生成服务层代码：
服务: {context}
要求：实现 CRUD 操作，使用 async/await""",
                
                "api": """生成 API 路由代码：
API: {context}
要求：RESTful 设计，适当的状态码""",
                
                "tests": """生成测试代码：
测试目标: {context}
要求：使用 pytest，包含单元测试和集成测试"""
            }
            
            if code_type not in prompts:
                return f"Error: Unknown code type '{code_type}'"
            
            prompt = PromptTemplate.from_template(prompts[code_type])
            chain = prompt | self.llm
            response = chain.invoke({"context": context})
            
            return response.content
            
        except Exception as e:
            return f"Error generating code: {str(e)}"
    
    def _validate_code_tool(self, file_path: str) -> str:
        """验证代码工具"""
        import subprocess
        
        try:
            # 语法检查
            result = subprocess.run(
                ["python", "-m", "py_compile", file_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"✅ Syntax valid for {file_path}"
            else:
                return f"❌ Syntax error in {file_path}: {result.stderr}"
                
        except Exception as e:
            return f"Error validating {file_path}: {str(e)}"
    
    def _create_planner(self):
        """创建计划器"""
        planner_prompt = PromptTemplate.from_template("""
You are a code generation planner. Given a PSM file path and output directory, 
create a detailed step-by-step plan to generate a complete FastAPI application.

Task: Generate FastAPI code from {psm_file} to {output_dir}

Your plan should include:
1. Reading and analyzing the PSM file
2. Creating project structure
3. Generating models and schemas
4. Generating services
5. Generating API routes
6. Generating tests
7. Validating generated code

For each step, be specific about:
- What tool to use
- What inputs to provide
- What files to create

Output your plan as numbered steps, one per line.
""")
        
        return LLMChain(llm=self.llm, prompt=planner_prompt)
    
    def _create_executor(self):
        """创建执行器"""
        # ReAct agent 作为执行器
        executor_prompt = PromptTemplate.from_template("""
You are a code generation executor. Execute the given step using available tools.

Available tools:
{tools}

Current step: {step}
Context: {context}

Use the following format:
Thought: think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat as needed)
Thought: I have completed the step
Final Answer: summary of what was accomplished

Begin!
Thought: {agent_scratchpad}
""")
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=executor_prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    def generate(self, psm_file: str, output_dir: str) -> Dict[str, Any]:
        """使用 Plan-and-Execute 生成代码"""
        print("🚀 启动 Plan-and-Execute 代码生成")
        print(f"PSM文件: {psm_file}")
        print(f"输出目录: {output_dir}")
        print("=" * 60)
        
        # 1. 生成计划
        print("\n📋 第一阶段：生成执行计划")
        plan_result = self.planner.invoke({
            "psm_file": psm_file,
            "output_dir": output_dir
        })
        
        plan_text = plan_result["text"]
        print("\n生成的计划:")
        print(plan_text)
        
        # 解析计划步骤
        steps = [line.strip() for line in plan_text.split("\n") 
                if line.strip() and line[0].isdigit()]
        
        # 2. 执行计划
        print("\n🔨 第二阶段：执行计划")
        context = {
            "psm_file": psm_file,
            "output_dir": output_dir,
            "generated_files": []
        }
        
        results = []
        for i, step in enumerate(steps, 1):
            print(f"\n{'='*60}")
            print(f"执行步骤 {i}/{len(steps)}: {step}")
            print(f"{'='*60}")
            
            try:
                # 执行单个步骤
                result = self.executor.invoke({
                    "step": step,
                    "context": json.dumps(context)
                })
                
                # 更新上下文
                if "generated_files" in result.get("output", ""):
                    # 简单解析输出中的文件信息
                    output = result["output"]
                    if "created" in output.lower() or "generated" in output.lower():
                        # 提取文件路径（简化实现）
                        import re
                        files = re.findall(r'[/\w]+\.(?:py|txt|md|json)', output)
                        context["generated_files"].extend(files)
                
                results.append({
                    "step": i,
                    "description": step,
                    "status": "completed",
                    "output": result.get("output", "")
                })
                
                print(f"\n✅ 步骤 {i} 完成")
                
            except Exception as e:
                print(f"\n❌ 步骤 {i} 失败: {e}")
                results.append({
                    "step": i,
                    "description": step,
                    "status": "failed",
                    "error": str(e)
                })
        
        # 3. 总结
        print("\n" + "="*60)
        print("📊 执行总结")
        print("="*60)
        
        completed = sum(1 for r in results if r["status"] == "completed")
        print(f"完成步骤: {completed}/{len(steps)}")
        
        if context.get("generated_files"):
            print(f"\n生成的文件:")
            for f in context["generated_files"]:
                print(f"  - {f}")
        
        return {
            "plan": steps,
            "results": results,
            "context": context,
            "success": completed == len(steps)
        }


def main():
    """主函数"""
    print("🎯 PSM 代码生成器 - 真正的 Plan-and-Execute Agent")
    print("=" * 60)
    
    config = LLMConfig.from_env('deepseek')
    generator = PlanAndExecuteCodeGenerator(llm_config=config)
    
    # 演示选项
    print("\n选择演示:")
    print("1. 从示例PSM生成代码")
    print("2. 查看 Plan-and-Execute 的优势")
    
    choice = input("\n你的选择 (1-2): ")
    
    if choice == "1":
        # 创建示例PSM
        example_psm = """
# 任务管理系统 PSM - FastAPI

## 平台
- 框架: FastAPI
- 数据库: SQLite with SQLAlchemy
- 认证: Bearer Token

## 实体
### Task
- id: int (primary key)
- title: str (required)
- description: str
- status: enum [pending, in_progress, completed]
- created_at: datetime
- updated_at: datetime

### User
- id: int (primary key)
- username: str (unique)
- email: str (unique)
- tasks: List[Task]

## 服务
### TaskService
- create_task(task_data)
- get_task(task_id)
- update_task(task_id, task_data)
- delete_task(task_id)
- list_tasks(status=None)

### UserService
- create_user(user_data)
- get_user(user_id)
- get_user_tasks(user_id)

## API端点
- POST /tasks - 创建任务
- GET /tasks - 列出任务
- GET /tasks/{id} - 获取任务
- PUT /tasks/{id} - 更新任务
- DELETE /tasks/{id} - 删除任务
- POST /users - 创建用户
- GET /users/{id}/tasks - 获取用户任务
"""
        
        # 保存示例PSM
        psm_file = "example_task_psm.md"
        with open(psm_file, 'w', encoding='utf-8') as f:
            f.write(example_psm)
        
        output_dir = "generated_task_api"
        
        # 创建输出目录
        Path(output_dir).mkdir(exist_ok=True)
        
        # 生成代码
        result = generator.generate(psm_file, output_dir)
        
        # 保存结果
        with open("plan_execute_result.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: plan_execute_result.json")
        
    elif choice == "2":
        print("\n📚 Plan-and-Execute Agent 的优势：")
        print("\n1. **分离规划和执行**")
        print("   - 规划阶段：LLM 专注于制定完整计划")
        print("   - 执行阶段：按步骤执行，每步都有明确目标")
        
        print("\n2. **更好的可预测性**")
        print("   - 用户可以在执行前审查计划")
        print("   - 每个步骤的目的明确")
        
        print("\n3. **错误恢复**")
        print("   - 单个步骤失败不影响整体")
        print("   - 可以从失败点继续执行")
        
        print("\n4. **适合的场景**")
        print("   - 代码生成（步骤明确）")
        print("   - 项目搭建（流程标准）")
        print("   - 批量任务（可并行化）")
        
        print("\n5. **与 ReAct 的区别**")
        print("   - ReAct: 适合探索性任务，边做边调整")
        print("   - Plan-Execute: 适合结构化任务，先谋后动")


if __name__ == "__main__":
    main()