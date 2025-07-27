#!/usr/bin/env python3
"""直接运行ReactAgentGenerator，绕过所有导入问题"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 手动导入必要的内容
from dotenv import load_dotenv
load_dotenv()

# 直接复制ReactAgentGenerator的代码，避免导入问题
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from pydantic import BaseModel, Field

# 设置缓存 - 使用绝对路径确保缓存生效
import os
cache_path = os.path.join(os.path.dirname(__file__), ".langchain.db")
set_llm_cache(SQLiteCache(database_path=cache_path))

# 工具定义
class FileInput(BaseModel):
    file_path: str = Field(description="文件路径")
    content: str = Field(description="文件内容")

class DirectoryInput(BaseModel):
    directory_path: str = Field(description="目录路径")

class TestInput(BaseModel):
    test_dir: Optional[str] = Field(default="tests", description="测试目录")
    verbose: bool = Field(default=True, description="是否显示详细输出")

class GeneratorConfig:
    def __init__(self, platform, output_dir, additional_config=None):
        self.platform = platform
        self.output_dir = output_dir
        self.additional_config = additional_config or {}

class ReactAgentGenerator:
    """React Agent 代码生成器"""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.llm = self._create_llm()
        
    def _create_llm(self):
        """创建语言模型"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")
            
        return ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0,  # 设置为0以确保输出一致，充分利用缓存
            max_tokens=4000,
            cache=True  # 显式启用缓存
        )
    
    def generate_psm(self, pim_content: str) -> str:
        """生成PSM"""
        prompt = f"""你是一个专业的软件架构师，负责生成 PSM（Platform Specific Model）。

目标平台: {self.config.platform}

请根据以下PIM生成详细的PSM文档：

{pim_content}

要求：
1. 包含详细的数据模型定义（字段类型、约束等）
2. API端点设计（RESTful）  
3. 服务层方法定义
4. 认证和权限控制
5. 数据库设计

请使用Markdown格式输出。"""

        response = self.llm.invoke(prompt)
        return response.content
    
    def generate_code(self, psm_content: str, output_dir: str):
        """使用React Agent生成代码"""
        # 创建工具
        @tool("write_file", args_schema=FileInput)
        def write_file(file_path: str, content: str) -> str:
            """写入文件"""
            try:
                file_full_path = Path(output_dir) / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                file_full_path.write_text(content, encoding='utf-8')
                return f"Successfully wrote file: {file_path}"
            except Exception as e:
                return f"Error writing file: {str(e)}"

        class ReadFileInput(BaseModel):
            file_path: str = Field(description="文件路径")
        
        @tool("read_file", args_schema=ReadFileInput)
        def read_file(file_path: str) -> str:
            """读取文件"""
            try:
                file_full_path = Path(output_dir) / file_path
                if not file_full_path.exists():
                    return f"File not found: {file_path}"
                content = file_full_path.read_text(encoding='utf-8')
                return content
            except Exception as e:
                return f"Error reading file: {str(e)}"

        @tool("create_directory", args_schema=DirectoryInput)
        def create_directory(directory_path: str) -> str:
            """创建目录"""
            try:
                dir_full_path = Path(output_dir) / directory_path
                dir_full_path.mkdir(parents=True, exist_ok=True)
                return f"Successfully created directory: {directory_path}"
            except Exception as e:
                return f"Error creating directory: {str(e)}"

        @tool("list_directory", args_schema=DirectoryInput)
        def list_directory(directory_path: str = ".") -> str:
            """列出目录内容"""
            try:
                dir_full_path = Path(output_dir) / directory_path
                if not dir_full_path.exists():
                    return f"Directory not found: {directory_path}"
                items = []
                for item in dir_full_path.iterdir():
                    if item.is_dir():
                        items.append(f"[DIR] {item.name}")
                    else:
                        items.append(f"[FILE] {item.name}")
                return "\n".join(items) if items else "Empty directory"
            except Exception as e:
                return f"Error listing directory: {str(e)}"

        @tool("run_tests", args_schema=TestInput)  
        def run_tests(test_dir: Optional[str] = "tests", verbose: bool = True) -> str:
            """运行 pytest 测试"""
            try:
                # 查找测试目录
                test_path = Path(output_dir) / test_dir
                if not test_path.exists():
                    return f"Test directory not found: {test_dir}"
                
                import subprocess
                work_dir = test_path.parent
                
                # 设置环境变量
                env = os.environ.copy()
                env["PYTHONPATH"] = str(work_dir) + ":" + env.get("PYTHONPATH", "")
                
                # 构建命令
                cmd = ["python", "-m", "pytest"]
                if verbose:
                    cmd.append("-v")
                cmd.append(str(test_path))
                
                # 执行测试
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=str(work_dir),
                    timeout=60
                )
                
                output = f"Exit code: {result.returncode}\n"
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                    
                return output
                
            except subprocess.TimeoutExpired:
                return "Test execution timed out after 60 seconds"
            except Exception as e:
                return f"Error running tests: {str(e)}"

        # 工具列表
        tools = [
            write_file,
            read_file,
            create_directory,
            list_directory,
            run_tests
        ]
        
        # 系统提示词
        system_prompt = f"""你是一个专业的 {self.config.platform} 开发专家。

你的任务是根据 PSM（Platform Specific Model）生成完整的 {self.config.platform} 应用代码。

要求：
1. 创建清晰的项目结构
2. 实现所有的数据模型、API端点和服务
3. 包含适当的错误处理和验证
4. 生成 requirements.txt
5. 创建单元测试
6. 运行测试并修复错误

请一步步地创建项目结构和文件。生成代码后，使用 run_tests 工具运行测试。如果测试失败，分析错误并修复代码。"""

        # 创建prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # 创建agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=30,
            handle_parsing_errors=True
        )
        
        # 执行生成
        input_prompt = f"""请根据以下PSM生成完整的{self.config.platform}应用代码：

{psm_content}

请创建完整的项目结构，包括所有必要的文件。在生成代码后，运行测试并修复任何错误。"""

        executor.invoke({"input": input_prompt})


def main():
    """主函数"""
    # 配置
    pim_file = Path("../models/domain/用户管理_pim.md")
    output_dir = Path("output/react_agent_official")
    
    logger.info(f"Using generator: react-agent")
    logger.info(f"Target platform: fastapi")
    logger.info(f"Output directory: {output_dir}")
    
    # 检查PIM文件
    if not pim_file.exists():
        logger.error(f"PIM file not found: {pim_file}")
        return 1
    
    # 读取PIM内容
    pim_content = pim_file.read_text(encoding='utf-8')
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建配置
    config = GeneratorConfig(
        platform="fastapi",
        output_dir=str(output_dir),
        additional_config={}
    )
    
    try:
        # 创建生成器
        generator = ReactAgentGenerator(config)
        logger.info("Initialized ConfigurableCompiler with generator: react-agent")
        logger.info(f"Starting compilation of {pim_file}")
        
        # 步骤1：生成PSM
        logger.info("Step 1: Generating PSM...")
        start_time = time.time()
        psm_content = generator.generate_psm(pim_content)
        psm_time = time.time() - start_time
        logger.info(f"PSM generated in {psm_time:.2f} seconds")
        
        # 保存PSM
        psm_file = output_dir / "user_management_psm.md"
        psm_file.write_text(psm_content, encoding='utf-8')
        
        # 步骤2：生成代码
        logger.info("Step 2: Generating code...")
        print("\n[1m> Entering new AgentExecutor chain...[0m")
        
        start_time = time.time()
        generator.generate_code(psm_content, str(output_dir))
        code_time = time.time() - start_time
        
        print("[1m> Finished chain.[0m")
        logger.info(f"Code generated in {code_time:.2f} seconds")
        
        # 统计
        python_files = list(output_dir.rglob("*.py"))
        total_files = list(output_dir.rglob("*.*"))
        
        print("\n" + "=" * 50)
        print("✅ Compilation Successful!")
        print("=" * 50)
        print(f"Generator: react-agent")
        print(f"Platform: fastapi")
        print(f"Output: {output_dir}")
        print(f"\nStatistics:")
        print(f"  - PSM generation: {psm_time:.2f}s")
        print(f"  - Code generation: {code_time:.2f}s")
        print(f"  - Total time: {psm_time + code_time:.2f}s")
        print(f"  - Files generated: {len(total_files)}")
        print(f"  - Python files: {len(python_files)}")
        
        # 保存日志
        log_file = output_dir / "compile_output.log"
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Compilation completed at {datetime.now()}\n")
            f.write(f"Total time: {psm_time + code_time:.2f}s\n")
            f.write(f"Files generated: {len(total_files)}\n")
        
        print("\nNext steps:")
        print(f"  cd {output_dir}/generated")
        print("  pip install -r requirements.txt")
        print("  uvicorn main:app --reload")
        
        return 0
        
    except Exception as e:
        logger.error(f"Compilation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())