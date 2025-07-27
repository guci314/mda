#!/usr/bin/env python3
"""改进版ReactAgentGenerator v3，包含正确的Python包结构指导"""

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

# 处理代理设置问题 - 临时禁用
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

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

class InstallInput(BaseModel):
    requirements_file: str = Field(default="requirements.txt", description="依赖文件路径")

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
        
        # 创建ChatOpenAI实例  
        return ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0,  # 设置为0以确保输出一致，充分利用缓存
            max_tokens=4000
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

        @tool("install_dependencies", args_schema=InstallInput)
        def install_dependencies(requirements_file: str = "requirements.txt") -> str:
            """安装Python依赖包"""
            try:
                import subprocess
                
                # 查找requirements文件
                req_path = Path(output_dir) / requirements_file
                if not req_path.exists():
                    # 尝试在子目录中查找
                    for subdir in Path(output_dir).iterdir():
                        if subdir.is_dir():
                            temp_path = subdir / requirements_file
                            if temp_path.exists():
                                req_path = temp_path
                                break
                    else:
                        return f"Requirements file not found: {requirements_file}"
                
                # 获取当前Python解释器
                python_exe = sys.executable
                
                # 运行pip install
                result = subprocess.run(
                    [python_exe, "-m", "pip", "install", "-r", str(req_path)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                output = f"Exit code: {result.returncode}\n"
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                
                if result.returncode == 0:
                    output += f"\nSuccessfully installed dependencies from {req_path}"
                else:
                    output += f"\nFailed to install dependencies"
                    
                return output
                
            except subprocess.TimeoutExpired:
                return "Installation timed out after 5 minutes"
            except Exception as e:
                return f"Error installing dependencies: {str(e)}"

        @tool("run_tests", args_schema=TestInput)  
        def run_tests(test_dir: Optional[str] = "tests", verbose: bool = True) -> str:
            """运行 pytest 测试"""
            try:
                import subprocess
                
                # 查找项目根目录（包含tests目录的目录）
                project_root = None
                
                # 首先在输出目录直接查找
                if (Path(output_dir) / test_dir).exists():
                    project_root = Path(output_dir)
                else:
                    # 在子目录中查找
                    for subdir in Path(output_dir).iterdir():
                        if subdir.is_dir() and (subdir / test_dir).exists():
                            project_root = subdir
                            break
                
                if not project_root:
                    return f"Test directory not found: {test_dir}. Searched in {output_dir} and subdirectories."
                
                # 获取当前Python解释器
                python_exe = sys.executable
                
                # 设置环境变量 - 添加项目根目录到PYTHONPATH
                env = os.environ.copy()
                env["PYTHONPATH"] = str(project_root) + ":" + env.get("PYTHONPATH", "")
                
                # 构建命令 - 从项目根目录运行pytest
                cmd = [python_exe, "-m", "pytest", test_dir, "-v", "-s", "--tb=short", "-x"]
                
                # 执行测试
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=str(project_root),  # 在项目根目录运行
                    timeout=180  # 3分钟超时
                )
                
                output = f"Working directory: {project_root}\n"
                output += f"Test directory: {test_dir}\n"
                output += f"Python executable: {python_exe}\n"
                output += f"PYTHONPATH: {env['PYTHONPATH']}\n"
                output += f"Command: {' '.join(cmd)}\n"
                output += f"Exit code: {result.returncode}\n"
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                    
                return output
                
            except subprocess.TimeoutExpired:
                return "Test execution timed out after 3 minutes"
            except Exception as e:
                return f"Error running tests: {str(e)}"

        # 工具列表
        tools = [
            write_file,
            read_file,
            create_directory,
            list_directory,
            install_dependencies,
            run_tests
        ]
        
        # 系统提示词 - 包含正确的Python包结构和测试指导
        system_prompt = f"""你是一个专业的 {self.config.platform} 开发专家。

你的任务是根据 PSM（Platform Specific Model）生成完整的 {self.config.platform} 应用代码。

## 重要的Python包结构规则：

1. **正确的Python包结构**：
   - 每个Python目录都必须包含 `__init__.py` 文件（即使是空文件）
   - 项目根目录应该包含 `__init__.py`
   - 所有子目录（models/, services/, routers/, tests/ 等）都需要 `__init__.py`
   
2. **导入规则**：
   - 在应用代码中使用相对导入：`from .models import User`
   - 在测试代码中使用绝对导入：`from myapp.models import User`
   - 或者创建 `setup.py` 文件支持 `pip install -e .` 安装

3. **测试结构**：
   - 测试文件应该使用绝对导入
   - 测试运行时需要将项目根目录加入 PYTHONPATH
   - 测试文件命名必须以 `test_` 开头

## 示例项目结构：
```
myapp/
├── __init__.py          # 必需！
├── main.py
├── models/
│   ├── __init__.py      # 必需！
│   └── user.py
├── services/
│   ├── __init__.py      # 必需！
│   └── user_service.py
├── routers/
│   ├── __init__.py      # 必需！
│   └── users.py
├── tests/
│   ├── __init__.py      # 必需！
│   └── test_users.py
├── requirements.txt
└── setup.py             # 可选，但推荐
```

## 测试文件示例：
```python
# tests/test_users.py
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from myapp.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_something():
    response = client.get("/")
    assert response.status_code == 200
```

## 或者使用 setup.py：
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="myapp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # 从 requirements.txt 读取
    ],
)
```

## 工作流程：
1. 创建完整的项目结构（包括所有 __init__.py 文件）
2. 生成所有代码文件
3. 确保测试文件使用正确的导入方式
4. 创建 requirements.txt
5. 使用 install_dependencies 工具安装项目依赖
6. 使用 run_tests 工具运行测试
7. 如果测试失败，分析错误并修复代码
8. 重复步骤6-7直到所有测试通过

## 注意事项：
- 必须为每个Python包目录创建 __init__.py 文件
- 测试必须能够正确导入应用代码
- 如果遇到导入错误，检查是否缺少 __init__.py 文件
- 确保测试使用正确的导入路径"""

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
            max_iterations=50,  # 增加迭代次数
            handle_parsing_errors=True
        )
        
        # 执行生成
        input_prompt = f"""请根据以下PSM生成完整的{self.config.platform}应用代码：

{psm_content}

请创建完整的项目结构，包括所有必要的文件。

重要提醒：
1. 每个Python目录都需要 __init__.py 文件
2. 测试文件需要能够正确导入应用代码
3. 生成代码后必须安装依赖并运行测试
4. 只有所有测试通过，任务才算完成"""

        executor.invoke({"input": input_prompt})


def main():
    """主函数"""
    # 配置
    pim_file = Path("../models/domain/用户管理_pim.md")
    output_dir = Path("output/react_agent_v3")
    
    logger.info(f"Using generator: react-agent (v3)")
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
        logger.info("Initialized ReactAgentGenerator v3 with proper Python package guidance")
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
        logger.info("Step 2: Generating code with proper package structure...")
        print("\n[1m> Entering new AgentExecutor chain...[0m")
        
        start_time = time.time()
        generator.generate_code(psm_content, str(output_dir))
        code_time = time.time() - start_time
        
        print("[1m> Finished chain.[0m")
        logger.info(f"Code generated and tested in {code_time:.2f} seconds")
        
        # 统计
        python_files = list(output_dir.rglob("*.py"))
        total_files = list(output_dir.rglob("*.*"))
        
        print("\n" + "=" * 50)
        print("✅ Compilation Successful!")
        print("=" * 50)
        print(f"Generator: react-agent v3")
        print(f"Platform: fastapi")
        print(f"Output: {output_dir}")
        print(f"\nStatistics:")
        print(f"  - PSM generation: {psm_time:.2f}s")
        print(f"  - Code generation & testing: {code_time:.2f}s")
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
        print(f"  cd {output_dir}")
        print("  python -m uvicorn <app_name>.main:app --reload")
        
        return 0
        
    except Exception as e:
        logger.error(f"Compilation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())