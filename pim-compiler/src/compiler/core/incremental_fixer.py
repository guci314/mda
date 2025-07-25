"""增量修复策略实现"""
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import subprocess
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TestError:
    """测试错误信息"""
    file_path: str
    test_name: str
    error_type: str
    error_message: str
    full_traceback: str
    line_number: Optional[int] = None


@dataclass
class FileToFix:
    """需要修复的文件"""
    path: Path
    errors: List[TestError]
    priority: int  # 修复优先级，越小越优先
    dependencies: List[str] = None  # 依赖的其他文件


class IncrementalFixer:
    """增量修复器"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.app_dir = project_dir / "app"
        
        # 文件优先级映射
        self.priority_map = {
            "config.py": 1,
            "enums.py": 2,
            "models": 3,  # 目录
            "schemas": 4,  # 目录
            "db": 5,      # 目录
            "crud": 6,    # 目录
            "services": 7, # 目录
            "api": 8,     # 目录
            "tests": 9    # 目录
        }
    
    def parse_pytest_output(self, error_output: str) -> List[TestError]:
        """解析pytest输出，提取错误信息"""
        errors = []
        
        logger.info(f"Starting to parse pytest output, length: {len(error_output)}")
        
        # 增强的解析模式，支持更多格式
        test_patterns = [
            r"(\S+\.py)::(\S+)\s+FAILED",  # 标准格式
            r"FAILED\s+(\S+\.py)::(\S+)",  # 另一种格式
            r"(\S+)::(\S+)\s+FAILED"       # 无.py扩展名
        ]
        
        error_patterns = [
            r"E\s+(\w+Error|AssertionError):\s+(.+)",  # 标准错误
            r">\s+(\w+Error|AssertionError):\s+(.+)",  # 另一种格式
            r"(\w+Error|AssertionError):\s+(.+)"       # 简单格式
        ]
        
        file_patterns = [
            r"(\S+\.py):(\d+):",           # 标准格式
            r"File \"(.+\.py)\", line (\d+)",  # Python traceback格式
            r"(\S+\.py):(\d+)\s+in"        # pytest in 格式
        ]
        
        lines = error_output.split('\n')
        logger.info(f"Pytest output has {len(lines)} lines")
        
        current_test = None
        current_file = None
        current_traceback = []
        
        for i, line in enumerate(lines):
            # 尝试所有测试模式
            test_match = None
            for pattern in test_patterns:
                test_match = re.search(pattern, line)
                if test_match:
                    break
            
            if test_match:
                logger.debug(f"Found FAILED test at line {i}: {line}")
                # 保存之前的错误
                if current_test:
                    self._save_current_error(errors, current_test, current_file, current_traceback)
                
                test_file = test_match.group(1)
                if not test_file.endswith('.py'):
                    test_file += '.py'
                
                current_test = TestError(
                    file_path=test_file,
                    test_name=test_match.group(2),
                    error_type="",
                    error_message="",
                    full_traceback=""
                )
                current_traceback = []
                continue
            
            # 尝试所有错误模式
            if current_test:
                for pattern in error_patterns:
                    error_match = re.search(pattern, line)
                    if error_match:
                        current_test.error_type = error_match.group(1)
                        current_test.error_message = error_match.group(2)
                        break
            
            # 尝试所有文件模式
            for pattern in file_patterns:
                file_match = re.search(pattern, line)
                if file_match:
                    current_file = file_match.group(1)
                    if current_test and not current_test.line_number:
                        try:
                            current_test.line_number = int(file_match.group(2))
                        except:
                            pass
                    break
            
            # 收集traceback
            if current_test and line.strip():
                current_traceback.append(line)
        
        # 保存最后一个错误
        if current_test:
            self._save_current_error(errors, current_test, current_file, current_traceback)
        
        logger.info(f"Parsed {len(errors)} errors from pytest output")
        return errors
    
    def _save_current_error(self, errors: List[TestError], test_error: TestError, 
                           error_file: str, traceback: List[str]):
        """保存当前错误信息"""
        if error_file:
            test_error.file_path = error_file
        test_error.full_traceback = '\n'.join(traceback)
        errors.append(test_error)
    
    def group_errors_by_file(self, errors: List[TestError]) -> Dict[str, List[TestError]]:
        """按文件分组错误"""
        file_errors = {}
        
        logger.info(f"Grouping {len(errors)} errors by file")
        
        for error in errors:
            file_path = error.file_path
            
            # 跳过测试文件本身的错误，关注被测试代码的错误
            if file_path.startswith("tests/"):
                logger.debug(f"Processing test file error: {file_path}")
                # 从traceback中提取实际出错的文件
                actual_file = self._extract_actual_error_file(error.full_traceback)
                if actual_file:
                    logger.debug(f"Extracted actual file from traceback: {actual_file}")
                    file_path = actual_file
                else:
                    # 尝试根据测试名称推断文件
                    inferred_file = self._infer_source_file_from_test(error.test_name, error.error_message)
                    if inferred_file:
                        logger.debug(f"Inferred file from test name: {inferred_file}")
                        file_path = inferred_file
                    else:
                        logger.debug(f"Could not determine source file for test: {error.test_name}")
                        continue
            
            if file_path not in file_errors:
                file_errors[file_path] = []
            file_errors[file_path].append(error)
        
        return file_errors
    
    def _extract_actual_error_file(self, traceback: str) -> Optional[str]:
        """从traceback中提取实际出错的源文件"""
        # 尝试多种模式
        patterns = [
            r"(app/\S+\.py):\d+:",  # 标准格式：app/file.py:123:
            r"(app/\S+\.py):\d+\s+in",  # pytest格式：app/file.py:123 in function
            r"File \"(app/\S+\.py)\"",  # 标准Python traceback格式
            r"(app/\S+\.py)\s+in\s+\w+",  # 另一种格式
            r"in\s+(app/\S+\.py)",  # in app/file.py
            r"-->?\s*(\d+\s+)?(app/\S+\.py)",  # --> 123 app/file.py
        ]
        
        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, traceback, re.MULTILINE)
            # 处理可能的元组匹配
            for match in matches:
                if isinstance(match, tuple):
                    # 选择非空的部分
                    file_path = next((m for m in match if m and 'app/' in m), None)
                    if file_path:
                        all_matches.append(file_path.strip())
                else:
                    all_matches.append(match.strip())
        
        # 过滤掉重复项，保持顺序
        seen = set()
        unique_matches = []
        for match in all_matches:
            if match not in seen:
                seen.add(match)
                unique_matches.append(match)
        
        # 返回最后一个匹配的app文件（通常是实际出错的地方）
        if unique_matches:
            logger.debug(f"Found {len(unique_matches)} potential error files: {unique_matches}")
            return unique_matches[-1]
        return None
    
    def _infer_source_file_from_test(self, test_name: str, error_message: str) -> Optional[str]:
        """根据测试名称和错误消息推断源文件"""
        # 特殊处理：如果是OpenAPI相关的测试失败
        if "openapi" in test_name.lower() or "docs" in test_name.lower():
            # OpenAPI配置通常在main.py中
            if (self.app_dir / "main.py").exists():
                return "app/main.py"
        
        # 从测试名称中提取实体名（如test_update_user -> user）
        entity_patterns = [
            r"test_(?:create|read|update|delete|get|list)_(\w+)",
            r"test_(\w+)_",
            r"(\w+)_test"
        ]
        
        entity_name = None
        for pattern in entity_patterns:
            match = re.search(pattern, test_name.lower())
            if match:
                entity_name = match.group(1)
                break
        
        if entity_name:
            # 根据错误类型优先级返回文件
            if "TypeError" in error_message or "got an unexpected keyword argument" in error_message:
                # 类型错误通常在CRUD或API层
                candidates = [
                    f"app/crud/crud_{entity_name}.py",
                    f"app/crud/{entity_name}_crud.py",
                    f"app/crud/{entity_name}.py",
                    f"app/api/v1/endpoints/{entity_name}s.py",
                    f"app/api/v1/endpoints/{entity_name}.py",
                ]
            elif "ValidationError" in error_message or "422" in error_message:
                # 验证错误通常在schema层
                candidates = [
                    f"app/schemas/{entity_name}.py",
                    f"app/models/{entity_name}.py",
                    f"app/api/v1/endpoints/{entity_name}s.py",
                ]
            else:
                # 默认顺序
                candidates = [
                    f"app/api/v1/endpoints/{entity_name}s.py",
                    f"app/api/v1/endpoints/{entity_name}.py",
                    f"app/crud/crud_{entity_name}.py",
                    f"app/crud/{entity_name}_crud.py",
                    f"app/crud/{entity_name}.py",
                    f"app/models/{entity_name}.py",
                    f"app/schemas/{entity_name}.py",
                ]
            
            # 返回第一个存在的文件
            for candidate in candidates:
                if (self.project_dir / candidate).exists():
                    logger.debug(f"Inferred source file for {test_name}: {candidate}")
                    return candidate
        
        # 通用推断：根据错误消息
        if "404" in error_message:
            # 404通常是路由问题
            return self._find_file_by_pattern("app/api/v1/endpoints/*.py")
        elif "500" in error_message or "Internal Server Error" in error_message:
            # 500通常是main.py或数据库配置问题
            return "app/main.py" if (self.app_dir / "main.py").exists() else None
        
        return None
    
    def _find_file_by_pattern(self, pattern: str) -> Optional[str]:
        """根据模式查找文件"""
        import glob
        files = glob.glob(str(self.project_dir / pattern))
        if files:
            # 返回相对路径
            return str(Path(files[0]).relative_to(self.project_dir))
        return None
    
    def prioritize_files(self, file_errors: Dict[str, List[TestError]]) -> List[FileToFix]:
        """对需要修复的文件进行优先级排序"""
        files_to_fix = []
        
        for file_path, errors in file_errors.items():
            priority = self._calculate_priority(file_path)
            
            file_to_fix = FileToFix(
                path=Path(file_path),
                errors=errors,
                priority=priority,
                dependencies=self._find_dependencies(file_path)
            )
            files_to_fix.append(file_to_fix)
        
        # 按优先级排序
        files_to_fix.sort(key=lambda f: (f.priority, len(f.errors)))
        
        return files_to_fix
    
    def _calculate_priority(self, file_path: str) -> int:
        """计算文件修复优先级"""
        path_parts = Path(file_path).parts
        
        # 检查文件名
        if path_parts[-1] in self.priority_map:
            return self.priority_map[path_parts[-1]]
        
        # 检查目录名
        for part in path_parts:
            if part in self.priority_map:
                return self.priority_map[part]
        
        # 默认优先级
        return 99
    
    def _find_dependencies(self, file_path: str) -> List[str]:
        """查找文件的依赖"""
        dependencies = []
        file_full_path = self.project_dir / file_path
        
        if not file_full_path.exists():
            return dependencies
        
        try:
            with open(file_full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找导入语句
            import_pattern = r"from\s+(\S+)\s+import|import\s+(\S+)"
            matches = re.findall(import_pattern, content)
            
            for match in matches:
                module = match[0] or match[1]
                # 只关注项目内的导入
                if module.startswith("app."):
                    dep_path = module.replace(".", "/") + ".py"
                    dependencies.append(dep_path)
        
        except Exception as e:
            logger.warning(f"Failed to analyze dependencies for {file_path}: {e}")
        
        return dependencies
    
    def create_fix_batch(self, files_to_fix: List[FileToFix], 
                        batch_size: int = 3) -> List[List[FileToFix]]:
        """创建修复批次，考虑依赖关系"""
        batches = []
        processed = set()
        
        while len(processed) < len(files_to_fix):
            batch = []
            
            for file in files_to_fix:
                if file.path.as_posix() in processed:
                    continue
                
                # 检查依赖是否已处理
                deps_processed = all(
                    dep in processed for dep in (file.dependencies or [])
                )
                
                if deps_processed and len(batch) < batch_size:
                    batch.append(file)
                    processed.add(file.path.as_posix())
            
            if batch:
                batches.append(batch)
            else:
                # 处理循环依赖的情况
                for file in files_to_fix:
                    if file.path.as_posix() not in processed:
                        batch = [file]
                        processed.add(file.path.as_posix())
                        batches.append(batch)
                        break
        
        return batches
    
    def run_single_file_test(self, test_file: str) -> Tuple[bool, str]:
        """运行单个测试文件"""
        try:
            cmd = ["python", "-m", "pytest", test_file, "-xvs"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=60  # 单文件测试超时时间短
            )
            
            return result.returncode == 0, result.stdout + result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "Test timeout"
        except Exception as e:
            return False, str(e)
    
    def generate_file_specific_prompt(self, file: FileToFix) -> str:
        """生成针对特定文件的修复提示"""
        errors_summary = []
        
        for error in file.errors:
            errors_summary.append(f"""
测试: {error.test_name}
错误类型: {error.error_type}
错误消息: {error.error_message}
出错位置: {error.file_path}:{error.line_number or 'unknown'}
""")
        
        prompt = f"""需要修复文件 {file.path} 中的错误。

文件: {file.path}
错误数量: {len(file.errors)}

具体错误:
{''.join(errors_summary)}

相关的完整错误信息:
{file.errors[0].full_traceback if file.errors else ''}

请只修复这个文件中的错误，确保：
1. 仔细分析错误原因
2. 只修改必要的代码
3. 保持代码风格一致
4. 不要修改其他文件
5. 确保修复后代码可以正常运行

特别注意:
- 如果是导入错误，检查模块路径是否正确
- 如果是属性错误，确认方法或属性是否存在
- 如果是类型错误，检查参数类型是否匹配
"""
        
        return prompt