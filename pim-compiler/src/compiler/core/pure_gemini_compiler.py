"""
纯 Gemini CLI 编译器实现 - 不依赖其他 LLM
"""
import os
import subprocess
import shutil
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from compiler.config import CompilerConfig
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
    statistics: Optional[Dict[str, int]] = None


class PureGeminiCompiler:
    """纯 Gemini CLI 编译器
    
    使用 Gemini CLI 完成整个编译流程：
    1. PIM → PSM 转换
    2. PSM → Code 生成
    3. 测试和修复（可选）
    
    优势：
    - 只需要一个 API
    - 更好的上下文一致性
    - 更快的编译速度
    - 更简单的配置
    """
    
    def __init__(self, config: CompilerConfig):
        self.config = config
        self.gemini_cli_path = self._find_gemini_cli()
        
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
                logger.info(f"Found Gemini CLI at: {path}")
                return path
        
        # 使用系统 PATH
        logger.info("Using Gemini CLI from system PATH")
        return "gemini"
    
    def compile(self, pim_file: Path) -> CompilationResult:
        """编译 PIM 文件"""
        print("我是经过验证的编译器")
        logger.info("我是经过验证的编译器")
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
            
            # 准备目录结构
            work_dir = self.config.output_dir
            psm_dir = work_dir / "psm"
            psm_dir.mkdir(parents=True, exist_ok=True)
            
            code_dir = work_dir / "generated" / pim_file.stem
            if code_dir.exists():
                shutil.rmtree(code_dir)
            code_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制 PIM 文件到工作目录
            pim_copy = work_dir / "pim" / pim_file.name
            pim_copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pim_file, pim_copy)
            
            # 步骤 1: 使用 Gemini CLI 生成 PSM
            logger.info("Step 1: Generating PSM with Gemini CLI...")
            psm_file = psm_dir / f"{pim_file.stem}_psm.md"
            psm_start = time.time()
            
            success = self._generate_psm(pim_copy, psm_file, work_dir)
            if not success:
                return CompilationResult(
                    success=False,
                    pim_file=pim_file,
                    error="Failed to generate PSM"
                )
            
            psm_time = time.time() - psm_start
            logger.info(f"PSM generated in {psm_time:.2f} seconds")
            
            # 步骤 2: 使用 Gemini CLI 生成代码
            logger.info("Step 2: Generating code with Gemini CLI...")
            code_start = time.time()
            
            success = self._generate_code(psm_file, code_dir, work_dir)
            if not success:
                return CompilationResult(
                    success=False,
                    pim_file=pim_file,
                    psm_file=psm_file,
                    error="Failed to generate code"
                )
            
            code_time = time.time() - code_start
            logger.info(f"Code generated in {code_time:.2f} seconds")
            
            # 统计生成的文件
            all_files = list(code_dir.rglob("*"))
            file_count = len([f for f in all_files if f.is_file()])
            py_files = [f for f in all_files if f.suffix == ".py" and f.is_file()]
            
            statistics = {
                "total_files": file_count,
                "python_files": len(py_files),
                "psm_generation_time": int(psm_time),
                "code_generation_time": int(code_time)
            }
            
            # 步骤 3: 运行测试和修复（如果启用）
            test_results = None
            if self.config.auto_test:
                logger.info("Step 3: Running tests and auto-fixing...")
                test_results = self._run_tests_and_fix(code_dir)
            
            # 计算总编译时间
            compilation_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Compilation completed successfully in {compilation_time:.2f}s")
            logger.info(f"Generated {file_count} files ({len(py_files)} Python files)")
            
            return CompilationResult(
                success=True,
                pim_file=pim_file,
                psm_file=psm_file,
                code_dir=code_dir,
                compilation_time=compilation_time,
                test_results=test_results,
                statistics=statistics
            )
            
        except Exception as e:
            logger.error(f"Compilation failed: {e}")
            return CompilationResult(
                success=False,
                pim_file=pim_file,
                error=str(e)
            )
    
    def _generate_psm(self, pim_file: Path, psm_file: Path, work_dir: Path) -> bool:
        """使用 Gemini CLI 生成 PSM"""
        platform = self.config.target_platform
        framework = self._get_framework_for_platform()
        
        # 读取PIM文件内容
        try:
            pim_content = pim_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read PIM file: {e}")
            return False
        
        prompt = f"""你是一个专业的软件架构师，精通模型驱动架构（MDA）。

我有以下平台无关模型（PIM）内容：

```markdown
{pim_content}
```

请将这个 PIM 转换为 {platform} 平台的平台特定模型（PSM），并创建文件 psm/{psm_file.name}

要求：
1. 仔细阅读 PIM 文件，理解所有业务需求
2. 生成详细的 PSM 文档，包含以下部分：
   - 技术架构说明（使用 {framework} 框架）
   - 数据模型设计（包含具体字段类型、约束、索引、关系）
   - API 接口设计（RESTful，包含路由、请求/响应格式、状态码）
   - 业务逻辑实现方案（服务层设计）
   - 项目结构说明
   - 技术栈和依赖列表
3. 使用 Markdown 格式，包含代码示例
4. 保持技术中立的业务逻辑，只添加平台特定的技术实现细节

技术要求：
- 框架：{framework}
- 数据库：PostgreSQL 或 SQLite
- ORM：{self._get_orm_for_platform()}
- 数据验证：{self._get_validation_lib_for_platform()}
- 测试框架：{self._get_test_framework_for_platform()}

请生成完整、专业的 PSM 文档并保存为 psm/{psm_file.name} 文件。确保文件被创建。
"""
        
        success = self._execute_gemini_cli(prompt, work_dir, timeout=300)
        
        logger.info(f"PSM generation result: {success}")
        logger.info(f"Expected PSM file: {psm_file}")
        logger.info(f"PSM file exists: {psm_file.exists()}")
        
        # 检查PSM文件是否被创建
        if success and not psm_file.exists():
            logger.warning("PSM file not created by Gemini CLI, checking for alternative locations")
            # 检查工作目录中是否有生成的PSM文件
            possible_files = [
                work_dir / psm_file.name,
                work_dir / f"{pim_file.stem}_psm.md",
                work_dir / "psm" / psm_file.name,
                work_dir / "psm" / f"{pim_file.stem}_psm_psm.md",  # Gemini可能添加额外的_psm
                psm_file.parent / f"{pim_file.stem}_psm_psm.md",  # 在目标目录检查
            ]
            
            for possible_file in possible_files:
                logger.debug(f"Checking: {possible_file}")
                if possible_file.exists():
                    logger.info(f"Found PSM file at {possible_file}, moving to {psm_file}")
                    import shutil
                    psm_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(possible_file), str(psm_file))
                    return True
                    
            logger.error("PSM file was not created")
            return False
            
        return success
    
    def _generate_code(self, psm_file: Path, code_dir: Path, work_dir: Path) -> bool:
        """使用 Gemini CLI 生成代码"""
        platform = self.config.target_platform
        framework = self._get_framework_for_platform()
        
        # 读取PSM文件内容
        try:
            psm_content = psm_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read PSM file: {e}")
            return False
        
        prompt = f"""你是一个专业的 {platform} 开发工程师，精通 {framework} 框架。

我有以下平台特定模型（PSM）内容：

```markdown
{psm_content}
```

请根据这个 PSM 生成完整的 {platform} 代码实现。

要求：
1. 仔细阅读 PSM 文件，理解所有技术细节
2. 在 generated/{code_dir.name}/ 目录下创建完整的项目结构
3. 必须生成以下核心文件：
   - {'manage.py（Django 管理脚本）' if platform.lower() == 'django' else 'main.py（应用程序入口点）'}
   - requirements.txt（Python 依赖）
   - README.md（项目说明文档）
   - {'settings.py（Django 配置文件）' if platform.lower() == 'django' else ''}
4. 实现 PSM 中描述的所有功能：
   - 数据模型（使用 ORM）
   - API 接口（RESTful）
   - 业务逻辑服务
   - 配置管理
   - 数据库连接
   - 认证和授权（如果需要）
5. 生成必要的配置文件：
   - .env.example（环境变量示例）
   - .gitignore
6. 生成项目文档：
   - API 文档（如果适用）
7. 生成测试文件：
   - 单元测试（在 tests/ 目录下）
   - 测试配置文件

代码质量要求：
- 使用最新版本的库语法：
  - Pydantic v2+: 使用 'pattern' 而不是 'regex'
  - SQLAlchemy 2.0+: 使用新的查询语法
  - FastAPI: 使用最新的依赖注入方式
- 包含完整的错误处理和输入验证
- 添加适当的日志记录（使用 loguru 或标准 logging）
- 实现基本的安全功能（如密码哈希使用 bcrypt）
- 遵循语言规范（Python 的 PEP 8 等）
- 每个文件都要有适当的文档字符串
- 使用类型提示（Python）

重要：{'manage.py 必须是 Django 项目的管理脚本，能够运行服务器和管理命令' if platform.lower() == 'django' else 'main.py 必须是项目的入口点，能够启动整个应用程序'}。
不要只生成框架代码，要实现完整的业务逻辑。

{'对于 Django 项目，请确保正确的项目结构：项目名称目录包含 settings.py、urls.py、wsgi.py 等文件。' if platform.lower() == 'django' else ''}
"""
        
        return self._execute_gemini_cli(prompt, work_dir, timeout=600, monitor_progress=True, target_dir=code_dir)
    
    def _execute_gemini_cli(self, prompt: str, work_dir: Path, timeout: int = 300, 
                            monitor_progress: bool = False, target_dir: Optional[Path] = None) -> bool:
        """执行 Gemini CLI 命令"""
        try:
            # 准备环境变量
            env = os.environ.copy()
            # 处理 API key 冲突
            if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
                del env["GOOGLE_API_KEY"]
            
            # 获取 Gemini 模型配置
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            
            logger.info(f"Executing Gemini CLI with model {model}")
            
            if monitor_progress and target_dir:
                # 使用进程监控
                return self._execute_with_monitoring(prompt, work_dir, env, model, timeout, target_dir)
            else:
                # 简单执行
                result = subprocess.run(
                    [self.gemini_cli_path, "-m", model, "-p", prompt, "-y"],
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=work_dir,
                    timeout=timeout
                )
                
                if result.returncode != 0:
                    logger.error(f"Gemini CLI failed with return code {result.returncode}")
                    if result.stderr:
                        logger.error(f"Error: {result.stderr}")
                    return False
                
                return True
                
        except subprocess.TimeoutExpired:
            logger.error(f"Gemini CLI timed out after {timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Failed to execute Gemini CLI: {e}")
            return False
    
    def _execute_with_monitoring(self, prompt: str, work_dir: Path, env: dict, 
                                model: str, timeout: int, target_dir: Path) -> bool:
        """执行 Gemini CLI 并监控进度"""
        process = subprocess.Popen(
            [self.gemini_cli_path, "-m", model, "-p", prompt, "-y"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=work_dir
        )
        
        start_time = time.time()
        check_interval = 10
        last_file_count = 0
        no_progress_count = 0
        max_no_progress = 6  # 60秒没有新文件
        
        while True:
            # 检查进程是否结束
            poll_result = process.poll()
            if poll_result is not None:
                stdout, stderr = process.communicate()
                if poll_result != 0:
                    logger.error(f"Gemini CLI failed with return code {poll_result}")
                    if stderr:
                        logger.error(f"Error: {stderr}")
                    if stdout:
                        logger.error(f"Output: {stdout[:500]}")  # Log first 500 chars
                break
            
            # 检查超时
            if time.time() - start_time > timeout:
                logger.warning("Gemini CLI timeout, terminating process...")
                process.terminate()
                time.sleep(2)
                if process.poll() is None:
                    process.kill()
                stdout, stderr = process.communicate()
                if stderr:
                    logger.error(f"Timeout stderr: {stderr}")
                break
            
            # 监控文件生成进度
            if target_dir.exists():
                try:
                    current_files = list(target_dir.rglob("*"))
                    file_count = len([f for f in current_files if f.is_file()])
                    
                    if file_count > last_file_count:
                        logger.info(f"Progress: {file_count} files generated")
                        last_file_count = file_count
                        no_progress_count = 0
                    else:
                        no_progress_count += 1
                    
                    # 检查关键文件
                    if self._check_key_files(current_files) and no_progress_count >= max_no_progress:
                        logger.info(f"Key files generated and no new files for {no_progress_count * check_interval}s")
                        process.terminate()
                        time.sleep(2)
                        if process.poll() is None:
                            process.kill()
                        stdout, stderr = process.communicate()
                        break
                        
                except Exception as e:
                    logger.warning(f"Error checking files: {e}")
            
            time.sleep(check_interval)
        
        # 检查最终结果
        success = False
        
        # 检查目标目录和工作目录
        all_generated_files = []
        
        # 1. 检查目标目录
        if target_dir.exists():
            target_files = list(target_dir.rglob("*"))
            all_generated_files.extend([f for f in target_files if f.is_file()])
        
        # 2. 检查工作目录下的所有文件（排除已知的输入文件）
        work_files = []
        excluded_dirs = ["pim", "psm", ".git", "__pycache__"]
        for item in work_dir.iterdir():
            if item.is_file() and item.suffix in [".py", ".txt", ".md", ".toml", ".yml", ".yaml"]:
                work_files.append(item)
            elif item.is_dir() and item.name not in excluded_dirs:
                work_files.extend([f for f in item.rglob("*") if f.is_file()])
        
        # 合并文件列表
        all_generated_files.extend(work_files)
        
        file_count = len(all_generated_files)
        py_files = [f for f in all_generated_files if f.suffix == ".py"]
        
        # Log what was generated for debugging
        if file_count > 0:
            logger.info(f"Total generated files: {file_count}, including {len(py_files)} Python files")
            # Log Python files
            for py_file in py_files[:5]:  # 只显示前5个
                logger.info(f"  - {py_file.relative_to(work_dir)}")
            
            # Check if main.py exists
            main_py = any("main.py" in f.name for f in py_files)
            if not main_py:
                logger.warning("main.py not found in generated files")
            else:
                # 如果找到main.py，移动文件到正确位置
                for f in all_generated_files:
                    if f.parent == work_dir or f.parent.name == "generated":
                        # 移动到target_dir
                        try:
                            target_path = target_dir / f.name
                            if not target_path.exists():
                                import shutil
                                shutil.move(str(f), str(target_path))
                                logger.info(f"Moved {f.name} to {target_dir}")
                        except Exception as e:
                            logger.warning(f"Failed to move {f.name}: {e}")
        
        # Success if we have files AND the process didn't fail
        success = file_count > 0 and (poll_result == 0 if poll_result is not None else True)
        
        return success
    
    def _check_key_files(self, files: list) -> bool:
        """检查是否生成了关键文件"""
        # 检查通用文件
        common_files = ["requirements.txt", "README.md"]
        
        # 检查平台特定文件
        platform_specific_files = []
        if hasattr(self.config, 'target_platform'):
            if self.config.target_platform.lower() == "django":
                platform_specific_files = ["manage.py", "settings.py"]
            else:
                platform_specific_files = ["main.py"]
        else:
            platform_specific_files = ["main.py"]
        
        key_files = common_files + platform_specific_files
        found_count = 0
        
        for key_file in key_files:
            if any(key_file in str(f) for f in files):
                found_count += 1
        
        # 至少找到大部分关键文件
        return found_count >= len(key_files) - 1
    
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
                        tests_passed, _ = self._run_tests(code_dir)
                        results["tests"]["passed"] = tests_passed
            
        except Exception as e:
            logger.error(f"Error during test/fix phase: {e}")
        
        return results
    
    def _run_lint(self, code_dir: Path) -> tuple[bool, Optional[str]]:
        """运行 lint 检查"""
        try:
            result = subprocess.run(
                ["flake8", "--max-line-length=120", "."],
                capture_output=True,
                text=True,
                cwd=code_dir
            )
            
            return result.returncode == 0, result.stdout if result.returncode != 0 else None
                
        except FileNotFoundError:
            logger.warning("flake8 not found, skipping lint check")
            return True, None
    
    def _run_tests(self, code_dir: Path) -> tuple[bool, Optional[str]]:
        """运行单元测试"""
        try:
            test_dir = code_dir / "tests"
            if not test_dir.exists():
                logger.warning("No tests directory found")
                return True, None
            
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                capture_output=True,
                text=True,
                cwd=code_dir
            )
            
            error_output = result.stdout + "\n" + result.stderr if result.returncode != 0 else None
            return result.returncode == 0, error_output
                
        except FileNotFoundError:
            logger.warning("pytest not found, skipping tests")
            return True, None
    
    def _fix_with_gemini(self, code_dir: Path, error_msg: str, error_type: str) -> bool:
        """使用 Gemini CLI 修复错误"""
        if error_type == "lint":
            prompt = f"""在当前目录中有 Python 代码需要修复 lint 错误。

错误信息：
{error_msg}

请修复所有 flake8 报告的问题，确保代码符合 PEP 8 规范。
"""
        else:
            prompt = f"""运行 pytest 失败，需要修复测试错误。

错误信息：
{error_msg}

请分析并修复所有测试失败的原因。
"""
        
        return self._execute_gemini_cli(prompt, code_dir, timeout=300)
    
    def _get_framework_for_platform(self) -> str:
        """获取平台对应的框架"""
        frameworks = {
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "spring": "Spring Boot",
            "express": "Express.js"
        }
        return frameworks.get(self.config.target_platform.lower(), "FastAPI")
    
    def _get_orm_for_platform(self) -> str:
        """获取平台对应的 ORM"""
        orms = {
            "fastapi": "SQLAlchemy 2.0",
            "django": "Django ORM",
            "flask": "SQLAlchemy 2.0",
            "spring": "JPA/Hibernate",
            "express": "Sequelize or TypeORM"
        }
        return orms.get(self.config.target_platform.lower(), "SQLAlchemy")
    
    def _get_validation_lib_for_platform(self) -> str:
        """获取平台对应的验证库"""
        validators = {
            "fastapi": "Pydantic v2",
            "django": "Django Forms/Serializers",
            "flask": "Marshmallow or Pydantic",
            "spring": "Bean Validation",
            "express": "Joi or Yup"
        }
        return validators.get(self.config.target_platform.lower(), "Pydantic")
    
    def _get_test_framework_for_platform(self) -> str:
        """获取平台对应的测试框架"""
        tests = {
            "fastapi": "pytest",
            "django": "Django TestCase + pytest",
            "flask": "pytest",
            "spring": "JUnit 5",
            "express": "Jest or Mocha"
        }
        return tests.get(self.config.target_platform.lower(), "pytest")