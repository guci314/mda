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
        
        # 解析失败的测试
        test_pattern = r"(\S+\.py)::(\S+)\s+FAILED"
        error_pattern = r"E\s+(\w+Error|AssertionError):\s+(.+)"
        file_pattern = r"(\S+\.py):(\d+):"
        
        lines = error_output.split('\n')
        current_test = None
        current_file = None
        current_traceback = []
        
        for i, line in enumerate(lines):
            # 匹配失败的测试
            test_match = re.search(test_pattern, line)
            if test_match:
                # 保存之前的错误
                if current_test:
                    self._save_current_error(errors, current_test, current_file, current_traceback)
                
                current_test = TestError(
                    file_path=test_match.group(1),
                    test_name=test_match.group(2),
                    error_type="",
                    error_message="",
                    full_traceback=""
                )
                current_traceback = []
                continue
            
            # 匹配错误类型和消息
            error_match = re.search(error_pattern, line)
            if error_match and current_test:
                current_test.error_type = error_match.group(1)
                current_test.error_message = error_match.group(2)
            
            # 匹配文件路径
            file_match = re.search(file_pattern, line)
            if file_match:
                current_file = file_match.group(1)
                if current_test and not current_test.line_number:
                    current_test.line_number = int(file_match.group(2))
            
            # 收集traceback
            if current_test and line.strip():
                current_traceback.append(line)
        
        # 保存最后一个错误
        if current_test:
            self._save_current_error(errors, current_test, current_file, current_traceback)
        
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
        
        for error in errors:
            file_path = error.file_path
            
            # 跳过测试文件本身的错误，关注被测试代码的错误
            if file_path.startswith("tests/"):
                # 从traceback中提取实际出错的文件
                actual_file = self._extract_actual_error_file(error.full_traceback)
                if actual_file:
                    file_path = actual_file
                else:
                    continue
            
            if file_path not in file_errors:
                file_errors[file_path] = []
            file_errors[file_path].append(error)
        
        return file_errors
    
    def _extract_actual_error_file(self, traceback: str) -> Optional[str]:
        """从traceback中提取实际出错的源文件"""
        # 查找app/目录下的文件
        app_file_pattern = r"(app/\S+\.py):\d+:"
        matches = re.findall(app_file_pattern, traceback)
        
        # 返回最后一个匹配的app文件（通常是实际出错的地方）
        if matches:
            return matches[-1]
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