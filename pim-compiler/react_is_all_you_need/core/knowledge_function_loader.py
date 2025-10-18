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
import json
from pathlib import Path
from typing import List, Set, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class FunctionInfo:
    """知识函数信息

    类似Unix的whatis命令结果
    支持partial定义（类似C#的partial class）
    """
    name: str              # 函数名（不含@）
    path: Path             # 主文件绝对路径（第一个定义）
    docstring: str         # 第一段描述
    func_type: str         # 'contract' 或 'soft'
    signature: str = ""    # 函数签名（参数列表）
    all_locations: list = None  # 所有定义位置（支持partial定义）

    def __post_init__(self):
        if self.all_locations is None:
            self.all_locations = [self.path]


class KnowledgeFunctionLoader:
    """知识函数索引构建器

    功能：
    1. 启动时扫描knowledge/目录，建立函数索引
    2. 将索引保存到knowledge_function_index.json
    3. 智能体主动查询索引，自己读取需要的知识文件

    核心理念：
    - 系统只建立索引（类似图书馆目录）
    - 智能体自己查询索引、自己读取文件（主动学习）
    - 不是系统自动加载（避免剥夺智能体的主动性）
    """

    def __init__(self, knowledge_dirs: List[str]):
        """初始化索引构建器

        Args:
            knowledge_dirs: 知识目录列表（类似PATH环境变量）
        """
        self.knowledge_dirs = [Path(d) for d in knowledge_dirs]
        self.function_index: Dict[str, FunctionInfo] = {}  # @函数名 -> 函数信息

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

                # 建立映射（支持partial定义，类似C# partial class）
                for func_info in functions:
                    if func_info.name not in self.function_index:
                        # 第一次遇到，添加到索引
                        self.function_index[func_info.name] = func_info
                    else:
                        # 检测到重复定义（类似Unix PATH机制）
                        existing = self.function_index[func_info.name]
                        if existing.path != func_info.path:
                            # 检查核心一致性：签名和类型（不验证docstring）
                            signature_match = existing.signature == func_info.signature
                            type_match = existing.func_type == func_info.func_type
                            docstring_match = existing.docstring == func_info.docstring

                            if signature_match and type_match:
                                # ✅ Partial定义（类似C# partial class）
                                # docstring可以不同（允许从不同角度解释）
                                existing.all_locations.append(func_info.path)
                                print(f"  ✅ Partial定义: @{func_info.name}")
                                print(f"     主定义: {existing.path.name}")
                                print(f"     也出现在: {func_info.path.name}")
                                print(f"     验证核心: 签名✓ 类型✓")

                                if not docstring_match:
                                    print(f"     📝 docstring不同（允许，建议添加链接到主定义）")
                            else:
                                # ⚠️ 版本冲突（类似Unix PATH优先级）
                                print(f"  ⚠️ 版本冲突: @{func_info.name}")
                                print(f"     使用: {existing.path.name} (优先级高)")
                                print(f"     忽略: {func_info.path.name} (优先级低)")

                                # 详细差异报告（不抛出错误）
                                if not signature_match:
                                    print(f"        签名: ({existing.signature}) ≠ ({func_info.signature})")
                                if not type_match:
                                    print(f"        类型: {existing.func_type} ≠ {func_info.func_type}")

                                print(f"     💡 类似Unix: /usr/bin/ls 优先于 /bin/ls")

        # 保存索引到磁盘
        self._save_index_to_disk()

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

            # 匹配函数定义标题，捕获类型、名称和签名
            # 格式: ## [契约]函数 @名称(...) 或 ## [契约]函数 @名称
            # 括号是可选的，支持无参数函数
            pattern = r'##\s+(契约)?函数\s+@(\w+)(?:\s*\(([^)]*)\))?'

            # 找到所有匹配
            for match in re.finditer(pattern, content):
                is_contract = match.group(1) is not None  # 是否是契约函数
                func_name = match.group(2)
                signature = match.group(3).strip() if match.group(3) else ""  # 提取参数签名（可能为空）

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
                    func_type='contract' if is_contract else 'soft',
                    signature=signature  # 保存参数签名
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

    def get_index_info(self) -> str:
        """获取索引信息（用于调试）"""
        lines = [f"知识函数索引：共{len(self.function_index)}个函数"]
        for func_name, func_info in sorted(self.function_index.items()):
            lines.append(f"  @{func_name} ({func_info.func_type}) -> {func_info.path.name}")
            lines.append(f"    {func_info.docstring}")
        return "\n".join(lines)

    def _save_index_to_disk(self):
        """将索引保存到磁盘上的JSON文件

        保存位置：项目根目录/knowledge_function_index.json

        文件格式：
        {
            "metadata": {
                "total_functions": 数量,
                "knowledge_dirs": 扫描的目录列表,
                "generated_at": 生成时间
            },
            "functions": {
                "函数名": {
                    "name": "函数名",
                    "path": "文件绝对路径",
                    "docstring": "函数描述",
                    "func_type": "contract/soft",
                    "file_name": "文件名"
                }
            },
            "by_file": {
                "文件路径": ["函数1", "函数2", ...]
            },
            "by_type": {
                "contract": ["契约函数1", "契约函数2", ...],
                "soft": ["软约束函数1", "软约束函数2", ...]
            }
        }
        """
        import datetime

        # 构建保存的数据结构
        index_data = {
            "metadata": {
                "total_functions": len(self.function_index),
                "knowledge_dirs": [str(d) for d in self.knowledge_dirs],
                "generated_at": datetime.datetime.now().isoformat()
            },
            "functions": {},
            "by_file": {},
            "by_type": {"contract": [], "soft": []}
        }

        # 转换函数索引为可序列化的格式
        for func_name, func_info in sorted(self.function_index.items()):
            # 函数信息
            index_data["functions"][func_name] = {
                "name": func_info.name,
                "path": str(func_info.path),
                "docstring": func_info.docstring,
                "func_type": func_info.func_type,
                "signature": func_info.signature,
                "file_name": func_info.path.name,
                "all_locations": [str(loc) for loc in func_info.all_locations],  # 所有定义位置
                "is_partial": len(func_info.all_locations) > 1  # 是否是partial定义
            }

            # 按文件分组（包含所有定义位置）
            for loc in func_info.all_locations:
                loc_str = str(loc)
                if loc_str not in index_data["by_file"]:
                    index_data["by_file"][loc_str] = []
                index_data["by_file"][loc_str].append(func_name)

            # 按类型分组
            index_data["by_type"][func_info.func_type].append(func_name)

        # 确定保存路径（项目根目录）
        # 假设knowledge_dirs的第一个是 xxx/knowledge/，则项目根是上一级
        if self.knowledge_dirs:
            project_root = self.knowledge_dirs[0].parent
        else:
            project_root = Path.cwd()

        index_file = project_root / "knowledge_function_index.json"

        # 保存到文件
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)

            # 统计partial定义
            partial_funcs = [name for name, info in self.function_index.items()
                            if len(info.all_locations) > 1]

            print(f"\n📚 知识函数索引已保存到: {index_file}")
            print(f"   - 共索引 {len(self.function_index)} 个函数")
            print(f"   - 契约函数: {len(index_data['by_type']['contract'])} 个")
            print(f"   - 软约束函数: {len(index_data['by_type']['soft'])} 个")
            print(f"   - Partial定义: {len(partial_funcs)} 个")
            print(f"   - 涉及文件: {len(index_data['by_file'])} 个")

            if partial_funcs:
                print(f"\n   📋 Partial定义的函数:")
                for func_name in partial_funcs:
                    func_info = self.function_index[func_name]
                    print(f"      @{func_name}: {len(func_info.all_locations)} 个位置")
                    for loc in func_info.all_locations:
                        print(f"         - {loc.name}")
        except Exception as e:
            print(f"  ⚠️ 保存索引失败: {e}")
