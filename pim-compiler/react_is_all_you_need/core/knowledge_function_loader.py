#!/usr/bin/env python3
"""
知识函数自动加载器 - Unix哲学的实现

核心理念：
- knowledge/目录 = Linux的/bin/目录
- 知识函数 = Linux程序
- 自动检测@指令，按需加载知识文件
- 自然语言本身就是shell脚本
"""

import re
from pathlib import Path
from typing import List, Set, Dict, Optional
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    """知识函数信息

    类似Unix的whatis命令结果
    """
    name: str              # 函数名（不含@）
    path: Path             # 文件绝对路径
    docstring: str         # 第一段描述
    func_type: str         # 'contract' 或 'soft'


class KnowledgeFunctionLoader:
    """知识函数自动加载器

    功能：
    1. 启动时扫描knowledge/目录，建立函数索引
    2. 从用户消息中检测所有@函数引用
    3. 自动加载对应的知识文件
    4. 避免重复加载（智能去重）
    """

    def __init__(self, knowledge_dirs: List[str], already_loaded: Set[str] = None):
        """初始化加载器

        Args:
            knowledge_dirs: 知识目录列表（类似PATH环境变量）
            already_loaded: 已加载的知识文件集合
        """
        self.knowledge_dirs = [Path(d) for d in knowledge_dirs]
        self.function_index: Dict[str, FunctionInfo] = {}  # @函数名 -> 函数信息
        self.loaded_files: Set[str] = already_loaded or set()  # 已加载的文件路径

        # 启动时建立索引
        self._build_index()

    def _build_index(self):
        """扫描knowledge/目录，建立@函数名到函数信息的映射"""
        for dir_path in self.knowledge_dirs:
            if not dir_path.exists():
                continue

            # 递归扫描所有.md文件
            for md_file in dir_path.rglob("*.md"):
                # 跳过__init__.md和已索引的文件
                if md_file.name == "__init__.md":
                    continue

                # 提取文件中定义的所有@函数
                functions = self._extract_functions(md_file)

                # 建立映射
                for func_info in functions:
                    # 如果已存在映射，保留第一个（优先级）
                    if func_info.name not in self.function_index:
                        self.function_index[func_info.name] = func_info

    def _extract_functions(self, file_path: Path) -> List[FunctionInfo]:
        """从.md文件中提取所有@函数的完整信息

        匹配格式：
        - ## 函数 @xxx(...)
        - ## 契约函数 @xxx(...)

        提取信息：
        - 函数名
        - 函数类型（契约/软约束）
        - docstring（标题下第一段非空文本）

        Args:
            file_path: markdown文件路径

        Returns:
            FunctionInfo列表
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            functions = []

            # 匹配函数定义标题，捕获类型和名称
            # 格式: ## [契约]函数 @名称(...)
            pattern = r'##\s+(契约)?函数\s+@(\w+)\s*\([^)]*\)'

            # 找到所有匹配
            for match in re.finditer(pattern, content):
                is_contract = match.group(1) is not None  # 是否是契约函数
                func_name = match.group(2)

                # 提取docstring：标题后的第一段非空文本
                # 策略：从匹配位置向后查找，直到遇到下一个##或文件结束
                start_pos = match.end()
                remaining = content[start_pos:]

                # 找到下一个##标题（章节边界）
                next_section = re.search(r'\n##\s+', remaining)
                if next_section:
                    section_content = remaining[:next_section.start()]
                else:
                    section_content = remaining

                # 提取第一段非空文本
                docstring = self._extract_first_paragraph(section_content)

                # 创建FunctionInfo
                func_info = FunctionInfo(
                    name=func_name,
                    path=file_path.resolve(),  # 使用绝对路径
                    docstring=docstring,
                    func_type='contract' if is_contract else 'soft'
                )
                functions.append(func_info)

            return functions
        except Exception as e:
            print(f"  ⚠️ 提取函数信息失败 {file_path}: {e}")
            return []

    def _extract_first_paragraph(self, text: str) -> str:
        """从文本中提取第一段非空内容

        优先查找：
        1. Python docstring格式（```python ''' ... '''```）
        2. 否则提取第一段普通文本

        返回第一段完整文本，去除首尾空白
        """
        lines = text.split('\n')

        # 策略1：查找Python docstring（```python ''' ... '''```）
        in_python_block = False
        in_docstring = False
        docstring_lines = []

        for line in lines:
            stripped = line.strip()

            # 进入Python代码块
            if stripped.startswith('```python'):
                in_python_block = True
                continue

            # 退出代码块
            if in_python_block and stripped.startswith('```'):
                # 如果已经收集到docstring，立即返回
                if docstring_lines:
                    docstring = ' '.join(docstring_lines)
                    if len(docstring) > 100:
                        docstring = docstring[:97] + '...'
                    return docstring
                in_python_block = False
                continue

            # 在Python代码块中
            if in_python_block:
                # 检测三引号开始/结束
                if stripped.startswith("'''") or stripped.startswith('"""'):
                    if not in_docstring:
                        # 开始docstring
                        in_docstring = True
                        # 检查是否单行docstring
                        content = stripped.strip("'\"")
                        if content:
                            return content[:100] if len(content) <= 100 else content[:97] + '...'
                    else:
                        # 结束docstring
                        docstring = ' '.join(docstring_lines)
                        if len(docstring) > 100:
                            docstring = docstring[:97] + '...'
                        return docstring
                    continue

                # 收集docstring内容
                if in_docstring and stripped:
                    docstring_lines.append(stripped)

        # 策略2：如果没有找到Python docstring，提取第一段普通文本
        paragraph_lines = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()

            # 跳过代码块
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # 跳过子标题
            if stripped.startswith('###'):
                if paragraph_lines:
                    break
                continue

            # 空行表示段落结束
            if not stripped:
                if paragraph_lines:
                    break
                continue

            # 收集段落内容
            paragraph_lines.append(stripped)

        # 合并为单行，限制长度
        docstring = ' '.join(paragraph_lines)
        if len(docstring) > 100:
            docstring = docstring[:97] + '...'

        return docstring if docstring else '（无描述）'

    def detect_functions_in_message(self, message: str) -> List[str]:
        """从用户消息中提取所有@函数引用

        匹配格式：@函数名（支持英文字母、数字、下划线、中文）

        Args:
            message: 用户消息文本

        Returns:
            函数名列表（不含@符号）
        """
        # 匹配 @后面的标识符
        # 策略：先用宽松的正则匹配所有可能的候选，然后用索引过滤
        pattern = r'@([\w]+)'

        # 找到所有匹配
        all_matches = re.findall(pattern, message)

        # 智能过滤：尝试从左到右逐步缩短，找到索引中的匹配
        valid_matches = []
        for match in all_matches:
            # 尝试从完整匹配逐步缩短
            # 例如 "learning学习" -> 尝试 "learning学习", "learning学", "learning"
            for i in range(len(match), 0, -1):
                candidate = match[:i]
                if candidate in self.function_index:
                    valid_matches.append(candidate)
                    break  # 找到最长匹配就停止

        return valid_matches

    def load_required_functions(self, message: str) -> List[Path]:
        """检测消息中的@函数，自动加载对应知识文件

        工作流程：
        1. 从消息中提取所有@函数引用
        2. 在索引中查找对应的知识文件
        3. 避免重复加载
        4. 返回新加载的文件列表

        Args:
            message: 用户消息文本

        Returns:
            新加载的知识文件路径列表
        """
        detected = self.detect_functions_in_message(message)
        newly_loaded = []

        for func_name in detected:
            # 在索引中查找
            if func_name in self.function_index:
                func_info = self.function_index[func_name]
                file_str = str(func_info.path)

                # 避免重复加载
                if file_str not in self.loaded_files:
                    self.loaded_files.add(file_str)
                    newly_loaded.append(func_info.path)

        return newly_loaded

    def get_index_info(self) -> str:
        """获取索引信息（用于调试）"""
        lines = [f"知识函数索引：共{len(self.function_index)}个函数"]
        for func_name, func_info in sorted(self.function_index.items()):
            lines.append(f"  @{func_name} ({func_info.func_type}) -> {func_info.path.name}")
            lines.append(f"    {func_info.docstring}")
        return "\n".join(lines)
