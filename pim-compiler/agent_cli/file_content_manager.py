"""
文件内容管理器 - 解决文件覆盖问题
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging
import difflib

logger = logging.getLogger(__name__)


class MergeStrategy(Enum):
    """合并策略"""
    OVERWRITE = "overwrite"      # 覆盖（默认行为）
    APPEND = "append"           # 追加
    MERGE_SMART = "merge_smart" # 智能合并
    WARN_SKIP = "warn_skip"     # 警告并跳过
    INTERACTIVE = "interactive"  # 交互式（暂不实现）


@dataclass
class FileVersion:
    """文件版本信息"""
    content: str
    timestamp: float
    action_index: int  # 第几个动作创建的
    description: str   # 动作描述


class FileContentManager:
    """文件内容管理器
    
    防止文件被意外覆盖，支持内容合并
    """
    
    def __init__(self, default_strategy: MergeStrategy = MergeStrategy.MERGE_SMART):
        self.default_strategy = default_strategy
        self.file_history: Dict[str, List[FileVersion]] = {}
        self.merge_count = 0
        self.conflict_count = 0
        
    def check_file_write(
        self, 
        file_path: str, 
        new_content: str, 
        action_description: str,
        action_index: int
    ) -> Tuple[bool, str, Optional[str]]:
        """检查文件写入操作
        
        Returns:
            (should_write, reason, merged_content): 
            - should_write: 是否应该写入
            - reason: 决策原因
            - merged_content: 合并后的内容（如果需要）
        """
        # 如果文件从未写入过，直接允许
        if file_path not in self.file_history:
            self.file_history[file_path] = []
            return True, "新文件，允许创建", new_content
            
        # 获取文件历史
        history = self.file_history[file_path]
        latest_version = history[-1]
        
        # 如果内容完全相同，跳过
        if latest_version.content == new_content:
            return False, "内容与现有文件完全相同，跳过写入", None
            
        # 根据策略处理
        strategy = self._determine_strategy(file_path, action_description)
        
        if strategy == MergeStrategy.OVERWRITE:
            return True, "策略：覆盖现有文件", new_content
            
        elif strategy == MergeStrategy.APPEND:
            merged = latest_version.content + "\n\n" + new_content
            return True, "策略：追加到现有文件", merged
            
        elif strategy == MergeStrategy.WARN_SKIP:
            logger.warning(f"File {file_path} already exists with different content. Skipping.")
            self.conflict_count += 1
            return False, "文件已存在且内容不同，跳过以避免覆盖", None
            
        elif strategy == MergeStrategy.MERGE_SMART:
            merged, success, details = self._smart_merge(
                latest_version.content, new_content, file_path
            )
            if success:
                self.merge_count += 1
                return True, f"智能合并成功：{details}", merged
            else:
                self.conflict_count += 1
                return False, f"智能合并失败：{details}", None
                
        return False, "未知策略", None
        
    def record_file_write(
        self, 
        file_path: str, 
        content: str, 
        action_description: str,
        action_index: int,
        timestamp: float
    ):
        """记录文件写入"""
        if file_path not in self.file_history:
            self.file_history[file_path] = []
            
        version = FileVersion(
            content=content,
            timestamp=timestamp,
            action_index=action_index,
            description=action_description
        )
        self.file_history[file_path].append(version)
        
    def _determine_strategy(self, file_path: str, action_description: str) -> MergeStrategy:
        """根据文件类型和动作描述确定合并策略"""
        
        # 配置文件通常需要合并
        if file_path.endswith(('.json', '.yaml', '.yml', '.toml')):
            return MergeStrategy.MERGE_SMART
            
        # 主程序文件的增量更新
        if 'main.py' in file_path:
            if any(keyword in action_description.lower() for keyword in 
                  ['添加', 'add', '增加', 'append', '补充']):
                return MergeStrategy.MERGE_SMART
                
        # 测试文件通常追加
        if 'test' in file_path:
            return MergeStrategy.APPEND
            
        # 文档文件追加
        if file_path.endswith(('.md', '.txt', '.rst')):
            return MergeStrategy.APPEND
            
        # 默认策略
        return self.default_strategy
        
    def _smart_merge(
        self, 
        existing_content: str, 
        new_content: str, 
        file_path: str
    ) -> Tuple[str, bool, str]:
        """智能合并文件内容
        
        Returns:
            (merged_content, success, details)
        """
        # Python 文件的智能合并
        if file_path.endswith('.py'):
            return self._merge_python_files(existing_content, new_content)
            
        # JSON 文件的合并
        elif file_path.endswith('.json'):
            return self._merge_json_files(existing_content, new_content)
            
        # 其他文件类型
        else:
            # 简单的基于差异的合并
            return self._merge_by_diff(existing_content, new_content)
            
    def _merge_python_files(
        self, 
        existing: str, 
        new: str
    ) -> Tuple[str, bool, str]:
        """合并 Python 文件"""
        
        # 提取导入语句
        existing_imports = self._extract_imports(existing)
        new_imports = self._extract_imports(new)
        
        # 提取函数和类定义
        existing_defs = self._extract_definitions(existing)
        new_defs = self._extract_definitions(new)
        
        # 如果新内容只是添加新的函数/类，可以合并
        if not any(name in existing_defs for name in new_defs):
            # 合并导入
            merged_imports = self._merge_imports(existing_imports, new_imports)
            
            # 移除原有导入部分
            existing_body = self._remove_imports(existing)
            new_body = self._remove_imports(new)
            
            # 组合内容
            merged = merged_imports + "\n\n" + existing_body + "\n\n" + new_body
            
            return merged, True, "添加了新的函数/类定义"
            
        # 如果有重复定义，检查是否是相同的
        conflicts = []
        for name in new_defs:
            if name in existing_defs:
                if existing_defs[name] != new_defs[name]:
                    conflicts.append(name)
                    
        if conflicts:
            return "", False, f"存在冲突的定义：{', '.join(conflicts)}"
            
        # 如果定义相同，只合并导入
        merged_imports = self._merge_imports(existing_imports, new_imports)
        existing_body = self._remove_imports(existing)
        merged = merged_imports + "\n\n" + existing_body
        
        return merged, True, "合并了导入语句"
        
    def _extract_imports(self, content: str) -> List[str]:
        """提取导入语句"""
        import_pattern = r'^(from\s+\S+\s+import\s+.+|import\s+.+)$'
        imports = []
        for line in content.split('\n'):
            if re.match(import_pattern, line.strip()):
                imports.append(line.strip())
        return imports
        
    def _extract_definitions(self, content: str) -> Dict[str, str]:
        """提取函数和类定义"""
        definitions = {}
        
        # 简化的提取逻辑
        def_pattern = r'^(def\s+(\w+)|class\s+(\w+))'
        current_def = None
        current_lines = []
        
        for line in content.split('\n'):
            match = re.match(def_pattern, line)
            if match:
                if current_def:
                    definitions[current_def] = '\n'.join(current_lines)
                current_def = match.group(2) or match.group(3)
                current_lines = [line]
            elif current_def and line.strip():
                current_lines.append(line)
                
        if current_def:
            definitions[current_def] = '\n'.join(current_lines)
            
        return definitions
        
    def _merge_imports(self, imports1: List[str], imports2: List[str]) -> str:
        """合并导入语句"""
        all_imports = set(imports1) | set(imports2)
        
        # 分组排序
        standard_imports = []
        third_party_imports = []
        local_imports = []
        
        for imp in sorted(all_imports):
            if imp.startswith('from .') or imp.startswith('import .'):
                local_imports.append(imp)
            elif any(imp.startswith(f'from {lib}') or imp.startswith(f'import {lib}') 
                    for lib in ['os', 'sys', 'json', 'typing', 're', 'logging']):
                standard_imports.append(imp)
            else:
                third_party_imports.append(imp)
                
        # 组合
        result = []
        if standard_imports:
            result.extend(standard_imports)
        if third_party_imports:
            if result:
                result.append('')
            result.extend(third_party_imports)
        if local_imports:
            if result:
                result.append('')
            result.extend(local_imports)
            
        return '\n'.join(result)
        
    def _remove_imports(self, content: str) -> str:
        """移除导入语句"""
        import_pattern = r'^(from\s+\S+\s+import\s+.+|import\s+.+)$'
        lines = []
        skip_empty = True
        
        for line in content.split('\n'):
            if re.match(import_pattern, line.strip()):
                continue
            if skip_empty and not line.strip():
                continue
            skip_empty = False
            lines.append(line)
            
        return '\n'.join(lines).strip()
        
    def _merge_json_files(
        self, 
        existing: str, 
        new: str
    ) -> Tuple[str, bool, str]:
        """合并 JSON 文件"""
        try:
            import json
            existing_data = json.loads(existing)
            new_data = json.loads(new)
            
            # 深度合并
            merged_data = self._deep_merge_dict(existing_data, new_data)
            
            merged_json = json.dumps(merged_data, indent=2, ensure_ascii=False)
            return merged_json, True, "JSON 内容已合并"
            
        except Exception as e:
            return "", False, f"JSON 合并失败：{str(e)}"
            
    def _deep_merge_dict(self, dict1: dict, dict2: dict) -> dict:
        """深度合并字典"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dict(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def _merge_by_diff(
        self, 
        existing: str, 
        new: str
    ) -> Tuple[str, bool, str]:
        """基于差异的简单合并"""
        # 如果新内容是现有内容的超集，使用新内容
        if existing in new:
            return new, True, "新内容包含了现有内容"
            
        # 否则追加
        merged = existing + "\n\n# === 追加的内容 ===\n\n" + new
        return merged, True, "内容已追加"
        
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "files_tracked": len(self.file_history),
            "total_versions": sum(len(versions) for versions in self.file_history.values()),
            "merge_count": self.merge_count,
            "conflict_count": self.conflict_count
        }