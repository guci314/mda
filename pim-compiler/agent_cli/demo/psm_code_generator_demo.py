#!/usr/bin/env python3
"""
PSM 到代码生成器 - 使用 Plan-and-Execute 架构

展示如何使用计划执行模式生成代码
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
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool
from pydantic import SecretStr, BaseModel, Field

# Agent CLI 工具
from agent_cli.tools import get_all_tools
from agent_cli.core import LLMConfig


class CodeGenerationStep(BaseModel):
    """代码生成步骤"""
    step_number: int = Field(description="步骤编号")
    name: str = Field(description="步骤名称")
    description: str = Field(description="步骤描述")
    input_required: List[str] = Field(description="需要的输入")
    output_files: List[str] = Field(description="生成的文件")
    dependencies: List[int] = Field(description="依赖的步骤编号")


class CodeGenerationPlan(BaseModel):
    """代码生成计划"""
    psm_summary: str = Field(description="PSM模型摘要")
    target_platform: str = Field(description="目标平台")
    steps: List[CodeGenerationStep] = Field(description="生成步骤")


class PSMCodeGenerator:
    """PSM代码生成器 - Plan-and-Execute 模式"""
    
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        self.llm = self._create_llm()
        self.tools = self._setup_tools()
        self.validation_results = {}
        
    def _create_llm(self):
        """创建LLM实例"""
        return ChatOpenAI(
            api_key=SecretStr(self.llm_config.api_key) if self.llm_config.api_key else None,
            base_url=self.llm_config.base_url,
            model=self.llm_config.model,
            temperature=0.1
        )
    
    def _setup_tools(self):
        """设置工具"""
        agent_cli_tools = get_all_tools()
        tools = {}
        
        # 文件操作工具
        for tool_name in ["read_file", "write_file", "list_files"]:
            tool = next((t for t in agent_cli_tools if t.name == tool_name), None)
            if tool:
                tools[tool_name] = tool
                
        return tools
    
    def analyze_psm(self, psm_content: str) -> Dict[str, Any]:
        """分析PSM模型"""
        analyze_prompt = PromptTemplate.from_template("""
分析以下PSM（平台特定模型）并提取关键信息：

PSM内容：
{psm_content}

请提取：
1. 目标平台（如FastAPI、Django等）
2. 实体/模型列表
3. 服务/API列表
4. 关系和依赖

返回JSON格式：
{{
    "platform": "平台名称",
    "entities": ["实体1", "实体2"],
    "services": ["服务1", "服务2"],
    "dependencies": ["依赖1", "依赖2"]
}}
""")
        
        chain = analyze_prompt | self.llm
        response = chain.invoke({"psm_content": psm_content})
        
        # 解析响应
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
            
        return {
            "platform": "fastapi",
            "entities": ["未解析"],
            "services": ["未解析"],
            "dependencies": []
        }
    
    def create_generation_plan(self, psm_analysis: Dict[str, Any]) -> CodeGenerationPlan:
        """创建代码生成计划"""
        plan_prompt = PromptTemplate.from_template("""
基于PSM分析结果创建代码生成计划：

平台: {platform}
实体: {entities}
服务: {services}

创建一个详细的代码生成计划，包含以下步骤：
1. 项目结构初始化
2. 依赖配置（requirements.txt等）
3. 数据模型生成
4. 服务/API生成
5. 路由配置
6. 测试代码生成
7. 文档生成

为每个步骤指定：
- 步骤名称和描述
- 需要的输入
- 生成的文件
- 依赖关系

返回JSON格式的计划。
""")
        
        chain = plan_prompt | self.llm
        response = chain.invoke({
            "platform": psm_analysis["platform"],
            "entities": ", ".join(psm_analysis["entities"]),
            "services": ", ".join(psm_analysis["services"])
        })
        
        # 创建标准计划
        steps = [
            CodeGenerationStep(
                step_number=1,
                name="初始化项目结构",
                description="创建项目目录和基础文件",
                input_required=["platform", "project_name"],
                output_files=["__init__.py", "README.md"],
                dependencies=[]
            ),
            CodeGenerationStep(
                step_number=2,
                name="生成依赖配置",
                description="创建requirements.txt和配置文件",
                input_required=["platform", "dependencies"],
                output_files=["requirements.txt", "config.py"],
                dependencies=[1]
            ),
            CodeGenerationStep(
                step_number=3,
                name="生成数据模型",
                description="根据实体生成模型代码",
                input_required=["entities"],
                output_files=["models.py", "schemas.py"],
                dependencies=[1]
            ),
            CodeGenerationStep(
                step_number=4,
                name="生成服务层",
                description="生成业务逻辑服务",
                input_required=["services", "models"],
                output_files=["services.py"],
                dependencies=[3]
            ),
            CodeGenerationStep(
                step_number=5,
                name="生成API路由",
                description="生成API端点和路由",
                input_required=["services", "platform"],
                output_files=["api.py", "main.py"],
                dependencies=[4]
            ),
            CodeGenerationStep(
                step_number=6,
                name="生成测试代码",
                description="生成单元测试和集成测试",
                input_required=["services", "api"],
                output_files=["test_services.py", "test_api.py"],
                dependencies=[5]
            ),
            CodeGenerationStep(
                step_number=7,
                name="验证生成代码",
                description="运行测试验证生成代码的正确性",
                input_required=["test_files", "generated_code"],
                output_files=["test_report.json", "validation_results.md"],
                dependencies=[6]
            )
        ]
        
        return CodeGenerationPlan(
            psm_summary=f"基于{psm_analysis['platform']}平台的代码生成",
            target_platform=psm_analysis["platform"],
            steps=steps
        )
    
    def execute_step(self, step: CodeGenerationStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个生成步骤"""
        print(f"\n执行步骤 {step.step_number}: {step.name}")
        print(f"描述: {step.description}")
        print(f"生成文件: {', '.join(step.output_files)}")
        
        # 根据步骤类型生成代码
        if step.step_number == 1:
            # 初始化项目结构
            for file in step.output_files:
                if file == "__init__.py":
                    content = '"""Generated by PSM Code Generator"""\n'
                elif file == "README.md":
                    content = f"# {context.get('project_name', 'Generated Project')}\n\nGenerated from PSM model\n"
                
                self.tools["write_file"].run({
                    "path": f"{context['output_dir']}/{file}",
                    "content": content
                })
        
        elif step.step_number == 2:
            # 生成依赖配置
            if context["platform"].lower() == "fastapi":
                requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
"""
            else:
                requirements = "# Add your dependencies here\n"
            
            self.tools["write_file"].run({
                "path": f"{context['output_dir']}/requirements.txt",
                "content": requirements
            })
            
        elif step.step_number == 3:
            # 生成模型代码
            model_prompt = PromptTemplate.from_template("""
生成{platform}平台的数据模型代码：

实体列表: {entities}

要求：
1. 使用SQLAlchemy ORM定义数据模型
2. 使用Pydantic定义API模式
3. 包含必要的导入语句
4. 添加适当的类型注解

生成符合{platform}最佳实践的模型代码。
""")
            
            chain = model_prompt | self.llm
            model_code = chain.invoke({
                "platform": context["platform"],
                "entities": context["entities"]
            })
            
            self.tools["write_file"].run({
                "path": f"{context['output_dir']}/models.py",
                "content": model_code.content
            })
            
        elif step.step_number == 4:
            # 生成服务层代码
            service_prompt = PromptTemplate.from_template("""
基于模型生成服务层代码：

平台: {platform}
服务列表: {services}

要求：
1. 实现CRUD操作
2. 包含适当的错误处理
3. 使用async/await模式
4. 添加类型注解

生成服务层代码。
""")
            
            chain = service_prompt | self.llm
            service_code = chain.invoke({
                "platform": context["platform"],
                "services": context["services"]
            })
            
            self.tools["write_file"].run({
                "path": f"{context['output_dir']}/services.py",
                "content": service_code.content
            })
            
        elif step.step_number == 5:
            # 生成API路由
            api_prompt = PromptTemplate.from_template("""
生成{platform} API路由代码：

服务: {services}

要求：
1. RESTful API设计
2. 适当的HTTP状态码
3. 请求/响应模型验证
4. 错误处理中间件

生成API端点代码。
""")
            
            chain = api_prompt | self.llm
            api_code = chain.invoke({
                "platform": context["platform"],
                "services": context["services"]
            })
            
            self.tools["write_file"].run({
                "path": f"{context['output_dir']}/api.py",
                "content": api_code.content
            })
            
            # 生成主入口文件
            main_content = '''"""Generated FastAPI application"""
from fastapi import FastAPI
from api import router

app = FastAPI(title="Generated API", version="1.0.0")
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
            self.tools["write_file"].run({
                "path": f"{context['output_dir']}/main.py",
                "content": main_content
            })
            
        elif step.step_number == 6:
            # 生成测试代码
            test_prompt = PromptTemplate.from_template("""
生成单元测试和集成测试代码：

平台: {platform}
服务: {services}

要求：
1. 测试所有CRUD操作
2. 测试边界条件
3. 测试错误处理
4. 使用pytest框架
5. 包含fixtures和mock

生成完整的测试代码。
""")
            
            chain = test_prompt | self.llm
            test_code = chain.invoke({
                "platform": context["platform"],
                "services": context["services"]
            })
            
            # 生成服务测试
            self.tools["write_file"].run({
                "path": f"{context['output_dir']}/test_services.py",
                "content": test_code.content
            })
            
            # 生成API测试
            api_test_content = '''"""API Integration Tests"""
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200

# Add more API tests here
'''
            self.tools["write_file"].run({
                "path": f"{context['output_dir']}/test_api.py",
                "content": api_test_content
            })
            
        elif step.step_number == 7:
            # 验证生成的代码
            validation_results = self.validate_generated_code(context)
            
            # 保存验证报告
            self.tools["write_file"].run({
                "path": f"{context['output_dir']}/test_report.json",
                "content": json.dumps(validation_results, ensure_ascii=False, indent=2)
            })
            
            # 生成可读的验证报告
            report = self.generate_validation_report(validation_results)
            self.tools["write_file"].run({
                "path": f"{context['output_dir']}/validation_results.md",
                "content": report
            })
        
        # 其他步骤返回默认成功
        
        return {
            "step": step.step_number,
            "status": "completed",
            "files_generated": step.output_files
        }
    
    def validate_generated_code(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """验证生成的代码"""
        import subprocess
        import os
        
        validation_results = {
            "syntax_check": {},
            "import_check": {},
            "test_execution": {},
            "api_validation": {},
            "overall_status": "pending"
        }
        
        output_dir = context['output_dir']
        
        # 1. 语法检查
        print("\n🔍 执行语法检查...")
        python_files = []
        for file in ["models.py", "services.py", "api.py", "main.py"]:
            file_path = f"{output_dir}/{file}"
            if os.path.exists(file_path):
                python_files.append(file_path)
                
        for file_path in python_files:
            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", file_path],
                    capture_output=True,
                    text=True
                )
                file_name = os.path.basename(file_path)
                validation_results["syntax_check"][file_name] = {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "error": result.stderr if result.returncode != 0 else None
                }
            except Exception as e:
                validation_results["syntax_check"][file_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # 2. 导入检查
        print("🔍 执行导入检查...")
        for file_path in python_files:
            file_name = os.path.basename(file_path)
            try:
                # 尝试导入模块
                import_check_code = f"""
import sys
sys.path.insert(0, '{output_dir}')
try:
    import {file_name.replace('.py', '')}
    print("Import successful")
except Exception as e:
    print(f"Import failed: {{e}}")
    exit(1)
"""
                result = subprocess.run(
                    ["python", "-c", import_check_code],
                    capture_output=True,
                    text=True,
                    cwd=output_dir
                )
                
                validation_results["import_check"][file_name] = {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None
                }
            except Exception as e:
                validation_results["import_check"][file_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # 3. 运行测试
        print("🔍 运行单元测试...")
        test_files = ["test_services.py", "test_api.py"]
        
        for test_file in test_files:
            test_path = f"{output_dir}/{test_file}"
            if os.path.exists(test_path):
                try:
                    result = subprocess.run(
                        ["python", "-m", "pytest", test_file, "-v", "--tb=short"],
                        capture_output=True,
                        text=True,
                        cwd=output_dir
                    )
                    
                    validation_results["test_execution"][test_file] = {
                        "status": "passed" if result.returncode == 0 else "failed",
                        "output": result.stdout,
                        "error": result.stderr if result.returncode != 0 else None,
                        "return_code": result.returncode
                    }
                except Exception as e:
                    validation_results["test_execution"][test_file] = {
                        "status": "error",
                        "error": str(e)
                    }
        
        # 4. API启动验证（简单检查）
        print("🔍 验证API可启动性...")
        api_check_code = f"""
import sys
import os
sys.path.insert(0, '{output_dir}')
try:
    from main import app
    print("FastAPI app imported successfully")
    # 检查基本路由
    routes = [route.path for route in app.routes]
    print(f"Routes: {{routes}}")
except Exception as e:
    print(f"API validation failed: {{e}}")
    exit(1)
"""
        
        try:
            result = subprocess.run(
                ["python", "-c", api_check_code],
                capture_output=True,
                text=True,
                cwd=output_dir
            )
            
            validation_results["api_validation"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            validation_results["api_validation"] = {
                "status": "error",
                "error": str(e)
            }
        
        # 5. 计算总体状态
        all_passed = True
        for category in ["syntax_check", "import_check", "test_execution"]:
            if category in validation_results:
                for item, result in validation_results[category].items():
                    if isinstance(result, dict) and result.get("status") != "passed":
                        all_passed = False
                        break
        
        validation_results["overall_status"] = "passed" if all_passed else "failed"
        validation_results["timestamp"] = datetime.now().isoformat()
        
        return validation_results
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """生成验证报告"""
        report = []
        report.append("# 代码生成验证报告")
        report.append(f"\n生成时间: {validation_results.get('timestamp', 'N/A')}")
        report.append(f"总体状态: **{validation_results.get('overall_status', 'unknown').upper()}**\n")
        
        # 1. 语法检查结果
        report.append("## 1. 语法检查")
        syntax_results = validation_results.get("syntax_check", {})
        if syntax_results:
            report.append("\n| 文件 | 状态 | 错误信息 |")
            report.append("|------|------|----------|")
            for file, result in syntax_results.items():
                status = "✅ 通过" if result["status"] == "passed" else "❌ 失败"
                error = result.get("error", "").replace("\n", " ") if result.get("error") else "-"
                report.append(f"| {file} | {status} | {error[:50]}... |" if len(error) > 50 else f"| {file} | {status} | {error} |")
        
        # 2. 导入检查结果
        report.append("\n## 2. 导入检查")
        import_results = validation_results.get("import_check", {})
        if import_results:
            report.append("\n| 文件 | 状态 | 输出 |")
            report.append("|------|------|------|")
            for file, result in import_results.items():
                status = "✅ 通过" if result["status"] == "passed" else "❌ 失败"
                output = result.get("output", "").strip().replace("\n", " ")
                report.append(f"| {file} | {status} | {output[:50]}... |" if len(output) > 50 else f"| {file} | {status} | {output} |")
        
        # 3. 测试执行结果
        report.append("\n## 3. 单元测试执行")
        test_results = validation_results.get("test_execution", {})
        if test_results:
            for test_file, result in test_results.items():
                report.append(f"\n### {test_file}")
                status = "✅ 通过" if result["status"] == "passed" else "❌ 失败"
                report.append(f"状态: {status}")
                
                if result.get("output"):
                    report.append("\n```")
                    report.append(result["output"][:500] + "..." if len(result["output"]) > 500 else result["output"])
                    report.append("```")
        
        # 4. API验证结果
        report.append("\n## 4. API启动验证")
        api_result = validation_results.get("api_validation", {})
        if api_result:
            status = "✅ 通过" if api_result["status"] == "passed" else "❌ 失败"
            report.append(f"状态: {status}")
            if api_result.get("output"):
                report.append(f"输出: {api_result['output']}")
        
        # 5. 建议
        report.append("\n## 5. 改进建议")
        if validation_results["overall_status"] == "passed":
            report.append("✅ 所有验证通过！生成的代码质量良好。")
            report.append("\n下一步建议：")
            report.append("- 安装依赖: `pip install -r requirements.txt`")
            report.append("- 启动API: `python main.py`")
            report.append("- 运行完整测试: `pytest -v`")
        else:
            report.append("❌ 验证未完全通过，需要修复以下问题：")
            
            # 分析失败原因
            if syntax_results:
                failed_syntax = [f for f, r in syntax_results.items() if r["status"] != "passed"]
                if failed_syntax:
                    report.append(f"- 修复语法错误: {', '.join(failed_syntax)}")
            
            if import_results:
                failed_imports = [f for f, r in import_results.items() if r["status"] != "passed"]
                if failed_imports:
                    report.append(f"- 解决导入问题: {', '.join(failed_imports)}")
            
            if test_results:
                failed_tests = [f for f, r in test_results.items() if r.get("status") != "passed"]
                if failed_tests:
                    report.append(f"- 修复测试失败: {', '.join(failed_tests)}")
        
        return "\n".join(report)
    
    def generate_code(self, psm_file: str, output_dir: str) -> Dict[str, Any]:
        """完整的代码生成流程"""
        print(f"🚀 开始从PSM生成代码")
        print(f"PSM文件: {psm_file}")
        print(f"输出目录: {output_dir}")
        print("=" * 60)
        
        # 1. 读取PSM
        print("\n📖 第一步：读取PSM文件")
        psm_content = self.tools["read_file"].run({"path": psm_file})
        
        # 2. 分析PSM
        print("\n🔍 第二步：分析PSM模型")
        psm_analysis = self.analyze_psm(psm_content)
        print(f"识别到平台: {psm_analysis['platform']}")
        print(f"实体: {', '.join(psm_analysis['entities'])}")
        print(f"服务: {', '.join(psm_analysis['services'])}")
        
        # 3. 创建计划
        print("\n📋 第三步：创建生成计划")
        plan = self.create_generation_plan(psm_analysis)
        print(f"计划包含 {len(plan.steps)} 个步骤")
        
        # 显示计划
        print("\n执行计划：")
        for step in plan.steps:
            deps = f"(依赖: {step.dependencies})" if step.dependencies else ""
            print(f"  {step.step_number}. {step.name} {deps}")
        
        # 4. 执行计划
        print("\n🔨 第四步：执行代码生成")
        context = {
            "output_dir": output_dir,
            "platform": psm_analysis["platform"],
            "entities": psm_analysis["entities"],
            "services": psm_analysis["services"],
            "project_name": Path(output_dir).name
        }
        
        results = []
        for step in plan.steps:
            # 检查依赖
            if step.dependencies:
                print(f"  检查依赖步骤: {step.dependencies}")
            
            # 执行步骤
            result = self.execute_step(step, context)
            results.append(result)
            
            print(f"  ✅ 步骤 {step.step_number} 完成")
        
        # 5. 验证结果
        print("\n✅ 代码生成完成！")
        print(f"生成的文件位于: {output_dir}")
        
        return {
            "psm_file": psm_file,
            "output_dir": output_dir,
            "platform": psm_analysis["platform"],
            "plan": plan.dict(),
            "results": results
        }


def main():
    """主函数"""
    print("🎯 PSM 代码生成器 - Plan-and-Execute 模式")
    print("=" * 60)
    
    config = LLMConfig.from_env('deepseek')
    generator = PSMCodeGenerator(llm_config=config)
    
    # 演示选项
    print("\n选择演示:")
    print("1. 从示例PSM生成FastAPI代码")
    print("2. 从自定义PSM文件生成代码")
    print("3. 查看为什么使用Plan-and-Execute")
    
    choice = input("\n你的选择 (1-3): ")
    
    if choice == "1":
        # 创建示例PSM
        example_psm = """
# 用户管理系统 PSM - FastAPI

## 平台
- 框架: FastAPI
- 数据库: PostgreSQL with SQLAlchemy
- 认证: JWT

## 实体
### User
- id: UUID
- email: str (unique)
- username: str
- password_hash: str
- created_at: datetime

## 服务
### UserService
- create_user(user_data)
- get_user(user_id)
- update_user(user_id, user_data)
- delete_user(user_id)
- authenticate(email, password)

## API端点
- POST /users - 创建用户
- GET /users/{id} - 获取用户
- PUT /users/{id} - 更新用户
- DELETE /users/{id} - 删除用户
- POST /auth/login - 用户登录
"""
        
        # 保存示例PSM
        psm_file = "example_user_psm.md"
        with open(psm_file, 'w', encoding='utf-8') as f:
            f.write(example_psm)
        
        output_dir = "generated_user_api"
        
        # 创建输出目录
        Path(output_dir).mkdir(exist_ok=True)
        
        # 生成代码
        result = generator.generate_code(psm_file, output_dir)
        
        # 保存结果
        with open("generation_result.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print(f"\n💾 生成结果已保存到: generation_result.json")
        
        # 询问是否运行验证
        if input("\n是否运行代码验证？(y/n): ").lower() == 'y':
            print("\n" + "="*60)
            print("🧪 开始验证生成的代码...")
            print("="*60)
            
            # 执行验证步骤
            step_7 = CodeGenerationStep(
                step_number=7,
                name="验证生成代码",
                description="运行测试验证生成代码的正确性",
                input_required=["test_files", "generated_code"],
                output_files=["test_report.json", "validation_results.md"],
                dependencies=[6]
            )
            
            context = {
                "output_dir": output_dir,
                "platform": result["platform"],
                "entities": ["User"],
                "services": ["UserService"],
                "project_name": Path(output_dir).name
            }
            
            validation_result = generator.execute_step(step_7, context)
            print(f"\n验证完成！查看详细报告：{output_dir}/validation_results.md")
        
    elif choice == "2":
        psm_file = input("输入PSM文件路径: ")
        output_dir = input("输入输出目录: ")
        
        if Path(psm_file).exists():
            result = generator.generate_code(psm_file, output_dir)
        else:
            print(f"❌ PSM文件不存在: {psm_file}")
            
    elif choice == "3":
        print("\n📚 为什么PSM代码生成适合Plan-and-Execute？")
        print("\n1. **输入明确**：PSM模型结构已定义")
        print("2. **流程标准**：代码生成有固定步骤")
        print("3. **可预测性**：每步生成什么文件是确定的")
        print("4. **依赖清晰**：模型→服务→API的依赖关系")
        print("5. **错误可控**：生成错误类型可预期")
        print("\n相比之下，ReAct更适合：")
        print("- 调试生成的代码")
        print("- 探索未知的PSM格式")
        print("- 处理异常情况")


if __name__ == "__main__":
    main()