"""
新型编译器实现 - 使用 Gemini CLI 生成代码
"""
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from compiler.config import CompilerConfig
from compiler.llm import LLMClient, DeepSeekClient
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CompilationResult:
    """编译结果"""
    success: bool
    pim_file: Path
    psm_file: Optional[Path] = None
    code_dir: Optional[Path] = None
    error: Optional[str] = None
    compilation_time: Optional[float] = None
    test_results: Optional[Dict[str, Any]] = None


class GeminiCompiler:
    """使用 Gemini CLI 的新型编译器
    
    工作流程：
    1. 使用 DeepSeek 将 PIM 转换为 PSM
    2. 保存 PSM 到文件
    3. 使用 Gemini CLI 读取 PSM 文件生成代码
    4. 运行测试并自动修复（如果启用）
    """
    
    def __init__(self, config: CompilerConfig):
        self.config = config
        self.llm_client = self._create_llm_client()
        self.gemini_cli_path = self._find_gemini_cli()
        
    def _create_llm_client(self) -> LLMClient:
        """创建 LLM 客户端"""
        if self.config.llm_provider.lower() == "deepseek":
            return DeepSeekClient(api_key=self.config.deepseek_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")
    
    def _find_gemini_cli(self) -> str:
        """查找 Gemini CLI 路径"""
        # 尝试常见路径
        possible_paths = [
            "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini",
            os.path.expanduser("~/.local/bin/gemini"),
            "/usr/local/bin/gemini",
            "/usr/bin/gemini"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 使用系统 PATH
        return "gemini"
    
    def compile(self, pim_file: Path) -> CompilationResult:
        """编译 PIM 文件"""
        start_time = datetime.now()
        
        try:
            # 验证输入文件
            if not pim_file.exists():
                return CompilationResult(
                    success=False,
                    pim_file=pim_file,
                    error=f"PIM file not found: {pim_file}"
                )
            
            logger.info(f"Starting compilation of {pim_file}")
            
            # 步骤 1: 转换 PIM 到 PSM
            logger.info("Step 1: Transforming PIM to PSM...")
            psm_content = self._transform_pim_to_psm(pim_file)
            if not psm_content:
                return CompilationResult(
                    success=False,
                    pim_file=pim_file,
                    error="Failed to transform PIM to PSM"
                )
            
            # 步骤 2: 保存 PSM 文件
            psm_dir = self.config.output_dir / "psm"
            psm_dir.mkdir(parents=True, exist_ok=True)
            psm_file = psm_dir / f"{pim_file.stem}_psm.md"
            
            logger.info(f"Step 2: Saving PSM to {psm_file}")
            with open(psm_file, 'w', encoding='utf-8') as f:
                f.write(psm_content)
            
            # 步骤 3: 使用 Gemini CLI 生成代码
            code_dir = self.config.output_dir / "generated" / pim_file.stem
            if code_dir.exists():
                shutil.rmtree(code_dir)
            code_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Step 3: Generating code with Gemini CLI...")
            success = self._generate_code_with_gemini(psm_file, code_dir)
            
            if not success:
                return CompilationResult(
                    success=False,
                    pim_file=pim_file,
                    psm_file=psm_file,
                    code_dir=code_dir,
                    error="Failed to generate code with Gemini CLI"
                )
            
            # 步骤 4: 运行测试和修复（如果启用）
            test_results = None
            if self.config.auto_test:
                logger.info("Step 4: Running tests and auto-fixing...")
                test_results = self._run_tests_and_fix(code_dir)
            
            # 计算编译时间
            compilation_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Compilation completed successfully in {compilation_time:.2f}s")
            
            return CompilationResult(
                success=True,
                pim_file=pim_file,
                psm_file=psm_file,
                code_dir=code_dir,
                compilation_time=compilation_time,
                test_results=test_results
            )
            
        except Exception as e:
            logger.error(f"Compilation failed: {e}")
            return CompilationResult(
                success=False,
                pim_file=pim_file,
                error=str(e)
            )
    
    def _transform_pim_to_psm(self, pim_file: Path) -> Optional[str]:
        """使用 DeepSeek 将 PIM 转换为 PSM"""
        try:
            # 读取 PIM 内容
            with open(pim_file, 'r', encoding='utf-8') as f:
                pim_content = f.read()
            
            # 构建转换提示
            prompt = f"""你是一个专业的软件架构师，精通模型驱动架构（MDA）。

请将下面的平台无关模型（PIM）转换为 {self.config.target_platform} 平台的平台特定模型（PSM）。

PIM 内容：
{pim_content}

要求：
1. 保持业务逻辑不变，只添加技术实现细节
2. 使用 {self.config.target_platform} 的最佳实践和常用技术栈
3. 输出格式为 Markdown，包含以下部分：
   - 技术架构说明
   - 数据模型实现（包含具体的字段类型和约束）
   - API 接口设计（包含路由、请求/响应格式）
   - 业务逻辑实现（包含具体的代码结构）
   - 项目结构说明
   - 依赖列表

技术栈要求：
- 框架：{self._get_framework_for_platform()}
- 数据库：PostgreSQL 或 SQLite
- ORM：{self._get_orm_for_platform()}
- 数据验证：{self._get_validation_lib_for_platform()}
- 测试框架：{self._get_test_framework_for_platform()}

请生成完整、详细的 PSM 文档。
"""
            
            # 调用 LLM
            response = self.llm_client.complete(prompt)
            
            if response and response.strip():
                return response
            else:
                logger.error("Empty response from LLM")
                return None
                
        except Exception as e:
            logger.error(f"Failed to transform PIM to PSM: {e}")
            return None
    
    def _generate_code_with_gemini(self, psm_file: Path, code_dir: Path) -> bool:
        """使用 Gemini CLI 从 PSM 文件生成代码"""
        import time
        import signal
        
        try:
            # 准备工作目录（PSM 文件的上级目录）
            work_dir = psm_file.parent.parent
            
            # 构建提示
            platform = self.config.target_platform
            framework = self._get_framework_for_platform()
            
            prompt = f"""你是一个专业的 {platform} 开发工程师，精通 {framework} 框架。

我有一个平台特定模型（PSM）文件，位于：psm/{psm_file.name}

请你根据这个 PSM 文件生成完整的 {platform} 代码实现。

要求：
1. 仔细阅读 PSM 文件，理解所有需求
2. 在 generated/{code_dir.name}/ 目录下创建完整的项目结构
3. 实现 PSM 中描述的所有功能：
   - 数据模型（使用 ORM）
   - API 接口（RESTful）
   - 业务逻辑服务
   - 配置管理
   - 数据库连接
4. 生成 requirements.txt 或 package.json（根据平台）
5. 生成单元测试文件（在 tests/ 目录下）
6. 添加 README.md 说明如何运行项目

注意事项：
- 使用最新版本的库语法：
  - Pydantic v2+: 使用 'pattern' 而不是 'regex'
  - SQLAlchemy 2.0+: 使用新的查询语法
  - FastAPI: 使用最新的依赖注入方式
- 包含完整的错误处理和输入验证
- 添加适当的日志记录（使用 loguru 或标准 logging）
- 实现基本的安全功能（如密码哈希使用 bcrypt）
- 确保代码符合 PEP 8 规范（Python）或相应语言的规范
- 每个文件都要有适当的文档字符串

项目结构示例（FastAPI）：
generated/{code_dir.name}/
├── src/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API 路由
│   ├── services/            # 业务逻辑
│   └── core/                # 核心配置
├── tests/                   # 单元测试
├── requirements.txt         # 依赖列表
└── README.md               # 项目说明

开始生成代码...
"""
            
            # 准备环境变量
            env = os.environ.copy()
            # 处理 API key 冲突
            if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
                del env["GOOGLE_API_KEY"]
            
            # 获取 Gemini 模型配置
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            
            logger.info(f"Calling Gemini CLI with model {model}")
            logger.info(f"Working directory: {work_dir}")
            
            # 启动 Gemini CLI 进程
            process = subprocess.Popen(
                [self.gemini_cli_path, "-m", model, "-p", prompt, "-y"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=work_dir
            )
            
            # 监控进程和文件生成
            start_time = time.time()
            max_wait_time = 600  # 10分钟
            check_interval = 10  # 每10秒检查一次
            last_file_count = 0
            no_progress_count = 0
            max_no_progress = 6  # 60秒没有新文件生成
            
            while True:
                # 检查进程是否结束
                poll_result = process.poll()
                if poll_result is not None:
                    # 进程已结束
                    stdout, stderr = process.communicate()
                    if poll_result != 0:
                        logger.error(f"Gemini CLI failed with return code {poll_result}")
                        if stderr:
                            logger.error(f"Error: {stderr}")
                    break
                
                # 检查是否超时
                if time.time() - start_time > max_wait_time:
                    logger.warning("Gemini CLI timeout, terminating process...")
                    process.terminate()
                    time.sleep(2)
                    if process.poll() is None:
                        process.kill()
                    break
                
                # 检查文件生成进度
                try:
                    current_files = list(code_dir.rglob("*"))
                    file_count = len([f for f in current_files if f.is_file()])
                    
                    if file_count > last_file_count:
                        logger.info(f"Progress: {file_count} files generated")
                        last_file_count = file_count
                        no_progress_count = 0
                    else:
                        no_progress_count += 1
                        
                    # 检查是否生成了关键文件
                    key_files = [
                        "requirements.txt",
                        "src/main.py",
                        "src/models",
                        "src/schemas",
                        "src/api"
                    ]
                    
                    key_files_found = 0
                    for key_file in key_files:
                        if any(str(key_file) in str(f) for f in current_files):
                            key_files_found += 1
                    
                    # 如果关键文件都已生成且一段时间没有新文件，可能已完成
                    if key_files_found >= len(key_files) - 1 and no_progress_count >= max_no_progress:
                        logger.info(f"No new files generated for {no_progress_count * check_interval} seconds, assuming completion")
                        process.terminate()
                        time.sleep(2)
                        if process.poll() is None:
                            process.kill()
                        break
                        
                except Exception as e:
                    logger.warning(f"Error checking files: {e}")
                
                # 等待下一次检查
                time.sleep(check_interval)
            
            # 最终检查生成的文件
            generated_files = list(code_dir.rglob("*"))
            file_count = len([f for f in generated_files if f.is_file()])
            
            if file_count > 0:
                logger.info(f"Successfully generated {file_count} files")
                
                # 列出生成的主要文件
                py_files = [f for f in generated_files if f.suffix == ".py"]
                logger.info(f"Generated {len(py_files)} Python files")
                
                return True
            else:
                logger.error("No files were generated")
                return False
                
        except Exception as e:
            logger.error(f"Failed to generate code with Gemini CLI: {e}")
            return False
    
    def _run_tests_and_fix(self, code_dir: Path) -> Dict[str, Any]:
        """运行测试并自动修复错误"""
        results = {
            "lint": {"passed": False, "fixed": False},
            "tests": {"passed": False, "fixed": False}
        }
        
        try:
            # 1. 运行 lint 检查
            if self.config.auto_fix_lint:
                logger.info("Running lint checks...")
                lint_passed, lint_errors = self._run_lint(code_dir)
                results["lint"]["passed"] = lint_passed
                
                if not lint_passed and lint_errors:
                    logger.info("Fixing lint errors...")
                    if self._fix_with_gemini(code_dir, lint_errors, "lint"):
                        results["lint"]["fixed"] = True
                        # 重新检查
                        lint_passed, _ = self._run_lint(code_dir)
                        results["lint"]["passed"] = lint_passed
            
            # 2. 运行单元测试
            if self.config.auto_fix_tests:
                logger.info("Running unit tests...")
                tests_passed, test_errors = self._run_tests(code_dir)
                results["tests"]["passed"] = tests_passed
                
                if not tests_passed and test_errors:
                    logger.info("Fixing test failures...")
                    if self._fix_with_gemini(code_dir, test_errors, "pytest"):
                        results["tests"]["fixed"] = True
                        # 重新运行测试
                        tests_passed, _ = self._run_tests(code_dir)
                        results["tests"]["passed"] = tests_passed
            
        except Exception as e:
            logger.error(f"Error during test/fix phase: {e}")
        
        return results
    
    def _run_lint(self, code_dir: Path) -> Tuple[bool, Optional[str]]:
        """运行 lint 检查"""
        try:
            result = subprocess.run(
                ["flake8", "--max-line-length=120", "."],
                capture_output=True,
                text=True,
                cwd=code_dir
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stdout
                
        except FileNotFoundError:
            logger.warning("flake8 not found, skipping lint check")
            return True, None
    
    def _run_tests(self, code_dir: Path) -> Tuple[bool, Optional[str]]:
        """运行单元测试"""
        try:
            # 查找测试文件
            test_dir = code_dir / "tests"
            if not test_dir.exists():
                logger.warning("No tests directory found")
                return True, None
            
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--no-cov", "-p", "no:warnings"],
                capture_output=True,
                text=True,
                cwd=code_dir
            )
            
            if result.returncode == 0:
                return True, None
            else:
                error_output = result.stdout + "\n" + result.stderr
                return False, error_output
                
        except FileNotFoundError:
            logger.warning("pytest not found, skipping tests")
            return True, None
    
    def _fix_with_gemini(self, code_dir: Path, error_msg: str, error_type: str) -> bool:
        """使用 Gemini CLI 修复错误"""
        try:
            # 准备环境变量
            env = os.environ.copy()
            if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
                del env["GOOGLE_API_KEY"]
            
            # 构建修复提示
            if error_type == "lint":
                prompt = f"""在当前目录中有 Python 代码需要修复 lint 错误。

错误信息：
{error_msg}

请执行以下步骤：
1. 根据错误信息找到对应的文件和行号
2. 修复所有报告的问题：
   - E501 (line too long): 将长行拆分到多行
   - F841 (unused variable): 删除未使用的变量或使用它
   - F821 (undefined name): 定义缺失的变量或导入
   - 其他 flake8 错误按照 PEP 8 规范修复
3. 确保修复后代码仍然能正常工作
4. 修改文件后，再次运行 flake8 确认没有错误"""
            
            elif error_type == "pytest":
                prompt = f"""运行 pytest 失败，错误信息：
{error_msg}

请：
1. 仔细分析错误原因
2. 如果缺少依赖（如 email_validator），更新 requirements.txt
3. 如果是代码错误，修复相关文件
4. 如果是测试错误，修复测试文件
5. 确保所有修复符合最佳实践
6. 重新运行 pytest 确保所有测试通过

注意：
- 使用最新的库语法
- 确保所有导入路径正确
- 保持代码的可读性和可维护性"""
            
            else:
                prompt = f"修复以下错误：\n{error_msg}"
            
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            
            # 调用 Gemini CLI
            result = subprocess.run(
                [self.gemini_cli_path, "-m", model, "-p", prompt, "-y"],
                capture_output=True,
                text=True,
                env=env,
                cwd=code_dir,
                timeout=300  # 5分钟超时
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to fix with Gemini CLI: {e}")
            return False
    
    def _get_framework_for_platform(self) -> str:
        """获取平台对应的框架"""
        platform_frameworks = {
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "spring": "Spring Boot",
            "express": "Express.js",
            "rails": "Ruby on Rails"
        }
        return platform_frameworks.get(self.config.target_platform.lower(), "FastAPI")
    
    def _get_orm_for_platform(self) -> str:
        """获取平台对应的 ORM"""
        platform_orms = {
            "fastapi": "SQLAlchemy 2.0",
            "django": "Django ORM",
            "flask": "SQLAlchemy 2.0",
            "spring": "JPA/Hibernate",
            "express": "Sequelize or TypeORM",
            "rails": "Active Record"
        }
        return platform_orms.get(self.config.target_platform.lower(), "SQLAlchemy")
    
    def _get_validation_lib_for_platform(self) -> str:
        """获取平台对应的验证库"""
        platform_validators = {
            "fastapi": "Pydantic v2",
            "django": "Django Forms/Serializers",
            "flask": "Marshmallow or Pydantic",
            "spring": "Bean Validation",
            "express": "Joi or Yup",
            "rails": "Active Model Validations"
        }
        return platform_validators.get(self.config.target_platform.lower(), "Pydantic")
    
    def _get_test_framework_for_platform(self) -> str:
        """获取平台对应的测试框架"""
        platform_tests = {
            "fastapi": "pytest",
            "django": "Django TestCase + pytest",
            "flask": "pytest",
            "spring": "JUnit 5",
            "express": "Jest or Mocha",
            "rails": "RSpec"
        }
        return platform_tests.get(self.config.target_platform.lower(), "pytest")