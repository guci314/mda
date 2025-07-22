"""Base compiler abstract class for LLM-based PIM compilation"""

import os
import json
import yaml
import hashlib
import subprocess
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime
import logging

from .compiler_config import CompilerConfig


class CompilationResult:
    """编译结果"""
    def __init__(self, success: bool, psm_file: Optional[Path] = None, 
                 errors: Optional[List[str]] = None, warnings: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.success = success
        self.psm_file = psm_file
        self.errors = errors or []
        self.warnings = warnings or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "psm_file": str(self.psm_file) if self.psm_file else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class BaseCompiler(ABC):
    """基础编译器抽象类 - 使用 LLM 处理 Markdown"""
    
    def __init__(self, config: CompilerConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 设置日志级别
        if config.debug:
            self.logger.setLevel(logging.DEBUG)
        elif config.verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)
        
        # 初始化缓存
        self._cache = {}
        if config.enable_cache:
            self._load_cache()
    
    def compile(self, pim_file: Path) -> CompilationResult:
        """编译PIM文件到PSM
        
        使用 LLM 将 PIM Markdown 转换为 PSM Markdown
        """
        self.logger.info(f"开始编译: {pim_file}")
        
        try:
            # 检查缓存
            if self.config.enable_cache:
                cached_result = self._check_cache(pim_file)
                if cached_result:
                    self.logger.info("使用缓存的编译结果")
                    return cached_result
            
            # 1. 读取 PIM Markdown 文件
            pim_content = self._read_file(pim_file)
            if not pim_content:
                return CompilationResult(False, errors=["无法读取PIM文件"])
            
            # 2. 使用 LLM 转换 PIM 到 PSM
            psm_content = self._transform_pim_to_psm(pim_content, pim_file)
            if not psm_content:
                return CompilationResult(False, errors=["PIM到PSM转换失败"])
            
            # 3. 保存 PSM 文件
            psm_file = self._save_psm(psm_content, pim_file)
            
            # 4. 生成代码（如果需要）
            code_files = []
            if self.config.generate_code:
                code_files = self._generate_code_from_psm(psm_content, psm_file)
                
                # 5. 对生成的代码进行 lint 检查和修复
                if code_files and self.config.enable_lint:
                    self._lint_and_fix_code(code_files)
                    
                    # 6. 运行单元测试
                    if self.config.run_tests:
                        test_files = [f for f in code_files if 'test_' in Path(f).name]
                        if test_files:
                            self._run_and_fix_tests(test_files)
            
            # 创建成功结果
            result = CompilationResult(
                success=True,
                psm_file=psm_file,
                metadata={
                    "pim_file": str(pim_file),
                    "platform": self.config.target_platform,
                    "code_files": code_files,
                    "compile_time": (datetime.now() - datetime.now()).total_seconds()
                }
            )
            
            # 缓存结果
            if self.config.enable_cache:
                self._update_cache(pim_file, result)
            
            self.logger.info(f"编译成功: {psm_file}")
            return result
            
        except Exception as e:
            self.logger.error(f"编译失败: {e}", exc_info=True)
            return CompilationResult(False, errors=[str(e)])
    
    def _read_file(self, file_path: Path) -> Optional[str]:
        """读取文件内容"""
        if not file_path.exists():
            self.logger.error(f"文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"读取文件失败: {e}")
            return None
    
    @abstractmethod
    def _transform_pim_to_psm(self, pim_content: str, source_file: Path) -> Optional[str]:
        """使用 LLM 将 PIM 转换为 PSM（子类实现）"""
        pass
    
    @abstractmethod
    def _generate_code_from_psm(self, psm_content: str, psm_file: Path) -> List[str]:
        """从 PSM 生成代码（子类实现）"""
        pass
    
    def _save_psm(self, psm_content: str, source_file: Path) -> Path:
        """保存PSM文件"""
        # 生成输出文件名
        output_name = f"{source_file.stem}_{self.config.target_platform}.psm.md"
        # output_dir 在 CompilerConfig.__post_init__ 中会设置默认值
        output_dir = self.config.output_dir or Path("./output")
        output_file = output_dir / output_name
        
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(psm_content)
        
        self.logger.debug(f"PSM文件已保存: {output_file}")
        return output_file
    
    # 缓存相关方法
    def _get_cache_key(self, pim_file: Path) -> str:
        """生成缓存键"""
        # 使用文件路径、修改时间和目标平台生成缓存键
        mtime = pim_file.stat().st_mtime
        key_str = f"{pim_file}:{mtime}:{self.config.target_platform}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _check_cache(self, pim_file: Path) -> Optional[CompilationResult]:
        """检查缓存"""
        cache_key = self._get_cache_key(pim_file)
        
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            # 检查PSM文件是否仍然存在
            if cached["psm_file"] and Path(cached["psm_file"]).exists():
                return CompilationResult(
                    success=True,
                    psm_file=Path(cached["psm_file"]),
                    metadata=cached.get("metadata", {})
                )
        
        return None
    
    def _update_cache(self, pim_file: Path, result: CompilationResult):
        """更新缓存"""
        if result.success and result.psm_file:
            cache_key = self._get_cache_key(pim_file)
            self._cache[cache_key] = {
                "psm_file": str(result.psm_file),
                "metadata": result.metadata,
                "timestamp": result.timestamp.isoformat()
            }
            self._save_cache()
    
    def _load_cache(self):
        """加载缓存"""
        cache_file = self.config.cache_dir / "compiler_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self._cache = json.load(f)
            except Exception as e:
                self.logger.warning(f"加载缓存失败: {e}")
                self._cache = {}
    
    def _save_cache(self):
        """保存缓存"""
        cache_file = self.config.cache_dir / "compiler_cache.json"
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            self.logger.warning(f"保存缓存失败: {e}")
    
    def _lint_and_fix_code(self, code_files: List[str]):
        """对生成的代码进行 lint 检查并自动修复"""
        for file_path in code_files:
            file_ext = Path(file_path).suffix
            
            # 根据文件扩展名选择 linter
            if file_ext == '.py':
                self._lint_python(file_path)
            elif file_ext in ['.js', '.ts']:
                self._lint_javascript(file_path)
            elif file_ext == '.java':
                self._lint_java(file_path)
    
    def _lint_python(self, file_path: str):
        """Python 代码 lint 检查和修复"""
        try:
            # 先用 black 格式化
            subprocess.run(['black', file_path], capture_output=True, check=False)
            
            # 使用 flake8 检查
            result = subprocess.run(
                ['flake8', file_path], 
                capture_output=True, 
                text=True,
                check=False
            )
            
            if result.returncode != 0 and result.stdout:
                self.logger.warning(f"Lint 错误: {result.stdout}")
                # 调用 Gemini CLI 修复
                if self.config.auto_fix_lint:
                    if self._fix_with_gemini(file_path, result.stdout, 'python lint'):
                        # 重新运行 lint 检查
                        result = subprocess.run(
                            ['flake8', file_path], 
                            capture_output=True, 
                            text=True,
                            check=False
                        )
                        if result.returncode == 0:
                            self.logger.info(f"Lint 修复成功: {file_path}")
                        else:
                            self.logger.warning(f"Lint 仍有错误: {result.stdout}")
                
        except FileNotFoundError:
            self.logger.warning("未安装 black 或 flake8，跳过 Python lint")
    
    def _lint_javascript(self, file_path: str):
        """JavaScript/TypeScript 代码 lint 检查和修复"""
        try:
            # 使用 eslint 检查和自动修复
            subprocess.run(
                ['eslint', '--fix', file_path], 
                capture_output=True,
                check=False
            )
        except FileNotFoundError:
            self.logger.warning("未安装 eslint，跳过 JavaScript lint")
    
    def _lint_java(self, file_path: str):
        """Java 代码 lint 检查"""
        # Java 的 lint 工具配置较复杂，这里仅作示例
        self.logger.info(f"Java lint 检查: {file_path}")
    
    def _run_and_fix_tests(self, test_files: List[str]):
        """运行单元测试并修复失败的测试"""
        for test_file in test_files:
            file_ext = Path(test_file).suffix
            
            if file_ext == '.py':
                self._run_python_tests(test_file)
            elif file_ext in ['.js', '.ts']:
                self._run_javascript_tests(test_file)
            elif file_ext == '.java':
                self._run_java_tests(test_file)
    
    def _run_python_tests(self, test_file: str):
        """运行 Python 测试"""
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', test_file, '-v'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.logger.warning(f"测试失败: {result.stdout}")
                # 调用 Gemini CLI 修复测试
                if self.config.auto_fix_tests:
                    if self._fix_with_gemini(test_file, result.stdout, 'pytest failures'):
                        # 重新运行测试
                        result = subprocess.run(
                            ['python', '-m', 'pytest', test_file, '-v'],
                            capture_output=True,
                            text=True,
                            check=False
                        )
                        if result.returncode == 0:
                            self.logger.info(f"测试修复成功: {test_file}")
                        else:
                            self.logger.warning(f"测试仍有失败: {result.stdout}")
                
        except FileNotFoundError:
            self.logger.warning("未安装 pytest，跳过测试运行")
    
    def _run_javascript_tests(self, test_file: str):
        """运行 JavaScript 测试"""
        try:
            subprocess.run(['npm', 'test', test_file], check=False)
        except FileNotFoundError:
            self.logger.warning("未安装 npm，跳过 JavaScript 测试")
    
    def _run_java_tests(self, test_file: str):
        """运行 Java 测试"""
        self.logger.info(f"运行 Java 测试: {test_file}")
    
    def _fix_with_gemini(self, file_path: str, error_msg: str, error_type: str):
        """使用 Gemini CLI 修复代码错误 - 在项目目录中执行"""
        try:
            self.logger.info(f"使用 Gemini 修复 {error_type} 错误")
            
            # 获取项目目录（文件所在的目录）
            project_dir = Path(file_path).parent
            relative_file = Path(file_path).name
            
            self.logger.debug(f"项目目录: {project_dir}")
            
            # 根据错误类型构建更智能的提示
            if error_type == "python lint":
                fix_prompt = f"""在当前目录中有 Python 代码需要修复 lint 错误。

错误信息：
{error_msg}

请执行以下步骤：
1. 根据错误信息找到对应的文件和行号
2. 修复所有报告的问题：
   - E501 (line too long): 将长行拆分到多行
   - F841 (unused variable): 删除未使用的变量或使用它
   - F821 (undefined name): 定义缺失的变量或导入
3. 对于 Pydantic 的 'regex' 参数，改为 'pattern'
4. 修改文件后，再次运行 flake8 确认没有错误"""
                
            elif error_type == "pytest failures":
                    fix_prompt = f"""运行 pytest 失败，错误信息：

{error_msg}

请：
1. 分析错误原因
2. 如果缺少依赖（如 email_validator），在 requirements.txt 中添加
3. 如果是代码错误，修复相关文件
4. 如果是测试错误，修复测试文件
5. 重新运行 pytest 确保所有测试通过

注意：
- 对于 Pydantic，使用 'pattern' 而不是 'regex'
- 对于 SQLAlchemy，从 sqlalchemy.orm 导入 declarative_base
- 确保所有导入路径正确"""
            else:
                fix_prompt = f"""修复以下错误：

{error_msg}

请分析错误并修复相关文件。"""
            
            # 设置环境变量
            env = os.environ.copy()
                
            # 设置代理（如果配置了）
            proxy_host = os.getenv("PROXY_HOST", "127.0.0.1")
            proxy_port = os.getenv("PROXY_PORT", "7890")
            if proxy_host and proxy_port:
                proxy_url = f"http://{proxy_host}:{proxy_port}"
                env["HTTP_PROXY"] = proxy_url
                env["HTTPS_PROXY"] = proxy_url
            
            # API key 设置
            if "GOOGLE_AI_STUDIO_KEY" in env and "GEMINI_API_KEY" not in env:
                env["GEMINI_API_KEY"] = env["GOOGLE_AI_STUDIO_KEY"]
            
            # 获取 Gemini CLI 路径
            gemini_cli_path = "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini"
            if not os.path.exists(gemini_cli_path):
                gemini_cli_path = "gemini"
            
            # 获取模型
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            
            # 构建命令
            cmd = [gemini_cli_path, "-m", model, "-p", fix_prompt, "-y"]  # 添加 -y 自动确认
            
            self.logger.info(f"在 {project_dir} 中调用 Gemini CLI")
            
            # 执行命令（使用 cwd 参数指定工作目录）
            result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=project_dir,  # 在项目目录中执行
                    check=False,
                    timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                self.logger.info(f"Gemini 修复完成")
                # Gemini 直接修改文件，不需要我们处理输出
                return True
            else:
                self.logger.warning(f"Gemini 修复失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Gemini CLI 超时（5分钟）")
            return False
        except FileNotFoundError:
            self.logger.warning("未安装 Gemini CLI，跳过自动修复")
            return False
        except Exception as e:
            self.logger.error(f"Gemini 修复出错: {e}")
            return False