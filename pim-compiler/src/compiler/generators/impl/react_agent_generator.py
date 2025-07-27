"""
React Agent 代码生成器实现
使用 LangChain 的 React Agent 进行代码生成
"""

import os
import time
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging
from datetime import datetime
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from pydantic import BaseModel, Field

from ..base_generator import BaseGenerator, GeneratorConfig, GenerationResult


# 软件工程知识注入
SOFTWARE_ENGINEERING_KNOWLEDGE = """
## 软件工程原则和知识

### 1. 分层架构原则
- **表现层**: 处理 HTTP 请求，包括路由、控制器、API 端点
- **业务逻辑层**: 包含服务类、业务规则、工作流
- **数据访问层**: 包含仓储、数据映射、数据库交互
- **领域模型层**: 核心实体、值对象、领域逻辑

### 2. 依赖关系规则
- **单向依赖**: 上层依赖下层，下层不依赖上层
- **依赖顺序**: API → Service → Repository → Domain Model
- **横向隔离**: 同层组件之间应该松耦合

### 3. 文件组织最佳实践
- 每个 Python 包必须包含 __init__.py 文件
- 配置文件应该独立管理 (config.py, settings.py)
- 数据库配置应该集中管理 (database.py)
- 使用相对导入保持包的可移植性

### 4. 代码生成顺序
1. 配置文件 (config.py, settings.py)
2. 数据库配置 (database.py)
3. Domain Model (models/*.py)
4. Schema/DTO (schemas/*.py)
5. Repository/DAO (repositories/*.py)
6. Service Layer (services/*.py)
7. API/Controller (api/*.py)
8. Main Application (main.py)

### 5. FastAPI 特定知识
- 使用 Pydantic v2 进行数据验证
- 依赖注入通过 Depends() 实现
- 数据库会话通过依赖注入管理
- 路由应该分组并使用 prefix
- 使用 response_model 确保类型安全

### 6. 测试和质量保证
- 为每个服务方法编写单元测试
- 使用 pytest 作为测试框架
- 使用 pytest-asyncio 测试异步代码
- Mock 外部依赖（数据库、第三方服务）
- 测试覆盖率应达到 80% 以上

### 7. 代码生成和测试流程
1. 生成所有代码文件
2. 创建虚拟环境（可选）
3. 安装依赖 (pip install -r requirements.txt)
4. 运行测试 (pytest tests/)
5. 如果测试失败，分析错误并修复代码
6. 重复步骤 4-5 直到所有测试通过
"""


# Pydantic 模型定义
class FileWriteInput(BaseModel):
    """写入文件的输入参数"""
    file_path: str = Field(description="要写入的文件路径")
    content: str = Field(description="文件内容")


class FileReadInput(BaseModel):
    """读取文件的输入参数"""
    file_path: str = Field(description="要读取的文件路径")


class DirectoryListInput(BaseModel):
    """列出目录内容的输入参数"""
    directory_path: str = Field(description="要列出的目录路径", default=".")


class CreateDirectoryInput(BaseModel):
    """创建目录的输入参数"""
    directory_path: str = Field(description="要创建的目录路径")


class RunCommandInput(BaseModel):
    """运行命令的输入参数"""
    command: str = Field(description="要运行的命令")
    cwd: Optional[str] = Field(None, description="工作目录（相对于输出目录）")
    timeout: Optional[int] = Field(60, description="命令超时时间（秒）")


class InstallDependenciesInput(BaseModel):
    """安装依赖的输入参数"""
    requirements_file: Optional[str] = Field("requirements.txt", description="requirements文件路径")


class RunTestsInput(BaseModel):
    """运行测试的输入参数"""
    test_dir: Optional[str] = Field("tests", description="测试目录")
    verbose: bool = Field(True, description="是否输出详细信息")


class ReactAgentGenerator(BaseGenerator):
    """React Agent 代码生成器
    
    使用 LangChain 的 React Agent 进行智能代码生成
    """
    
    def setup(self):
        """初始化设置"""
        # 设置 LangChain 缓存
        cache_path = self.config.extra_params.get("cache_path", ".langchain.db") if self.config.extra_params else ".langchain.db"
        set_llm_cache(SQLiteCache(database_path=cache_path))
        self.logger.info(f"LangChain cache configured at: {cache_path}")
        
        # 设置 LLM 配置
        api_key = self.config.api_key or os.getenv("DEEPSEEK_API_KEY")
        api_base = self.config.api_base or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = self.config.model or "deepseek-chat"
        
        if not api_key:
            raise ValueError("API key not provided. Set DEEPSEEK_API_KEY or provide in config")
        
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=api_base,
            temperature=self.config.temperature
        )
        
        self.logger.info(f"Initialized React Agent with model: {model}")
    
    def generate_psm(
        self, 
        pim_content: str, 
        platform: str = "fastapi",
        output_dir: Optional[Path] = None
    ) -> GenerationResult:
        """从 PIM 生成 PSM"""
        start_time = time.time()
        
        if output_dir is None:
            output_dir = Path.cwd()
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用并行生成方案
        if self.config.extra_params and self.config.extra_params.get("use_parallel", True):
            return self._generate_psm_parallel(pim_content, platform, output_dir, start_time)
        else:
            # 保留原有的 React Agent 方案
            return self._generate_psm_with_agent(pim_content, platform, output_dir, start_time)
    
    def _generate_psm_parallel(
        self,
        pim_content: str,
        platform: str,
        output_dir: Path,
        start_time: float
    ) -> GenerationResult:
        """使用并行方案生成 PSM"""
        self.logger.info("Using parallel PSM generation")
        
        # 运行异步并行生成
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self._async_generate_psm_parallel(pim_content, platform, output_dir)
            )
            
            # 合并生成的章节
            psm_content = self._merge_psm_chapters(result, platform)
            
            # 保存 PSM 文件
            psm_file = output_dir / "psm.md"
            psm_file.write_text(psm_content, encoding='utf-8')
            
            # 保存各章节文件
            for chapter_name, content in result.items():
                if content:
                    chapter_file = output_dir / f"psm_{chapter_name}.md"
                    chapter_file.write_text(content, encoding='utf-8')
            
            # 保存生成报告
            report = {
                "generation_time": datetime.now().isoformat(),
                "platform": platform,
                "duration_seconds": time.time() - start_time,
                "chapters": list(result.keys()),
                "success": all(content for content in result.values())
            }
            report_file = output_dir / "psm_generation_report.json"
            report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            
            return GenerationResult(
                success=True,
                output_path=output_dir,
                psm_content=psm_content,
                generation_time=time.time() - start_time,
                logs=f"Generated PSM with {len(result)} chapters in parallel"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate PSM in parallel: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
        finally:
            loop.close()
    
    async def _async_generate_psm_parallel(
        self,
        pim_content: str,
        platform: str,
        output_dir: Path
    ) -> Dict[str, str]:
        """异步并行生成 PSM 的各个章节"""
        # 定义要生成的章节
        chapters = ["domain", "service", "api", "config"]
        
        # 创建异步任务
        tasks = [
            self._generate_psm_chapter(pim_content, platform, chapter)
            for chapter in chapters
        ]
        
        # 并行执行所有任务
        results = await asyncio.gather(*tasks)
        
        # 返回结果字典
        return dict(zip(chapters, results))
    
    async def _generate_psm_chapter(
        self,
        pim_content: str,
        platform: str,
        chapter: str
    ) -> str:
        """生成 PSM 的单个章节"""
        self.logger.info(f"Generating PSM chapter: {chapter}")
        
        # 获取章节对应的提示词
        system_prompt = self._get_psm_system_prompt(platform)
        chapter_prompt = self._get_psm_chapter_prompt(chapter, platform)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"{chapter_prompt}\n\nPIM 内容:\n```markdown\n{pim_content}\n```")
        ]
        
        try:
            # 使用 ainvoke 进行异步调用
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            self.logger.error(f"Failed to generate {chapter} chapter: {e}")
            return ""
    
    def _get_psm_system_prompt(self, platform: str) -> str:
        """获取 PSM 生成的系统提示词"""
        framework = self._get_framework_for_platform(platform)
        orm = self._get_orm_for_platform(platform)
        validator = self._get_validation_lib_for_platform(platform)
        
        return f"""你是一个专业的软件架构师，负责生成 PSM（Platform Specific Model）。

目标平台: {platform}
技术栈:
- 框架: {framework}
- ORM: {orm}
- 验证库: {validator}

要求:
1. 生成详细的技术规范
2. 包含具体的类型定义和约束
3. 使用中文注释说明业务逻辑
4. 遵循平台最佳实践"""
    
    def _get_psm_chapter_prompt(self, chapter: str, platform: str) -> str:
        """获取各章节的生成提示词"""
        prompts = {
            "domain": """生成 Domain Models 章节，包含：
1. 实体定义（Entity）
   - 属性详细说明
   - 数据类型（使用平台特定类型）
   - 约束条件（唯一性、必填、长度等）
   - 关系定义

2. 值对象（Value Objects）
   - 不可变对象定义
   - 业务含义说明

3. 枚举定义（Enums）
   - 状态枚举
   - 类型枚举

4. 领域规则
   - 业务约束
   - 验证规则""",
            
            "service": """生成 Service Layer 章节，包含：
1. 服务接口定义
   - 方法签名
   - 参数说明
   - 返回值定义
   - 异常说明

2. 业务流程
   - 详细的方法实现逻辑
   - 事务边界
   - 错误处理

3. 仓储接口（Repository）
   - CRUD 操作定义
   - 查询方法
   - 分页支持""",
            
            "api": """生成 API Design 章节，包含：
1. RESTful 端点设计
   - HTTP 方法
   - URL 路径
   - 请求/响应格式
   - 状态码

2. 请求验证
   - 参数验证规则
   - 请求体格式

3. 响应格式
   - 成功响应
   - 错误响应
   - 分页格式

4. API 版本控制策略""",
            
            "config": """生成 Configuration 章节，包含：
1. 应用配置
   - 数据库连接
   - 服务端口
   - 环境变量

2. 依赖配置
   - 第三方服务
   - 中间件配置

3. 安全配置
   - 认证方式
   - 授权策略
   - CORS 设置

4. 部署配置
   - Docker 配置
   - 环境差异"""
        }
        
        return prompts.get(chapter, "生成章节内容")
    
    def _merge_psm_chapters(self, chapters: Dict[str, str], platform: str) -> str:
        """合并各章节为完整的 PSM"""
        psm_content = f"""# Platform Specific Model (PSM)

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
目标平台: {platform}
框架: {self._get_framework_for_platform(platform)}
ORM: {self._get_orm_for_platform(platform)}
验证库: {self._get_validation_lib_for_platform(platform)}

---

"""
        
        # 按顺序添加各章节
        chapter_order = ["domain", "service", "api", "config"]
        chapter_titles = {
            "domain": "## 1. Domain Models（领域模型）",
            "service": "## 2. Service Layer（服务层）",
            "api": "## 3. API Design（API 设计）",
            "config": "## 4. Configuration（配置）"
        }
        
        for chapter in chapter_order:
            if chapter in chapters and chapters[chapter]:
                psm_content += f"{chapter_titles[chapter]}\n\n"
                psm_content += chapters[chapter]
                psm_content += "\n\n---\n\n"
        
        return psm_content
    
    def _generate_psm_with_agent(
        self,
        pim_content: str,
        platform: str,
        output_dir: Path,
        start_time: float
    ) -> GenerationResult:
        """使用原有的 React Agent 方案生成 PSM"""
        # 创建代理工具
        agent = self._create_agent(output_dir)
        
        # 构建提示词
        prompt = f"""请根据以下 PIM（Platform Independent Model）生成对应的 PSM（Platform Specific Model）。

目标平台: {platform}
框架: {self._get_framework_for_platform(platform)}
ORM: {self._get_orm_for_platform(platform)}
验证库: {self._get_validation_lib_for_platform(platform)}

PIM 内容:
```markdown
{pim_content}
```

请生成详细的 PSM 文档，包括：
1. 数据模型定义（包含字段类型、约束等）
2. API 端点设计（RESTful）
3. 服务层方法定义
4. 业务规则说明

将 PSM 保存为 psm.md 文件。"""
        
        try:
            # 执行代理
            result = agent.invoke({"input": prompt})
            
            # 查找生成的 PSM 文件
            psm_file = output_dir / "psm.md"
            if psm_file.exists():
                psm_content = psm_file.read_text(encoding='utf-8')
                return GenerationResult(
                    success=True,
                    output_path=output_dir,
                    psm_content=psm_content,
                    generation_time=time.time() - start_time,
                    logs=result.get("output", "")
                )
            else:
                return GenerationResult(
                    success=False,
                    output_path=output_dir,
                    error_message="PSM file not generated",
                    generation_time=time.time() - start_time
                )
                
        except Exception as e:
            self.logger.error(f"Failed to generate PSM: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def generate_code(
        self, 
        psm_content: str, 
        output_dir: Path,
        platform: str = "fastapi"
    ) -> GenerationResult:
        """从 PSM 生成代码"""
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建代理工具
        agent = self._create_agent(output_dir)
        
        # 构建提示词
        prompt = f"""请根据以下 PSM（Platform Specific Model）生成完整的 {platform} 应用代码。

{SOFTWARE_ENGINEERING_KNOWLEDGE}

PSM 内容:
```markdown
{psm_content}
```

## 重要的项目结构要求：

1. **Python包结构**：
   - 项目根目录必须包含 __init__.py 文件
   - 每个子目录（models/, services/, routers/, db/, tests/ 等）都必须包含 __init__.py 文件
   - 即使 __init__.py 是空文件也必须创建

2. **导入规则**：
   - 应用代码内部使用相对导入：`from .models import User`
   - 测试代码使用绝对导入，并在文件开头添加：
     ```python
     import sys
     from pathlib import Path
     sys.path.insert(0, str(Path(__file__).parent.parent))
     ```

3. **测试文件结构**：
   - 所有测试文件必须以 test_ 开头
   - 测试目录也需要 __init__.py 文件
   - 使用绝对导入引用应用代码

## 示例结构：
```
user_management/
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
├── db/
│   ├── __init__.py      # 必需！
│   └── database.py
├── tests/
│   ├── __init__.py      # 必需！
│   └── test_users.py
└── requirements.txt
```

## 执行步骤：
1. 创建项目根目录和所有子目录
2. 为每个目录创建 __init__.py 文件
3. 生成所有代码文件，确保导入路径正确
4. 生成测试文件，使用正确的导入方式
5. 使用 install_dependencies 工具安装项目依赖
6. 使用 run_tests 工具运行测试验证代码正确性
7. 如果测试失败，分析错误输出并修复代码，然后重新运行测试
8. 只有当所有测试通过后，任务才算完成

现在开始生成代码并执行完整的测试流程！"""
        
        try:
            # 执行代理
            result = agent.invoke({"input": prompt})
            
            # 收集生成的文件
            code_files = {}
            for file_path in output_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.txt', '.md', '.yml', '.yaml']:
                    relative_path = file_path.relative_to(output_dir)
                    try:
                        code_files[str(relative_path)] = file_path.read_text(encoding='utf-8')
                    except:
                        pass
            
            return GenerationResult(
                success=True,
                output_path=output_dir,
                code_files=code_files,
                generation_time=time.time() - start_time,
                logs=result.get("output", "")
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def _create_agent(self, output_dir: Path) -> AgentExecutor:
        """创建 React Agent"""
        
        # 创建工具
        @tool("write_file", args_schema=FileWriteInput)
        def write_file(file_path: str, content: str) -> str:
            """写入文件到指定路径"""
            try:
                full_path = output_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                return f"Successfully wrote file: {file_path}"
            except Exception as e:
                return f"Error writing file {file_path}: {str(e)}"
        
        @tool("read_file", args_schema=FileReadInput)
        def read_file(file_path: str) -> str:
            """读取文件内容"""
            try:
                full_path = output_dir / file_path
                if not full_path.exists():
                    return f"File not found: {file_path}"
                return full_path.read_text(encoding='utf-8')
            except Exception as e:
                return f"Error reading file {file_path}: {str(e)}"
        
        @tool("list_directory", args_schema=DirectoryListInput)
        def list_directory(directory_path: str = ".") -> str:
            """列出目录中的文件和子目录"""
            try:
                full_path = output_dir / directory_path
                if not full_path.exists():
                    return f"Directory not found: {directory_path}"
                
                items = []
                for item in sorted(full_path.iterdir()):
                    if item.is_file():
                        items.append(f"📄 {item.name}")
                    else:
                        items.append(f"📁 {item.name}/")
                
                return "\n".join(items) if items else "Empty directory"
            except Exception as e:
                return f"Error listing directory {directory_path}: {str(e)}"
        
        @tool("create_directory", args_schema=CreateDirectoryInput)
        def create_directory(directory_path: str) -> str:
            """创建目录"""
            try:
                full_path = output_dir / directory_path
                full_path.mkdir(parents=True, exist_ok=True)
                return f"Successfully created directory: {directory_path}"
            except Exception as e:
                return f"Error creating directory {directory_path}: {str(e)}"
        
        @tool("run_command", args_schema=RunCommandInput)
        def run_command(command: str, cwd: Optional[str] = None, timeout: Optional[int] = 60) -> str:
            """运行 shell 命令"""
            try:
                work_dir = output_dir / cwd if cwd else output_dir
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=str(work_dir),
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                output = f"Exit code: {result.returncode}\n"
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                return output
            except subprocess.TimeoutExpired:
                return f"Command timed out after {timeout} seconds"
            except Exception as e:
                return f"Error running command: {str(e)}"
        
        @tool("install_dependencies", args_schema=InstallDependenciesInput)
        def install_dependencies(requirements_file: Optional[str] = "requirements.txt") -> str:
            """安装 Python 依赖"""
            try:
                req_path = output_dir / requirements_file
                if not req_path.exists():
                    return f"Requirements file not found: {requirements_file}"
                
                result = subprocess.run(
                    ["pip", "install", "-r", str(req_path)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode == 0:
                    return f"Successfully installed dependencies from {requirements_file}"
                else:
                    return f"Failed to install dependencies:\n{result.stderr}"
            except subprocess.TimeoutExpired:
                return "Installation timed out after 5 minutes"
            except Exception as e:
                return f"Error installing dependencies: {str(e)}"
        
        @tool("run_tests", args_schema=RunTestsInput)
        def run_tests(test_dir: Optional[str] = "tests", verbose: bool = True) -> str:
            """运行 pytest 测试"""
            try:
                # 查找测试目录
                test_path = output_dir / test_dir
                if not test_path.exists():
                    # 尝试在子目录中查找
                    for subdir in output_dir.iterdir():
                        if subdir.is_dir() and (subdir / test_dir).exists():
                            test_path = subdir / test_dir
                            break
                    else:
                        return f"Test directory not found: {test_dir}"
                
                # 确定工作目录（包含测试的项目根目录）
                work_dir = test_path.parent
                
                # 设置环境变量
                env = os.environ.copy()
                env["PYTHONPATH"] = str(work_dir) + ":" + env.get("PYTHONPATH", "")
                
                cmd = ["python", "-m", "pytest", test_dir]
                if verbose:
                    cmd.append("-v")
                cmd.extend(["--tb=short", "-x"])  # Stop on first failure
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(work_dir),
                    env=env,
                    timeout=180  # 3 minutes timeout
                )
                
                output = f"Working directory: {work_dir}\n"
                output += f"PYTHONPATH: {env['PYTHONPATH']}\n"
                output += f"Exit code: {result.returncode}\n"
                output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                
                return output
            except subprocess.TimeoutExpired:
                return "Tests timed out after 3 minutes"
            except Exception as e:
                return f"Error running tests: {str(e)}"
        
        # 创建工具列表
        tools = [
            write_file, read_file, list_directory, create_directory,
            run_command, install_dependencies, run_tests
        ]
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的代码生成助手，负责根据模型定义生成高质量的应用代码。

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
   - 在测试文件开头添加项目路径：
     ```python
     import sys
     from pathlib import Path
     sys.path.insert(0, str(Path(__file__).parent.parent))
     ```

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

## 工作流程：
1. 分析 PSM 并生成所有必要的代码文件
2. 创建完整的项目结构，确保每个目录都有 __init__.py
3. 生成测试文件时确保使用正确的导入方式
4. 安装项目依赖
5. 运行测试验证代码正确性
6. 如果测试失败，分析错误并修复代码，然后重新运行测试

你可以使用以下工具：
- write_file: 创建和写入文件
- read_file: 读取文件内容
- list_directory: 查看目录结构
- create_directory: 创建目录
- run_command: 运行任意 shell 命令
- install_dependencies: 安装 Python 依赖
- run_tests: 运行 pytest 测试

记住：代码质量和测试通过是最重要的目标。

测试执行注意事项：
1. 测试文件通常在项目根目录下的 tests/ 目录中
2. 运行测试前确保已经安装了所有依赖
3. 如果遇到导入错误，检查：
   - 是否缺少 __init__.py 文件
   - 是否在正确的目录下运行测试
   - 是否需要设置 PYTHONPATH
   - 是否需要使用 pip install -e . 安装包
4. 测试失败后要分析错误信息并修复代码"""),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        
        # 创建代理
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        
        # 创建执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=self.config.extra_params.get("max_iterations", 30) if self.config.extra_params else 30,
            handle_parsing_errors=True,
            max_execution_time=600  # 10 minutes timeout
        )
        
        return agent_executor
    
    def _get_framework_for_platform(self, platform: str) -> str:
        """获取平台对应的框架"""
        frameworks = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
            "springboot": "Spring Boot",
            "express": "Express.js",
            "gin": "Gin"
        }
        return frameworks.get(platform, "FastAPI")
    
    def _get_orm_for_platform(self, platform: str) -> str:
        """获取平台对应的 ORM"""
        orms = {
            "fastapi": "SQLAlchemy",
            "flask": "SQLAlchemy",
            "django": "Django ORM",
            "springboot": "JPA/Hibernate",
            "express": "Sequelize",
            "gin": "GORM"
        }
        return orms.get(platform, "SQLAlchemy")
    
    def _get_validation_lib_for_platform(self, platform: str) -> str:
        """获取平台对应的验证库"""
        validators = {
            "fastapi": "Pydantic",
            "flask": "Marshmallow",
            "django": "Django Forms/Serializers",
            "springboot": "Bean Validation",
            "express": "Joi",
            "gin": "go-playground/validator"
        }
        return validators.get(platform, "Pydantic")