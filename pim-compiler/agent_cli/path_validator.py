"""
路径验证器 - 确保文件路径的正确性
"""
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class PathValidator:
    """路径验证和修正器
    
    解决路径错误问题：
    1. 维护项目根目录上下文
    2. 自动修正相对路径
    3. 验证路径合法性
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """初始化路径验证器
        
        Args:
            project_root: 项目根目录，如果为 None 则使用当前工作目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.created_directories: List[Path] = []
        self.output_directory: Optional[Path] = None
        
    def set_output_directory(self, directory: str) -> None:
        """设置输出目录（如 blog_management_output_v2）"""
        self.output_directory = Path(directory)
        logger.info(f"Set output directory: {self.output_directory}")
        
    def infer_output_directory(self, created_files: List[str]) -> Optional[str]:
        """从已创建的文件推断输出目录"""
        if not created_files:
            return None
            
        # 查找公共前缀
        common_parts = []
        for file_path in created_files:
            parts = Path(file_path).parts
            if not common_parts:
                common_parts = list(parts[:-1])  # 排除文件名
            else:
                # 找到公共部分
                new_common = []
                for i, part in enumerate(common_parts):
                    if i < len(parts) - 1 and parts[i] == part:
                        new_common.append(part)
                    else:
                        break
                common_parts = new_common
                
        if common_parts:
            inferred = Path(*common_parts)
            logger.info(f"Inferred output directory: {inferred}")
            return str(inferred)
        return None
        
    def validate_and_fix_path(self, file_path: str, context: Dict) -> Tuple[str, str]:
        """验证并修正文件路径
        
        Args:
            file_path: 原始文件路径
            context: 执行上下文，包含已创建的文件等信息
            
        Returns:
            (fixed_path, reason): 修正后的路径和修正原因
        """
        original_path = Path(file_path)
        
        # 如果是绝对路径，直接返回
        if original_path.is_absolute():
            return file_path, "已是绝对路径"
            
        # 策略1：如果设置了输出目录，检查路径是否应该在输出目录下
        if self.output_directory:
            # 检查路径是否已经包含输出目录
            if not str(original_path).startswith(str(self.output_directory)):
                # 检查是否是典型的项目结构路径
                typical_dirs = ['api', 'models', 'schemas', 'services', 'tests', 'config']
                first_part = original_path.parts[0] if original_path.parts else ""
                
                if first_part in typical_dirs:
                    # 应该在输出目录下
                    fixed_path = self.output_directory / original_path
                    return str(fixed_path), f"添加输出目录前缀 {self.output_directory}"
                    
        # 策略2：从上下文推断
        if "created_files" in context and context["created_files"]:
            # 尝试从已创建的文件推断输出目录
            inferred_dir = self.infer_output_directory(context["created_files"])
            if inferred_dir and not str(original_path).startswith(inferred_dir):
                # 检查是否应该在推断的目录下
                typical_dirs = ['api', 'models', 'schemas', 'services', 'tests', 'config']
                first_part = original_path.parts[0] if original_path.parts else ""
                
                if first_part in typical_dirs:
                    fixed_path = Path(inferred_dir) / original_path
                    return str(fixed_path), f"基于已创建文件推断，添加目录前缀 {inferred_dir}"
                    
        # 策略3：检查父目录是否存在
        parent = original_path.parent
        if parent != Path('.') and not parent.exists():
            # 尝试在已知的目录中查找
            for created_dir in self.created_directories:
                if created_dir.name == parent.name:
                    # 找到匹配的目录
                    fixed_path = created_dir / original_path.name
                    return str(fixed_path), f"修正为已创建的目录 {created_dir}"
                    
        # 如果没有问题，返回原路径
        return file_path, "路径正确"
        
    def track_directory_creation(self, directory: str) -> None:
        """跟踪创建的目录"""
        dir_path = Path(directory)
        if dir_path not in self.created_directories:
            self.created_directories.append(dir_path)
            logger.debug(f"Tracked directory creation: {directory}")
            
    def suggest_path_fixes(self, file_path: str) -> List[str]:
        """建议可能的路径修正"""
        suggestions = []
        original_path = Path(file_path)
        
        # 建议1：添加输出目录
        if self.output_directory:
            suggestion1 = self.output_directory / original_path
            suggestions.append(str(suggestion1))
            
        # 建议2：在当前目录
        suggestions.append(file_path)
        
        # 建议3：在项目根目录
        suggestion3 = self.project_root / original_path
        if str(suggestion3) not in suggestions:
            suggestions.append(str(suggestion3))
            
        return suggestions
        
    def validate_write_path(self, file_path: str) -> Tuple[bool, str]:
        """验证写入路径是否安全
        
        Returns:
            (is_valid, message): 是否有效和消息
        """
        path = Path(file_path)
        
        # 检查是否尝试写入系统目录
        dangerous_prefixes = ['/etc', '/usr', '/bin', '/sbin', '/var/log']
        for prefix in dangerous_prefixes:
            if str(path).startswith(prefix):
                return False, f"危险：尝试写入系统目录 {prefix}"
                
        # 检查是否尝试覆盖重要文件
        important_files = ['.bashrc', '.profile', '.gitconfig', 'requirements.txt']
        if path.name in important_files and path.parent == Path.home():
            return False, f"危险：尝试覆盖重要配置文件 {path.name}"
            
        return True, "路径安全"


def integrate_path_validator_with_executor(
    executor,
    path_validator: PathValidator,
    context: Dict
) -> None:
    """将路径验证器集成到执行器中"""
    
    # 保存原始的执行方法
    original_execute = executor.execute
    
    def validated_execute(tool_name: str, parameters: Dict, **kwargs):
        """带路径验证的执行方法"""
        
        # 如果是写文件操作，验证和修正路径
        if tool_name == "write_file" and "path" in parameters:
            original_path = parameters["path"]
            
            # 验证路径安全性
            is_safe, safety_msg = path_validator.validate_write_path(original_path)
            if not is_safe:
                logger.error(f"Path validation failed: {safety_msg}")
                return {"error": safety_msg}
                
            # 修正路径
            fixed_path, reason = path_validator.validate_and_fix_path(
                original_path, context
            )
            
            if fixed_path != original_path:
                logger.info(f"Fixed path: {original_path} -> {fixed_path} ({reason})")
                parameters = parameters.copy()
                parameters["path"] = fixed_path
                
        # 如果是创建目录操作，跟踪目录
        elif tool_name == "bash" and "mkdir" in parameters.get("command", ""):
            # 简单提取目录名（这是一个简化的实现）
            import re
            mkdir_match = re.search(r'mkdir\s+(?:-p\s+)?([^\s;]+)', parameters["command"])
            if mkdir_match:
                dir_path = mkdir_match.group(1)
                path_validator.track_directory_creation(dir_path)
                
        # 调用原始执行方法
        return original_execute(tool_name=tool_name, parameters=parameters, **kwargs)
        
    # 替换执行方法
    executor.execute = validated_execute