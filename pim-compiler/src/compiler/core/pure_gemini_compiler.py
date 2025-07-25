"""
纯 Gemini CLI 编译器实现 - 不依赖其他 LLM
"""
import os
import subprocess
import shutil
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from collections import namedtuple

# 加载环境变量
load_dotenv()

from ..config import CompilerConfig
from utils.logger import get_logger
from .error_pattern_cache import ErrorPatternCache
from .incremental_fixer import IncrementalFixer
from .prompts import (
    PSM_GENERATION_PROMPT,
    CODE_GENERATION_PROMPT,
    TEST_FIX_PROMPT,
    FIX_HISTORY_APPEND,
    LINT_FIX_MANY_ERRORS_PROMPT,
    LINT_FIX_FEW_ERRORS_PROMPT,
    STARTUP_FIX_PROMPT,
    INCREMENTAL_FIX_PROMPT,
    FILE_SPECIFIC_FIX_PROMPT,
    API_ERROR_PATTERNS,
    CRITICAL_LINT_ERROR_CODES,
    ERROR_TYPE_MAPPING,
    PLATFORM_FRAMEWORKS,
    PLATFORM_ORMS,
    PLATFORM_VALIDATORS,
    PLATFORM_TEST_FRAMEWORKS
)

# 不再需要导入独立的 PSM 生成函数，直接使用 Gemini CLI

logger = get_logger(__name__)

# 定义命令结果类型
CommandResult = namedtuple('CommandResult', ['returncode', 'stdout', 'stderr'])


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
    app_results: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, int]] = None
    message: Optional[str] = None


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
        self.error_cache = ErrorPatternCache()
        self.use_incremental_fix = True  # 启用增量修复
        
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
            
            # 项目根目录就是 generated/{project_name}
            code_dir = work_dir / "generated" / pim_file.stem
            if code_dir.exists():
                shutil.rmtree(code_dir)
            code_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制 PIM 文件到项目根目录
            pim_copy = code_dir / pim_file.name
            shutil.copy2(pim_file, pim_copy)
            
            # 复制知识库文件到项目根目录
            # 首先尝试从pim-compiler目录查找
            knowledge_file = Path(__file__).parent.parent.parent / "GEMINI_KNOWLEDGE.md"
            if not knowledge_file.exists():
                # 如果不存在，尝试从当前工作目录查找
                knowledge_file = Path.cwd() / "GEMINI_KNOWLEDGE.md"
            
            if knowledge_file.exists():
                shutil.copy2(knowledge_file, code_dir / "GEMINI_KNOWLEDGE.md")
                logger.info(f"Copied knowledge file to {code_dir / 'GEMINI_KNOWLEDGE.md'}")
            else:
                logger.warning(f"Knowledge file not found at {knowledge_file}")
            
            # 步骤 1: 使用 Gemini CLI 生成 PSM，直接放在项目根目录
            logger.info("Step 1: Generating PSM with Gemini CLI...")
            psm_file = code_dir / f"{pim_file.stem}_psm.md"
            psm_start = time.time()
            
            success = self._generate_psm(pim_copy, psm_file, code_dir)
            if not success:
                return CompilationResult(
                    success=False,
                    pim_file=pim_file,
                    error="Failed to generate PSM"
                )
            
            psm_time = time.time() - psm_start
            logger.info(f"PSM generated in {psm_time:.2f} seconds")
            
            # 不再创建 GEMINI.md 文件，改为在提示词中包含修复指南
            
            # 步骤 2: 使用 Gemini CLI 生成代码
            logger.info("Step 2: Generating code with Gemini CLI...")
            code_start = time.time()
            
            success = self._generate_code(psm_file, code_dir, code_dir)
            if not success:
                return CompilationResult(
                    success=False,
                    pim_file=pim_file,
                    psm_file=psm_file,
                    error="Failed to generate code"
                )
            
            code_time = time.time() - code_start
            logger.info(f"Code generated in {code_time:.2f} seconds")
            
            # 统计生成的文件（排除虚拟环境）
            all_files = list(code_dir.rglob("*"))
            file_count = len([f for f in all_files if f.is_file() and "venv" not in str(f) and "__pycache__" not in str(f)])
            py_files = [f for f in all_files if f.suffix == ".py" and f.is_file() and "venv" not in str(f)]
            
            statistics = {
                "total_files": file_count,
                "python_files": len(py_files),
                "psm_generation_time": int(psm_time),
                "code_generation_time": int(code_time)
            }
            
            # 步骤 3: 运行测试和修复（如果启用）
            test_results = None
            test_failed = False
            if self.config.auto_test:
                logger.info("Step 3: Running tests and auto-fixing...")
                test_results = self._run_tests_and_fix(code_dir)
                
                # 检查测试是否通过
                if test_results and self.config.fail_on_test_failure:
                    tests_info = test_results.get("tests", {})
                    if not tests_info.get("passed", False):
                        test_failed = True
                        logger.error("Tests failed and fail_on_test_failure is True")
                        return CompilationResult(
                            success=False,
                            pim_file=pim_file,
                            psm_file=psm_file,
                            code_dir=code_dir,
                            test_results=test_results,
                            error=f"Tests failed after {tests_info.get('attempts', 0)} attempts. {tests_info.get('final_error', 'Unit tests did not pass.')}"
                        )
            
            # 步骤 4: 运行应用程序
            app_results = None
            if self.config.auto_test and not test_failed:  # 只有在测试通过时才运行应用
                logger.info("Step 4: Starting application...")
                app_results = self._run_application(code_dir)
                
                # 步骤 5: 测试 REST 端点
                if app_results and app_results.get("success") and app_results.get("port"):
                    logger.info("Step 5: Testing REST endpoints...")
                    rest_results = self._test_rest_endpoints(code_dir, app_results["port"])
                    # 转换为标准格式以便后续处理
                    app_results["rest_tests"] = {
                        "passed": rest_results.get("endpoints_passed", 0),
                        "failed": rest_results.get("endpoints_tested", 0) - rest_results.get("endpoints_passed", 0),
                        "total": rest_results.get("endpoints_tested", 0),
                        "success": rest_results.get("success", False),
                        "details": rest_results.get("test_details", [])
                    }
                else:
                    logger.warning("Skipping REST endpoint tests - application not running")
            
            # 计算总编译时间
            compilation_time = (datetime.now() - start_time).total_seconds()
            
            # 判断编译是否真正成功
            compilation_success = True
            success_message = "Compilation completed successfully"
            
            # 检查测试结果
            if test_results:
                tests_info = test_results.get("tests", {})
                if not tests_info.get("passed", False):
                    compilation_success = False
                    success_message = "Compilation completed with test failures"
            
            # 检查应用启动结果
            if app_results and not app_results.get("success", False):
                compilation_success = False
                success_message = "Compilation completed but application failed to start"
            
            # 检查REST端点测试结果
            if app_results and app_results.get("rest_tests"):
                rest_tests = app_results["rest_tests"]
                total_tests = rest_tests.get("total", 0)
                passed_tests = rest_tests.get("passed", 0)
                failed_tests = rest_tests.get("failed", 0)
                
                # 确保total正确计算
                if total_tests == 0 and (passed_tests > 0 or failed_tests > 0):
                    total_tests = passed_tests + failed_tests
                    rest_tests["total"] = total_tests
                
                if total_tests > 0:
                    pass_rate = passed_tests / total_tests
                    if pass_rate < self.config.min_test_pass_rate:
                        compilation_success = False
                        success_message = f"Compilation completed but REST tests pass rate ({pass_rate:.1%}) below threshold ({self.config.min_test_pass_rate:.1%})"
            
            if compilation_success:
                logger.info(f"{success_message} in {compilation_time:.2f}s")
            else:
                logger.warning(f"{success_message} in {compilation_time:.2f}s")
            
            logger.info(f"Generated {file_count} files ({len(py_files)} Python files)")
            
            return CompilationResult(
                success=compilation_success,
                pim_file=pim_file,
                psm_file=psm_file,
                code_dir=code_dir,
                compilation_time=compilation_time,
                test_results=test_results,
                app_results=app_results,
                statistics=statistics,
                message=success_message
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
        logger.info(f"Generating PSM from {pim_file.name} using Gemini CLI")
        
        platform = self.config.target_platform
        framework = self._get_framework_for_platform()
        
        # 确保 PIM 文件存在
        if not pim_file.exists():
            logger.error(f"PIM file not found: {pim_file}")
            return False
        
        # 将 PIM 文件复制到工作目录，确保 Gemini 可以访问
        work_pim_file = work_dir / pim_file.name
        try:
            # 只有当源文件和目标文件不同时才复制
            if pim_file.resolve() != work_pim_file.resolve():
                shutil.copy2(pim_file, work_pim_file)
                logger.info(f"Copied PIM file to work directory: {work_pim_file}")
            else:
                logger.info(f"PIM file already in work directory: {work_pim_file}")
        except Exception as e:
            logger.error(f"Failed to copy PIM file to work directory: {e}")
            return False
        
        prompt = PSM_GENERATION_PROMPT.format(
            pim_file=work_pim_file.name,
            platform=platform,
            psm_file=psm_file.name,
            framework=framework,
            orm=self._get_orm_for_platform(),
            validation_lib=self._get_validation_lib_for_platform()
        )
        
        # 重试机制：最多尝试3次
        max_attempts = 3
        success = False
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"PSM generation attempt {attempt}/{max_attempts}")
            
            # 执行 Gemini CLI
            success = self._execute_gemini_cli(prompt, work_dir, timeout=300)  # 5分钟超时
            
            # 检查 PSM 文件是否生成
            if success and psm_file.exists():
                logger.info(f"PSM file generated successfully on attempt {attempt}")
                break
            elif success and not psm_file.exists():
                # 命令成功但文件未创建，可能在其他位置
                logger.warning(f"Command succeeded but PSM file not found at expected location (attempt {attempt})")
                # 这里会在后续的代码中搜索文件
                break
            else:
                logger.warning(f"PSM generation failed on attempt {attempt}")
                if attempt < max_attempts:
                    logger.info(f"Waiting 5 seconds before retry...")
                    time.sleep(5)
        
        logger.info(f"PSM generation result: {success}")
        logger.info(f"Expected PSM file: {psm_file}")
        logger.info(f"PSM file exists: {psm_file.exists()}")
        
        # 检查PSM文件是否被创建
        if success and not psm_file.exists():
            logger.warning("PSM file not created at expected location")
            # 检查最常见的备选位置
            alt_psm = work_dir / f"{pim_file.stem}_psm_psm.md"
            if alt_psm.exists():
                logger.info(f"Found PSM file at {alt_psm}, moving to {psm_file}")
                shutil.move(str(alt_psm), str(psm_file))
                return True
            
            logger.error("PSM file was not created")
            return False
            
        return success
    
    def _generate_code(self, psm_file: Path, code_dir: Path, work_dir: Path) -> bool:
        """使用 Gemini CLI 生成代码"""
        logger.info(f"Generating code from {psm_file.name} to {code_dir}")
        
        platform = self.config.target_platform
        framework = self._get_framework_for_platform()
        
        # 读取PSM文件内容
        try:
            psm_content = psm_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read PSM file: {e}")
            return False
        
        # 简化的提示词，只告诉 Gemini PSM 文件位置和知识库
        prompt = CODE_GENERATION_PROMPT.format(psm_file=psm_file.name)
        
        return self._execute_gemini_cli(prompt, work_dir, timeout=600, monitor_progress=True, target_dir=code_dir)
    
       
    def _execute_gemini_cli(self, prompt: str, work_dir: Path, timeout: int = 300, 
                            monitor_progress: bool = False, target_dir: Optional[Path] = None) -> bool:
        """执行 Gemini CLI 命令，支持 API 500 错误重试"""
        # API 500 错误重试配置
        max_retries = 3
        retry_delay = 5  # 初始延迟秒数
        
        for attempt in range(max_retries):
            try:
                # 准备环境变量
                env = os.environ.copy()
                # 处理 API key 冲突
                if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
                    del env["GOOGLE_API_KEY"]
                
                # 获取 Gemini 模型配置
                model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
                
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} for Gemini CLI")
                else:
                    logger.info(f"Executing Gemini CLI with model {model}")
                    logger.info(f"Gemini CLI working directory (absolute): {work_dir.resolve()}")
                
                if monitor_progress and target_dir:
                    # 使用进程监控
                    success, is_api_error = self._execute_with_monitoring(prompt, work_dir, env, model, timeout, target_dir)
                else:
                    # 简单执行，同时保存输出到日志
                    gemini_log_path = work_dir / "gemini.log"
                    logger.info(f"Gemini CLI output will be saved to: {gemini_log_path}")
                    
                    with open(gemini_log_path, "w", encoding="utf-8") as log_file:
                        # 先写入提示词
                        log_file.write(f"=== GEMINI CLI PROMPT ===\n{prompt}\n\n=== GEMINI CLI OUTPUT ===\n")
                        log_file.flush()
                        
                        # 直接使用提示词，不再判断长度
                        process = subprocess.Popen(
                            [self.gemini_cli_path, "-m", model, "-p", prompt, "-y"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            env=env,
                            cwd=work_dir
                        )
                        
                        output_lines = []
                        if process.stdout:
                            while True:
                                line = process.stdout.readline()
                                if not line and process.poll() is not None:
                                    break
                                if line:
                                    log_file.write(line)
                                    log_file.flush()
                                    output_lines.append(line.rstrip())
                        
                        # 等待进程结束，但要处理超时
                        try:
                            return_code = process.wait(timeout=timeout)
                        except subprocess.TimeoutExpired:
                            logger.warning(f"Gemini CLI timeout after {timeout} seconds, terminating...")
                            process.terminate()
                            try:
                                return_code = process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                logger.warning("Force killing Gemini CLI process...")
                                process.kill()
                                return_code = process.wait()
                            log_file.write(f"\n\n=== TIMEOUT: Process terminated after {timeout} seconds ===\n")
                        
                    # 构造结果对象以保持兼容性
                    result = CommandResult(
                        returncode=return_code,
                        stdout='\n'.join(output_lines),
                        stderr='' if return_code == 0 else '\n'.join(output_lines)
                    )
                    
                    if result.returncode != 0:
                        # 检查是否是 API 500 错误
                        is_api_error = self._is_api_500_error(result.stderr)
                        
                        if is_api_error and attempt < max_retries - 1:
                            logger.warning(f"Gemini API 500 error detected, will retry after {retry_delay} seconds")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # 指数退避
                            continue
                        
                        logger.error(f"Gemini CLI failed with return code {result.returncode}")
                        if result.stderr:
                            logger.error(f"Error: {result.stderr}")
                        return False
                    
                    success = True
                    is_api_error = False
                
                # 如果是 API 错误且还有重试机会
                if not success and is_api_error and attempt < max_retries - 1:
                    logger.warning(f"Gemini API error detected, will retry after {retry_delay} seconds")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    continue
                
                return success
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Gemini CLI timed out after {timeout} seconds")
                # 超时不重试
                return False
            except Exception as e:
                logger.error(f"Failed to execute Gemini CLI: {e}")
                # 其他异常不重试
                return False
        
        # 所有重试都失败
        logger.error(f"All {max_retries} attempts failed for Gemini CLI")
        return False
    
    
    def _is_api_500_error(self, error_text: str) -> bool:
        """检查错误文本是否包含 API 500 错误"""
        if not error_text:
            return False
        
        return any(pattern in error_text for pattern in API_ERROR_PATTERNS)
    
    def _execute_with_monitoring(self, prompt: str, work_dir: Path, env: dict, 
                                model: str, timeout: int, target_dir: Path) -> tuple[bool, bool]:
        """执行 Gemini CLI 并监控进度"""
        # 创建日志文件
        gemini_log_path = work_dir / "gemini.log"
        logger.info(f"Gemini CLI output will be saved to: {gemini_log_path}")
        
        with open(gemini_log_path, "w", encoding="utf-8") as log_file:
            # 先写入提示词
            log_file.write(f"=== GEMINI CLI PROMPT ===\n{prompt}\n\n=== GEMINI CLI OUTPUT ===\n")
            log_file.flush()
            
            # 直接使用提示词，不再判断长度
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
                    # 排除虚拟环境目录中的文件
                    file_count = len([f for f in current_files if f.is_file() and "venv" not in str(f) and "__pycache__" not in str(f)])
                    
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
        is_api_error = False
        
        # 首先检查是否是 API 500 错误
        if poll_result != 0 and stderr:
            is_api_error = self._is_api_500_error(stderr)
        
        # 检查目标目录和工作目录
        all_generated_files = []
        
        # 1. 检查目标目录
        if target_dir.exists():
            target_files = list(target_dir.rglob("*"))
            # 排除虚拟环境和缓存目录
            all_generated_files.extend([f for f in target_files if f.is_file() and "venv" not in str(f) and "__pycache__" not in str(f)])
        
        # 2. 检查工作目录下的所有文件（排除已知的输入文件）
        work_files = []
        excluded_dirs = ["pim", "psm", ".git", "__pycache__", "venv", "env", ".venv"]
        for item in work_dir.iterdir():
            if item.is_file() and item.suffix in [".py", ".txt", ".md", ".toml", ".yml", ".yaml"]:
                work_files.append(item)
            elif item.is_dir() and item.name not in excluded_dirs:
                work_files.extend([f for f in item.rglob("*") if f.is_file()])
        
        # 合并文件列表
        all_generated_files.extend(work_files)
        
        file_count = len(all_generated_files)
        py_files = [f for f in all_generated_files if f.suffix == ".py"]
        
        # Log summary
        if file_count > 0:
            logger.info(f"Generated {file_count} files ({len(py_files)} Python files)")
            # 特别检查测试文件
            test_files = [f for f in all_generated_files if "test" in f.name.lower() or f.parent.name == "tests"]
            if test_files:
                logger.info(f"Found {len(test_files)} test files")
            
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
                                shutil.move(str(f), str(target_path))
                                logger.info(f"Moved {f.name} to {target_dir}")
                        except Exception as e:
                            logger.warning(f"Failed to move {f.name}: {e}")
        
        # Success if we have files AND the process didn't fail
        success = file_count > 0 and (poll_result == 0 if poll_result is not None else True)
        
        return success, is_api_error
    
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
    
    def _find_project_directory(self, code_dir: Path) -> Optional[Path]:
        """查找实际的项目目录
        
        Gemini CLI 可能会生成嵌套的项目结构，比如：
        - code_dir/
          - project-name/
            - tests/
            - app/
            - main.py
        
        或者直接在 code_dir 下生成：
        - code_dir/
          - tests/
          - app/
          - main.py
        """
        # 首先检查 code_dir 本身是否是项目目录
        if (code_dir / "tests").exists() or (code_dir / "app").exists() or (code_dir / "main.py").exists():
            return code_dir
        
        # 查找子目录中的项目
        for subdir in code_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                # 检查子目录是否包含项目结构
                if (subdir / "tests").exists() or (subdir / "app").exists() or (subdir / "main.py").exists():
                    return subdir
        
        # 如果找不到，返回 None
        return None
    
    def _run_tests_and_fix(self, code_dir: Path) -> Dict[str, Any]:
        """运行测试并自动修复错误（带反馈循环）"""
        results = {
            "lint": {"passed": False, "fixed": False, "attempts": 0},
            "tests": {"passed": False, "fixed": False, "attempts": 0, "errors": []},
            "total_attempts": 0,
            "max_attempts_reached": False
        }
        
        # 查找实际的项目目录（可能在子目录中）
        project_dir = self._find_project_directory(code_dir)
        if not project_dir:
            logger.warning(f"No valid project directory found in {code_dir}")
            project_dir = code_dir  # 回退到原始目录
        else:
            logger.info(f"Found project directory: {project_dir}")
        
        try:
            # 1. 运行 lint 检查（单次修复）
            if self.config.enable_lint:
                logger.info("Running lint checks...")
                lint_passed, lint_errors = self._run_lint(project_dir)
                results["lint"]["passed"] = lint_passed
                results["lint"]["attempts"] = 1
                
                if not lint_passed and lint_errors and self.config.auto_fix_lint and self.config.lint_fix_mode != "skip":
                    if self.config.lint_fix_mode == "critical":
                        # 只在有关键错误时才修复
                        critical_errors = self._filter_critical_lint_errors(lint_errors)
                        if critical_errors:
                            logger.info(f"Fixing {len(critical_errors.split(chr(10)))} critical lint errors...")
                            if self._fix_with_gemini(project_dir, critical_errors, "lint"):
                                results["lint"]["fixed"] = True
                                lint_passed, _ = self._run_lint(project_dir)
                                results["lint"]["passed"] = lint_passed
                        else:
                            logger.info("No critical lint errors found, skipping fix")
                            results["lint"]["passed"] = True  # 忽略非关键错误
                    else:  # "all" mode
                        logger.info("Fixing all lint errors...")
                        if self._fix_with_gemini(project_dir, lint_errors, "lint"):
                            results["lint"]["fixed"] = True
                            lint_passed, _ = self._run_lint(project_dir)
                            results["lint"]["passed"] = lint_passed
                elif not lint_passed and not self.config.auto_fix_lint:
                    logger.warning("Lint errors found but auto-fix is disabled")
            else:
                logger.info("Lint check is disabled, skipping...")
                results["lint"]["passed"] = True  # 跳过时认为通过
            
            # 2. 运行测试反馈循环（最多5次）
            if self.config.auto_fix_tests:
                test_results = self._run_test_feedback_loop(project_dir)
                results["tests"] = test_results
                results["total_attempts"] = test_results["attempts"]
                results["max_attempts_reached"] = test_results.get("max_attempts_reached", False)
            
        except Exception as e:
            logger.error(f"Error during test/fix phase: {e}")
            results["error"] = str(e)
        
        return results
    
    def _run_test_feedback_loop(self, code_dir: Path, max_attempts: int = 5) -> Dict[str, Any]:
        """运行测试反馈循环，使用增量修复策略"""
        result = {
            "passed": False,
            "fixed": False,
            "attempts": 0,
            "errors": [],
            "fix_history": [],
            "cache_stats": {}
        }
        
        # 如果启用增量修复，使用新策略
        if self.use_incremental_fix:
            return self._run_incremental_test_loop(code_dir, max_attempts)
        
        # 否则使用原有策略（保留兼容性）
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Test feedback loop - Attempt {attempt}/{max_attempts}")
            result["attempts"] = attempt
            
            # 运行测试
            logger.info("Running unit tests...")
            test_passed, test_errors = self._run_tests(code_dir)
            
            if test_passed:
                logger.info(f"Tests passed on attempt {attempt}")
                result["passed"] = True
                if attempt > 1:
                    result["fixed"] = True
                break
            
            # 记录错误
            error_info = {
                "attempt": attempt,
                "errors": test_errors,
                "timestamp": datetime.now().isoformat()
            }
            result["errors"].append(error_info)
            
            # 如果是最后一次尝试，不再修复
            if attempt >= max_attempts:
                logger.error(f"Test fixes failed after {max_attempts} attempts. Human intervention required.")
                result["max_attempts_reached"] = True
                result["final_error"] = f"测试修复失败，已尝试 {max_attempts} 次，需要人类介入"
                break
            
            # 分析错误并生成修复提示
            logger.info(f"Analyzing test failures (attempt {attempt})...")
            fix_prompt = self._generate_test_fix_prompt(test_errors or "", attempt, result["fix_history"])
            
            # 调用 Gemini 修复
            logger.info(f"Attempting to fix test failures...")
            fix_success = self._fix_with_gemini(code_dir, fix_prompt, "pytest")
            
            # 记录修复历史
            fix_info = {
                "attempt": attempt,
                "prompt_summary": fix_prompt[:200] + "...",
                "success": fix_success,
                "timestamp": datetime.now().isoformat()
            }
            result["fix_history"].append(fix_info)
            
            if not fix_success:
                logger.warning(f"Fix attempt {attempt} failed, will retry...")
                # 继续下一次循环
        
        return result
    
    def _generate_test_fix_prompt(self, test_errors: str, attempt: int, fix_history: list) -> str:
        """生成测试修复提示词，包含错误上下文和历史信息"""
        # 分析错误类型
        error_types = self._categorize_errors(test_errors)
        
        prompt = TEST_FIX_PROMPT.format(
            attempt=attempt,
            errors=test_errors,
            error_types=', '.join(error_types)
        )
        
        # 如果有修复历史，添加上下文
        if fix_history:
            history_text = ""
            for fix in fix_history[-2:]:  # 只包含最近2次历史
                history_text += f"- 第 {fix['attempt']} 次尝试: {'成功' if fix['success'] else '失败'}\n"
            prompt += FIX_HISTORY_APPEND.format(fix_history=history_text)
        
        return prompt
    
    def _categorize_errors(self, error_output: str) -> list:
        """分类错误类型"""
        error_types = []
        
        for error_key, error_name in ERROR_TYPE_MAPPING.items():
            if error_key in error_output:
                if error_name not in error_types:
                    error_types.append(error_name)
        
        if not error_types:
            error_types.append("未知错误")
        
        return error_types
    
    def _run_incremental_test_loop(self, code_dir: Path, max_attempts: int = 5) -> Dict[str, Any]:
        """使用增量修复策略运行测试循环"""
        result = {
            "passed": False,
            "fixed": False,
            "attempts": 0,
            "errors": [],
            "fix_history": [],
            "cache_stats": {},
            "incremental_fixes": []
        }
        
        fixer = IncrementalFixer(code_dir)
        total_fixes = 0
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Incremental test loop - Attempt {attempt}/{max_attempts}")
            result["attempts"] = attempt
            
            # 运行完整测试
            logger.info("Running full test suite...")
            test_passed, test_errors = self._run_tests(code_dir)
            
            if test_passed:
                logger.info(f"All tests passed on attempt {attempt}")
                result["passed"] = True
                if total_fixes > 0:
                    result["fixed"] = True
                break
            
            # 解析错误
            errors = fixer.parse_pytest_output(test_errors or "")
            logger.info(f"Parsed {len(errors)} test errors from pytest output")
            
            # 记录部分pytest输出以便调试
            if test_errors and len(test_errors) > 0:
                logger.info(f"Pytest output preview (first 500 chars): {test_errors[:500]}...")
            
            file_errors = fixer.group_errors_by_file(errors)
            logger.info(f"Grouped errors into {len(file_errors)} files")
            
            files_to_fix = fixer.prioritize_files(file_errors)
            
            logger.info(f"Found {len(files_to_fix)} files to fix")
            if len(files_to_fix) == 0 and len(errors) > 0:
                logger.warning(f"Found {len(errors)} test errors but could not map them to source files")
                # 记录一些错误细节以帮助调试
                for i, error in enumerate(errors[:3]):  # 只记录前3个
                    logger.info(f"Error {i+1}: {error.file_path}::{error.test_name} - {error.error_type}")
            
            # 创建修复批次
            batches = fixer.create_fix_batch(files_to_fix, batch_size=2)
            
            for batch_idx, batch in enumerate(batches):
                logger.info(f"Processing batch {batch_idx + 1}/{len(batches)}")
                
                for file in batch:
                    # 先检查缓存
                    cached_fix = None
                    pattern_match = None
                    
                    for error in file.errors:
                        # 检查错误模式
                        pattern_match = self.error_cache.find_pattern_match(error.full_traceback)
                        if pattern_match:
                            logger.info(f"Found pattern match: {pattern_match.description}")
                            break
                        
                        # 检查缓存的修复
                        cached_fix = self.error_cache.find_cached_fix(
                            error.full_traceback, 
                            str(file.path)
                        )
                        if cached_fix:
                            logger.info(f"Found cached fix for {file.path}")
                            break
                    
                    # 应用修复
                    fix_applied = False
                    
                    if pattern_match and pattern_match.success_rate > 0.5:
                        # 使用模式模板快速修复
                        logger.info(f"Applying pattern template for {file.path}")
                        prompt = INCREMENTAL_FIX_PROMPT.format(
                            fix_template=pattern_match.fix_template,
                            file_path=file.path,
                            error_message=file.errors[0].error_message
                        )
                        fix_applied = self._fix_with_gemini(code_dir, prompt, "pytest", timeout=60)
                        self.error_cache.update_pattern_success_rate(pattern_match, fix_applied)
                    
                    elif cached_fix:
                        # 应用缓存的修复
                        logger.info(f"Reusing cached fix for {file.path}")
                        # 这里简化处理，实际可以直接应用修复内容
                        fix_applied = True
                    
                    else:
                        # 生成新的修复
                        logger.info(f"Generating new fix for {file.path}")
                        prompt = fixer.generate_file_specific_prompt(file)
                        fix_applied = self._fix_with_gemini(code_dir, prompt, "pytest", timeout=120)
                        
                        # 缓存结果
                        if fix_applied:
                            self.error_cache.add_fix_result(
                                file.errors[0].full_traceback,
                                str(file.path),
                                "fix_applied",  # 简化，实际应记录具体修复内容
                                True
                            )
                    
                    if fix_applied:
                        total_fixes += 1
                        
                        # 运行受影响的测试验证修复
                        test_file = f"tests/{file.path.stem.replace('_', '')}_test.py"
                        if (code_dir / test_file).exists():
                            quick_pass, _ = fixer.run_single_file_test(test_file)
                            logger.info(f"Quick test for {test_file}: {'PASSED' if quick_pass else 'FAILED'}")
                    
                    result["incremental_fixes"].append({
                        "file": str(file.path),
                        "errors": len(file.errors),
                        "fixed": fix_applied,
                        "method": "pattern" if pattern_match else ("cached" if cached_fix else "generated")
                    })
            
            # 如果没有修复任何文件，避免死循环
            if total_fixes == 0 and attempt > 1:
                logger.warning("No fixes applied in this attempt, stopping")
                break
        
        # 添加缓存统计
        result["cache_stats"] = self.error_cache.get_stats()
        
        return result
    
    def _filter_critical_lint_errors(self, lint_errors: str) -> str:
        """过滤出关键的 lint 错误"""
        critical_lines = []
        for line in lint_errors.strip().split('\n'):
            # 检查是否包含关键错误代码
            for error_code in CRITICAL_LINT_ERROR_CODES:
                if f" {error_code}" in line:
                    critical_lines.append(line)
                    break
        
        return '\n'.join(critical_lines)
    
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
        # 查找实际的项目目录
        project_dir = self._find_project_directory(code_dir)
        if project_dir and project_dir != code_dir:
            logger.info(f"Found project directory: {project_dir}")
            code_dir = project_dir
        
        try:
            test_dir = code_dir / "tests"
            if not test_dir.exists():
                logger.warning(f"No tests directory found at: {test_dir}")
                # 列出 code_dir 的内容以帮助调试
                logger.info("Listing code_dir contents:")
                for item in code_dir.iterdir():
                    logger.info(f"  - {item.name} (dir={item.is_dir()})")
                return True, None
            
            logger.info(f"Found tests directory: {test_dir}")
            logger.info("Running pytest...")
            
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "--no-header", "-s"],
                capture_output=True,
                text=True,
                cwd=code_dir
            )
            
            error_output = result.stdout + "\n" + result.stderr if result.returncode != 0 else None
            
            # 检查是否是 pytest 启动失败
            if result.returncode != 0 and error_output:
                if "ImportError: cannot import name 'FixtureDef' from 'pytest'" in error_output:
                    logger.warning("pytest version compatibility issue detected")
                    # 尝试修复 pytest 版本问题
                    if self._fix_pytest_version(code_dir):
                        logger.info("Fixed pytest version, retrying tests...")
                        # 重新运行测试
                        result = subprocess.run(
                            ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "--no-header", "-s"],
                            capture_output=True,
                            text=True,
                            cwd=code_dir
                        )
                        error_output = result.stdout + "\n" + result.stderr if result.returncode != 0 else None
                elif "ModuleNotFoundError" in error_output and "pytest" in error_output:
                    logger.warning("pytest not installed or broken")
                    # 标记为环境问题，让上层处理
                    return False, "ENVIRONMENT_ERROR: pytest installation issue"
            
            if result.returncode == 0:
                logger.info("Tests passed successfully")
                logger.info(f"Test output: {result.stdout[:200]}..." if result.stdout else "No stdout")
            else:
                logger.warning(f"Tests failed with return code: {result.returncode}")
                logger.info(f"Test stdout length: {len(result.stdout) if result.stdout else 0}")
                logger.info(f"Test stderr length: {len(result.stderr) if result.stderr else 0}")
                if error_output:
                    logger.info(f"Combined error output length: {len(error_output)}")
            
            return result.returncode == 0, error_output
                
        except FileNotFoundError:
            logger.warning("pytest not found, skipping tests")
            return True, None
    
    def _fix_pytest_version(self, code_dir: Path) -> bool:
        """修复 pytest 版本兼容性问题"""
        try:
            requirements_file = code_dir / "requirements.txt"
            if not requirements_file.exists():
                logger.error("requirements.txt not found")
                return False
            
            # 读取当前内容
            content = requirements_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 查找并更新 pytest 版本
            updated = False
            new_lines = []
            for line in lines:
                if line.strip().startswith('pytest'):
                    # 确保使用兼容的版本
                    new_lines.append('pytest==7.4.3')
                    updated = True
                else:
                    new_lines.append(line)
            
            # 如果没有找到 pytest，添加它
            if not updated:
                # 在其他测试依赖之前添加
                for i, line in enumerate(new_lines):
                    if 'httpx' in line or 'test' in line.lower():
                        new_lines.insert(i, 'pytest==7.4.3')
                        updated = True
                        break
                if not updated:
                    new_lines.append('pytest==7.4.3')
            
            # 写回文件
            requirements_file.write_text('\n'.join(new_lines), encoding='utf-8')
            logger.info("Updated pytest version in requirements.txt")
            
            # 尝试安装正确版本的 pytest
            logger.info("Installing correct pytest version...")
            result = subprocess.run(
                ["pip", "install", "pytest==7.4.3", "--force-reinstall"],
                capture_output=True,
                text=True,
                cwd=code_dir
            )
            
            if result.returncode == 0:
                logger.info("Successfully installed pytest 7.4.3")
                return True
            else:
                logger.error(f"Failed to install pytest: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error fixing pytest version: {e}")
            return False
    
    def _fix_with_gemini(self, code_dir: Path, error_msg: str, error_type: str, timeout: Optional[int] = None) -> bool:
        """使用 Gemini CLI 修复错误
        
        注意：Gemini CLI 会自动读取项目根目录的 GEMINI.md 文件获取修复指南
        """
        if error_type == "lint":
            # 分析错误数量，如果太多就只修复最重要的
            error_lines = error_msg.strip().split('\n')
            error_count = len(error_lines)
            
            if error_count > 20:
                logger.warning(f"Too many lint errors ({error_count}), will fix only critical ones")
                prompt = LINT_FIX_MANY_ERRORS_PROMPT.format(
                    errors=chr(10).join(error_lines[:20]),
                    remaining_count=error_count - 20
                )
            else:
                prompt = LINT_FIX_FEW_ERRORS_PROMPT.format(errors=error_msg)
        elif error_type == "startup":
            # error_type == "startup" 时，error_msg 已经是完整的修复提示词
            prompt = error_msg
        else:
            # error_type == "pytest" 时，error_msg 已经是完整的修复提示词
            prompt = error_msg
        
        # 使用传入的超时时间，如果没有则使用默认值
        if timeout is None:
            timeout = 600 if error_type == "lint" else 300
        return self._execute_gemini_cli(prompt, code_dir, timeout=timeout)
    
    def _get_framework_for_platform(self) -> str:
        """获取平台对应的框架"""
        return PLATFORM_FRAMEWORKS.get(self.config.target_platform.lower(), "FastAPI")
    
    def _get_orm_for_platform(self) -> str:
        """获取平台对应的 ORM"""
        return PLATFORM_ORMS.get(self.config.target_platform.lower(), "SQLAlchemy")
    
    def _get_validation_lib_for_platform(self) -> str:
        """获取平台对应的验证库"""
        return PLATFORM_VALIDATORS.get(self.config.target_platform.lower(), "Pydantic")
    
    def _get_test_framework_for_platform(self) -> str:
        """获取平台对应的测试框架"""
        return PLATFORM_TEST_FRAMEWORKS.get(self.config.target_platform.lower(), "pytest")
    
    
    def _run_application(self, code_dir: Path) -> Dict[str, Any]:
        """运行生成的应用程序，包含修复反馈循环"""
        logger.info("Starting application with fix feedback loop...")
        result = {
            "success": False,
            "port": None,
            "errors": [],
            "attempts": 0,
            "fix_history": [],
            "final_process": None
        }
        
        # 查找实际的项目目录
        project_dir = self._find_project_directory(code_dir)
        if not project_dir:
            project_dir = code_dir
        
        # 启动反馈循环，最多10次
        max_attempts = 10
        port = 8100
        result["port"] = port
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Application startup attempt {attempt}/{max_attempts}")
            result["attempts"] = attempt
            
            # 尝试启动应用
            startup_result = self._try_start_application(project_dir, port)
            
            if startup_result["success"]:
                logger.info(f"Application started successfully on attempt {attempt}")
                result["success"] = True
                result["final_process"] = startup_result.get("process")
                if attempt > 1:
                    result["fixed"] = True
                break
            
            # 记录错误
            error_info = {
                "attempt": attempt,
                "errors": startup_result["errors"],
                "log_content": startup_result.get("log_content", ""),
                "timestamp": datetime.now().isoformat()
            }
            result["errors"].append(error_info)
            
            # 如果是最后一次尝试，不再修复
            if attempt >= max_attempts:
                logger.error(f"Application startup failed after {max_attempts} attempts")
                result["max_attempts_reached"] = True
                result["final_error"] = f"应用启动失败，已尝试 {max_attempts} 次，需要人工介入"
                break
            
            # 分析错误并生成修复提示
            logger.info(f"Analyzing startup failures (attempt {attempt})...")
            fix_prompt = self._generate_startup_fix_prompt(
                startup_result["errors"], 
                startup_result.get("log_content", ""),
                attempt,
                result["fix_history"],
                project_dir
            )
            
            # 调用 Gemini 修复
            logger.info(f"Attempting to fix startup issues...")
            fix_success = self._fix_with_gemini(project_dir, fix_prompt, "startup")
            
            # 记录修复历史
            fix_info = {
                "attempt": attempt,
                "prompt_summary": fix_prompt[:200] + "...",
                "success": fix_success,
                "timestamp": datetime.now().isoformat()
            }
            result["fix_history"].append(fix_info)
            
            if not fix_success:
                logger.warning(f"Fix attempt {attempt} failed, will retry...")
            
            # 等待一下再重试
            time.sleep(2)
        
        return result
    
    def _test_rest_endpoints(self, code_dir: Path, port: int = 8100) -> Dict[str, Any]:
        """测试 REST API 端点"""
        logger.info("Testing REST endpoints...")
        result = {
            "success": False,
            "endpoints_tested": 0,
            "endpoints_passed": 0,
            "test_details": []
        }
        
        # 查找实际的项目目录
        project_dir = self._find_project_directory(code_dir) or code_dir
        
        try:
            # 基础测试端点
            test_cases = [
                {
                    "name": "Root endpoint",
                    "method": "GET",
                    "url": f"http://localhost:{port}/",
                    "expected_status": [200, 301, 302]
                },
                {
                    "name": "API docs",
                    "method": "GET",
                    "url": f"http://localhost:{port}/docs",
                    "expected_status": [200]
                }
            ]
            
            # 添加 OpenAPI 路径测试
            # FastAPI 默认的 OpenAPI 路径是 /openapi.json
            test_cases.append({
                "name": "OpenAPI schema",
                "method": "GET",
                "url": f"http://localhost:{port}/openapi.json",
                "expected_status": [200]
            })
            
            
            # 执行测试
            for test in test_cases:
                test_result = {
                    "name": test["name"],
                    "method": test["method"],
                    "url": test["url"],
                    "success": False,
                    "status_code": None,
                    "error": None
                }
                
                logger.info(f"Testing: {test['method']} {test['url']}")
                result["endpoints_tested"] += 1
                
                try:
                    # 使用 --noproxy localhost 避免代理问题
                    cmd = f"curl --noproxy localhost -X {test['method']} -w '\\n%{{http_code}}' -s {test['url']}"
                    response = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if response.returncode == 0:
                        lines = response.stdout.strip().split('\n')
                        status_code = int(lines[-1]) if lines else 0
                        test_result["status_code"] = status_code
                        
                        if status_code in test["expected_status"]:
                            test_result["success"] = True
                            result["endpoints_passed"] += 1
                            logger.info(f"  ✓ Passed with status {status_code}")
                        else:
                            test_result["error"] = f"Unexpected status code: {status_code}"
                            logger.warning(f"  ✗ Failed with status {status_code}")
                    else:
                        test_result["error"] = f"curl failed: {response.stderr}"
                        logger.error(f"  ✗ curl failed: {response.stderr}")
                        
                except subprocess.TimeoutExpired:
                    test_result["error"] = "Request timeout"
                    logger.error(f"  ✗ Request timeout")
                except Exception as e:
                    test_result["error"] = str(e)
                    logger.error(f"  ✗ Error: {e}")
                
                result["test_details"].append(test_result)
            
            # 判断整体成功
            result["success"] = result["endpoints_passed"] > 0 and \
                               result["endpoints_passed"] >= result["endpoints_tested"] * 0.5  # 至少50%通过
            
            logger.info(f"REST endpoint testing completed: {result['endpoints_passed']}/{result['endpoints_tested']} passed")
            
        except Exception as e:
            logger.error(f"Failed to test REST endpoints: {e}")
            result["error"] = str(e)
        
        return result
    
    def _try_start_application(self, project_dir: Path, port: int) -> Dict[str, Any]:
        """尝试启动应用程序"""
        result = {
            "success": False,
            "errors": [],
            "log_content": "",
            "process": None
        }
        
        try:
            # 检查是否是 FastAPI 项目
            if self.config.target_platform.lower() == "fastapi":
                # 检查 main.py 或 app/main.py
                main_files = [
                    project_dir / "main.py",
                    project_dir / "app" / "main.py",
                    project_dir / "src" / "main.py",
                ]
                
                main_file = None
                for f in main_files:
                    if f.exists():
                        main_file = f
                        break
                
                if not main_file:
                    result["errors"].append("Cannot find main.py file")
                    return result
                
                # 构建启动命令
                app_module = str(main_file.relative_to(project_dir)).replace("/", ".").replace(".py", "")
                
                # 使用显式的 Python 解释器路径来避免 shell 兼容性问题
                venv_python = project_dir / "venv" / "bin" / "python"
                if venv_python.exists():
                    cmd = f"{venv_python} -m uvicorn {app_module}:app --host 0.0.0.0 --port {port}"
                else:
                    # 回退到系统 Python
                    cmd = f"python -m uvicorn {app_module}:app --host 0.0.0.0 --port {port}"
                
                logger.info(f"Starting FastAPI app: {cmd}")
                
                # 启动应用，将输出重定向到日志文件
                log_file = project_dir / "server.log"
                with open(log_file, "w") as f:
                    process = subprocess.Popen(cmd.split(), 
                                               cwd=str(project_dir),
                                               stdout=f,
                                               stderr=subprocess.STDOUT)
                
                result["process"] = process
                
                # 等待应用启动
                time.sleep(5)
                
                # 检查进程是否还在运行
                if process.poll() is not None:
                    # 进程已经退出，读取日志
                    with open(log_file, "r") as f:
                        log_content = f.read()
                    result["log_content"] = log_content
                    result["errors"].append("Application process exited prematurely")
                    if log_content:
                        result["errors"].append(f"Server log:\n{log_content}")
                    return result
                
                # 检查应用是否启动成功
                try:
                    response = subprocess.run(
                        f"curl --noproxy localhost http://localhost:{port}/",
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if response.returncode == 0:
                        logger.info(f"Application started successfully on port {port}")
                        result["success"] = True
                    else:
                        # 读取服务器日志
                        with open(log_file, "r") as f:
                            log_content = f.read()
                        result["log_content"] = log_content
                        result["errors"].append(f"Failed to connect: {response.stderr}")
                        if log_content:
                            result["errors"].append(f"Server log:\n{log_content}")
                        
                        # 终止进程
                        if process.poll() is None:
                            process.terminate()
                            time.sleep(1)
                            if process.poll() is None:
                                process.kill()
                except Exception as e:
                    result["errors"].append(f"Failed to check application status: {e}")
                    # 读取日志
                    try:
                        with open(log_file, "r") as f:
                            result["log_content"] = f.read()
                    except:
                        pass
            else:
                result["errors"].append(f"Platform not supported: {self.config.target_platform}")
                
        except Exception as e:
            result["errors"].append(f"Failed to start application: {e}")
        
        return result
    
    def _generate_startup_fix_prompt(self, errors: List[str], log_content: str, 
                                    attempt: int, fix_history: List[Dict], project_dir: Path) -> str:
        """生成应用启动修复提示词"""
        # 分析错误类型
        error_text = "\n".join(errors) + "\n" + log_content
        error_types = self._categorize_errors(error_text)
        
        prompt = STARTUP_FIX_PROMPT.format(
            attempt=attempt,
            error_text=error_text,
            error_types=', '.join(error_types),
            project_dir=project_dir.resolve()
        )
        
        # 如果有修复历史，添加上下文
        if fix_history:
            history_text = ""
            for fix in fix_history[-2:]:  # 只包含最近2次历史
                history_text += f"- 第 {fix['attempt']} 次尝试: {'成功' if fix['success'] else '失败'}\n"
            prompt += FIX_HISTORY_APPEND.format(fix_history=history_text)
        
        return prompt