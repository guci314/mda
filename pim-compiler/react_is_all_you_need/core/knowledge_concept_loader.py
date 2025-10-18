#!/usr/bin/env python3
"""
知识概念加载器 - 扩展支持理论概念索引

支持的格式：
- ## 函数 @xxx(...) - 可执行的知识函数
- ## 契约函数 @xxx(...) - 契约函数
- ## 概念 @xxx(...) - 理论概念
- ## 模式 @xxx - 设计模式
- ## 原理 @xxx - 基本原理
"""

import re
from pathlib import Path
from typing import List, Set, Dict, Optional
from dataclasses import dataclass


@dataclass
class KnowledgeItem:
    """知识项信息（函数、概念、模式等）"""
    name: str              # 名称（不含@）
    path: Path             # 文件绝对路径
    docstring: str         # 描述
    item_type: str         # 类型：'function', 'contract', 'concept', 'pattern', 'principle'
    category: str          # 分类：'executable'（可执行）, 'theory'（理论）


class KnowledgeConceptLoader:
    """扩展的知识加载器 - 支持函数和概念"""

    def __init__(self, knowledge_dirs: List[str], already_loaded: Set[str] = None):
        """初始化加载器"""
        self.knowledge_dirs = [Path(d) for d in knowledge_dirs]
        self.knowledge_index: Dict[str, KnowledgeItem] = {}  # @名称 -> 知识项
        self.loaded_files: Set[str] = already_loaded or set()

        # 分类索引
        self.functions: Dict[str, KnowledgeItem] = {}  # 可执行函数
        self.concepts: Dict[str, KnowledgeItem] = {}   # 理论概念

        # 启动时建立索引
        self._build_index()

    def _build_index(self):
        """扫描knowledge/目录，建立知识索引"""
        for dir_path in self.knowledge_dirs:
            if not dir_path.exists():
                continue

            # 递归扫描所有.md文件
            for md_file in dir_path.rglob("*.md"):
                if md_file.name == "__init__.md":
                    continue

                # 提取文件中定义的所有知识项
                items = self._extract_knowledge_items(md_file)

                # 建立映射
                for item in items:
                    # 统一索引
                    if item.name not in self.knowledge_index:
                        self.knowledge_index[item.name] = item

                    # 分类索引
                    if item.category == 'executable':
                        if item.name not in self.functions:
                            self.functions[item.name] = item
                    elif item.category == 'theory':
                        if item.name not in self.concepts:
                            self.concepts[item.name] = item

    def _extract_knowledge_items(self, file_path: Path) -> List[KnowledgeItem]:
        """从.md文件中提取所有知识项

        匹配格式：
        - ## 函数 @xxx(...)          -> function/executable
        - ## 契约函数 @xxx(...)      -> contract/executable
        - ## 概念 @xxx(...)          -> concept/theory
        - ## 模式 @xxx               -> pattern/theory
        - ## 原理 @xxx               -> principle/theory
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            items = []

            # 定义模式和类型映射
            patterns = [
                # 函数类（需要参数）
                (r'##\s+契约函数\s+@([\w]+)\s*\([^)]*\)', 'contract', 'executable'),
                (r'##\s+函数\s+@([\w]+)\s*\([^)]*\)', 'function', 'executable'),

                # 概念类（可选参数）
                (r'##\s+概念\s+@([\w]+)(?:\([^)]*\))?', 'concept', 'theory'),
                (r'##\s+模式\s+@([\w]+)', 'pattern', 'theory'),
                (r'##\s+原理\s+@([\w]+)', 'principle', 'theory'),
            ]

            # 逐个模式匹配
            for pattern, item_type, category in patterns:
                for match in re.finditer(pattern, content):
                    name = match.group(1)

                    # 提取描述
                    start_pos = match.end()
                    remaining = content[start_pos:]

                    # 找到下一个##标题
                    next_section = re.search(r'\n##\s+', remaining)
                    if next_section:
                        section_content = remaining[:next_section.start()]
                    else:
                        section_content = remaining

                    # 优先提取三引号内的描述
                    docstring = self._extract_docstring(section_content)
                    if not docstring:
                        docstring = self._extract_first_paragraph(section_content)

                    # 创建KnowledgeItem
                    item = KnowledgeItem(
                        name=name,
                        path=file_path.resolve(),
                        docstring=docstring,
                        item_type=item_type,
                        category=category
                    )
                    items.append(item)

            return items
        except Exception as e:
            print(f"  ⚠️ 提取知识项失败 {file_path}: {e}")
            return []

    def _extract_docstring(self, text: str) -> str:
        """提取三引号内的描述文本"""
        # 匹配 """ ... """ 格式的描述
        pattern = r'"""(.*?)"""'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            docstring = match.group(1).strip()
            # 处理多行，合并为单行
            lines = [line.strip() for line in docstring.split('\n') if line.strip()]
            result = ' '.join(lines)
            if len(result) > 100:
                result = result[:97] + '...'
            return result
        return ""

    def _extract_first_paragraph(self, text: str) -> str:
        """提取第一段文本作为描述"""
        lines = text.split('\n')
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

        # 合并为单行
        docstring = ' '.join(paragraph_lines)
        if len(docstring) > 100:
            docstring = docstring[:97] + '...'

        return docstring if docstring else '（无描述）'

    def detect_references(self, message: str) -> List[str]:
        """从消息中提取所有@引用（函数和概念）"""
        pattern = r'@([\w]+)'
        all_matches = re.findall(pattern, message)

        # 过滤出索引中存在的项
        valid_matches = []
        for match in all_matches:
            # 尝试最长匹配
            for i in range(len(match), 0, -1):
                candidate = match[:i]
                if candidate in self.knowledge_index:
                    valid_matches.append(candidate)
                    break

        return valid_matches

    def get_index_info(self) -> str:
        """获取索引信息（用于调试和展示）"""
        lines = [f"知识索引：共{len(self.knowledge_index)}项"]

        # 按类别分组显示
        if self.functions:
            lines.append("\n【可执行函数】")
            for name, item in sorted(self.functions.items()):
                type_str = "契约" if item.item_type == 'contract' else "函数"
                lines.append(f"  @{name} ({type_str}) -> {item.path.name}")
                lines.append(f"    {item.docstring}")

        if self.concepts:
            lines.append("\n【理论概念】")
            for name, item in sorted(self.concepts.items()):
                type_map = {
                    'concept': '概念',
                    'pattern': '模式',
                    'principle': '原理'
                }
                type_str = type_map.get(item.item_type, item.item_type)
                lines.append(f"  @{name} ({type_str}) -> {item.path.name}")
                lines.append(f"    {item.docstring}")

        return "\n".join(lines)

    def search_by_keyword(self, keyword: str) -> List[KnowledgeItem]:
        """按关键词搜索知识项"""
        results = []
        keyword_lower = keyword.lower()

        for item in self.knowledge_index.values():
            # 搜索名称和描述
            if (keyword_lower in item.name.lower() or
                keyword_lower in item.docstring.lower()):
                results.append(item)

        return results

    def get_related_items(self, name: str) -> List[KnowledgeItem]:
        """获取相关知识项（同文件或相似名称）"""
        if name not in self.knowledge_index:
            return []

        target = self.knowledge_index[name]
        related = []

        # 同文件的其他项
        for item in self.knowledge_index.values():
            if item.path == target.path and item.name != name:
                related.append(item)

        return related