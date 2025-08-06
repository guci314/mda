"""React Agent 工具集

包含所有 Agent 可用的工具函数，支持文件操作、命令执行、代码搜索等功能。
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Union

from langchain.tools import tool
from pydantic import BaseModel, Field

# Google 搜索相关导入
try:
    from googleapiclient.discovery import build
    import requests
    from bs4 import BeautifulSoup
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False


# Pydantic 输入模型定义
class FileInput(BaseModel):
    file_path: str = Field(description="文件路径")
    content: str = Field(description="文件内容")

class DirectoryInput(BaseModel):
    directory_path: str = Field(description="目录路径")

class CommandInput(BaseModel):
    command: str = Field(description="要执行的命令")
    working_dir: str = Field(default="", description="工作目录，默认为空字符串表示使用当前工作目录")

class SearchInput(BaseModel):
    pattern: str = Field(description="搜索模式（文件名或路径片段）")
    directory: str = Field(default=".", description="搜索目录")

class SearchReplaceInput(BaseModel):
    file_path: str = Field(description="文件路径")
    search_pattern: str = Field(description="搜索模式（支持正则表达式）")
    replace_text: str = Field(description="替换文本")
    use_regex: bool = Field(default=False, description="是否使用正则表达式")
    preview: bool = Field(default=False, description="是否仅预览更改")
    max_replacements: int = Field(default=-1, description="最大替换次数，-1表示全部替换")

class EditLinesInput(BaseModel):
    file_path: str = Field(description="文件路径")
    start_line: int = Field(description="起始行号（从1开始）")
    end_line: int = Field(description="结束行号（包含）")
    new_content: str = Field(default="", description="新内容，如果为空字符串则删除这些行")

class FindSymbolInput(BaseModel):
    symbol_name: str = Field(description="符号名称")
    symbol_type: str = Field(default="all", description="符号类型：function/class/variable/all")
    search_dir: str = Field(default=".", description="搜索目录")
    include_imports: bool = Field(default=False, description="是否包含导入语句")

class ExtractCodeInput(BaseModel):
    file_path: str = Field(description="文件路径")
    target: str = Field(description="目标函数名或类名")
    include_docstring: bool = Field(default=True, description="是否包含文档字符串")
    include_decorators: bool = Field(default=True, description="是否包含装饰器")

class DiffInput(BaseModel):
    file_path: str = Field(description="文件路径")
    diff_content: str = Field(description="Unified diff 格式的补丁内容")
    reverse: bool = Field(default=False, description="是否反向应用补丁")

class GoogleSearchInput(BaseModel):
    query: str = Field(description="搜索关键词")
    site: Optional[str] = Field(default=None, description="限定搜索的网站域名")
    num: int = Field(default=10, description="返回结果数量")

class WebPageInput(BaseModel):
    url: str = Field(description="网页 URL")


def create_tools(work_dir: str):
    """创建工具集
    
    Args:
        work_dir: 工作目录路径
        
    Returns:
        list: 工具函数列表
    """
    
    @tool("write_file", args_schema=FileInput)
    def write_file(file_path: str, content: str) -> str:
        """写入文件到指定路径
        
        将内容写入到指定的文件路径。
        如果传入绝对路径，直接使用；如果传入相对路径，则相对于 work_dir。
        如果目录不存在会自动创建。
        
        Args:
            file_path: 文件路径（可以是绝对路径或相对路径）
            content: 要写入的内容
            
        Returns:
            str: 成功或错误消息
        """
        try:
            # 检查是否为绝对路径
            if Path(file_path).is_absolute():
                file_full_path = Path(file_path)
                if os.environ.get('DEBUG'):
                    print(f"[DEBUG] write_file: Using absolute path: {file_full_path}")
            else:
                file_full_path = Path(work_dir) / file_path
                if os.environ.get('DEBUG'):
                    print(f"[DEBUG] write_file: Using relative path '{file_path}' -> absolute: {file_full_path}")
                    print(f"[DEBUG] write_file: work_dir is: {work_dir}")
            
            file_full_path.parent.mkdir(parents=True, exist_ok=True)
            file_full_path.write_text(content, encoding='utf-8')
            
            if os.environ.get('DEBUG'):
                print(f"[DEBUG] write_file: File written successfully to: {file_full_path}")
                print(f"[DEBUG] write_file: File exists check: {file_full_path.exists()}")
                print(f"[DEBUG] write_file: File size: {file_full_path.stat().st_size} bytes")
            
            return f"Successfully wrote file: {file_path}"
        except Exception as e:
            if os.environ.get('DEBUG'):
                print(f"[DEBUG] write_file: Error occurred: {str(e)}")
            return f"Error writing file: {str(e)}"

    @tool("read_file")
    def read_file(file_path: str) -> str:
        """读取文件内容
        
        Args:
            file_path: 文件路径（可以是绝对路径或相对路径）
            
        Returns:
            str: 文件内容或错误消息
        """
        try:
            # 检查是否为绝对路径
            if Path(file_path).is_absolute():
                file_full_path = Path(file_path)
                if os.environ.get('DEBUG'):
                    print(f"[DEBUG] read_file: Using absolute path: {file_full_path}")
            else:
                file_full_path = Path(work_dir) / file_path
                if os.environ.get('DEBUG'):
                    print(f"[DEBUG] read_file: Using relative path '{file_path}' -> absolute: {file_full_path}")
                    print(f"[DEBUG] read_file: work_dir is: {work_dir}")
            
            if os.environ.get('DEBUG'):
                print(f"[DEBUG] read_file: Checking file existence at: {file_full_path}")
                print(f"[DEBUG] read_file: File exists: {file_full_path.exists()}")
                if file_full_path.parent.exists():
                    print(f"[DEBUG] read_file: Parent directory exists: {file_full_path.parent}")
                    # 列出父目录中的文件
                    files_in_parent = list(file_full_path.parent.glob("*"))
                    print(f"[DEBUG] read_file: Files in parent directory: {[f.name for f in files_in_parent[:10]]}")
                
            if not file_full_path.exists():
                if os.environ.get('DEBUG'):
                    print(f"[DEBUG] read_file: File not found at: {file_full_path}")
                return f"File not found: {file_path}"
            
            content = file_full_path.read_text(encoding='utf-8')
            if os.environ.get('DEBUG'):
                print(f"[DEBUG] read_file: Successfully read file, size: {len(content)} chars")
            return content
        except Exception as e:
            if os.environ.get('DEBUG'):
                print(f"[DEBUG] read_file: Error occurred: {str(e)}")
            return f"Error reading file: {str(e)}"

    @tool("create_directory", args_schema=DirectoryInput)
    def create_directory(directory_path: str) -> str:
        """创建目录（包括父目录）"""
        try:
            dir_full_path = Path(work_dir) / directory_path
            dir_full_path.mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory: {directory_path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"

    @tool("list_directory", args_schema=DirectoryInput)
    def list_directory(directory_path: str = ".") -> str:
        """列出目录内容
        
        显示目录内容，包括文件和子目录。
        
        注意：对于生成 world_overview.md，建议使用 execute_command 工具：
        - Git仓库：git ls-files | xargs -n1 dirname | sort -u
        - 非Git仓库：eza . --tree -L 3 -I '.venv|venv|env|__pycache__|*.pyc|.git'
        
        Args:
            directory_path: 目录路径（可以是绝对路径或相对路径）
            
        Returns:
            str: 目录内容列表或错误消息
        """
        try:
            # 检查是否为绝对路径
            if Path(directory_path).is_absolute():
                dir_full_path = Path(directory_path)
            else:
                dir_full_path = Path(work_dir) / directory_path
                
            if not dir_full_path.exists():
                return f"Directory not found: {directory_path}"
            
            items = []
            for item in sorted(dir_full_path.iterdir()):
                if item.is_dir():
                    items.append(f"[DIR] {item.name}")
                else:
                    items.append(f"[FILE] {item.name}")
            
            return "\n".join(items) if items else "Empty directory"
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    @tool("execute_command", args_schema=CommandInput)
    def execute_command(command: str, working_dir: str = "") -> str:
        """执行系统命令
        
        在指定工作目录执行 shell 命令。
        
        Args:
            command: 要执行的命令
            working_dir: 工作目录，如果不指定则使用配置的 work_dir
            
        Returns:
            str: 命令输出或错误信息
        """
        try:
            cwd = working_dir if working_dir and working_dir.strip() else work_dir
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = f"Exit code: {result.returncode}\n"
            if result.stdout:
                output += f"{result.stdout}"
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
            
            return output
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @tool("search_files", args_schema=SearchInput)
    def search_files(pattern: str, directory: str = ".") -> str:
        """搜索文件或目录
        
        在指定目录中搜索匹配模式的文件或目录。
        支持：
        - 文件名搜索：例如 "test.py"
        - 路径片段搜索：例如 "src/models"
        - 自动 CamelCase 到 snake_case 转换
        
        Args:
            pattern: 搜索模式
            directory: 搜索起始目录（可以是绝对路径或相对路径）
            
        Returns:
            str: 匹配的文件路径列表
        """
        try:
            # 检查是否为绝对路径
            if Path(directory).is_absolute():
                search_dir = Path(directory)
                if os.environ.get('DEBUG'):
                    print(f"[DEBUG] search_files: Using absolute directory: {search_dir}")
            else:
                search_dir = Path(work_dir) / directory
                if os.environ.get('DEBUG'):
                    print(f"[DEBUG] search_files: Using relative directory '{directory}' -> absolute: {search_dir}")
                    print(f"[DEBUG] search_files: work_dir is: {work_dir}")
                
            if os.environ.get('DEBUG'):
                print(f"[DEBUG] search_files: Searching for pattern '{pattern}' in: {search_dir}")
                print(f"[DEBUG] search_files: Directory exists: {search_dir.exists()}")
                
            if not search_dir.exists():
                if os.environ.get('DEBUG'):
                    print(f"[DEBUG] search_files: Directory not found at: {search_dir}")
                return f"Directory not found: {directory}"
            
            # 生成搜索模式的多个变体
            patterns = [pattern]
            
            # 如果模式包含大写字母，尝试 snake_case 转换
            if any(c.isupper() for c in pattern) and not pattern.isupper():
                # CamelCase to snake_case
                snake_pattern = re.sub(r'(?<!^)(?=[A-Z])', '_', pattern).lower()
                patterns.append(snake_pattern)
                
                # 也尝试不带扩展名的版本
                if '.' not in pattern:
                    patterns.append(snake_pattern + '.py')
                    patterns.append(snake_pattern + '.md')
            
            # 收集所有匹配的文件
            matches = []
            for item in search_dir.rglob("*"):
                if item.is_file():
                    # 获取相对路径字符串
                    rel_path = str(item.relative_to(search_dir))
                    
                    # 检查是否匹配任何模式（大小写不敏感）
                    for p in patterns:
                        if p.lower() in rel_path.lower() or p.lower() in item.name.lower():
                            matches.append(rel_path)
                            break
            
            if matches:
                # 按路径长度排序（更短的路径通常更相关）
                matches.sort(key=len)
                result = f"Found {len(matches)} matches for '{pattern}':\n"
                # 限制显示前 20 个结果
                for match in matches[:20]:
                    result += f"  {match}\n"
                if len(matches) > 20:
                    result += f"  ... and {len(matches) - 20} more files"
                return result
            else:
                # 如果没找到，提供可能的建议
                suggestion = ""
                if any(c.isupper() for c in pattern) and not pattern.isupper():
                    snake = re.sub(r'(?<!^)(?=[A-Z])', '_', pattern).lower()
                    suggestion = f"\n\nHint: If you're looking for a Python file, try searching for '{snake}' or '{snake}.py'"
                
                return f"No files found matching '{pattern}' in {directory}{suggestion}"
                
        except Exception as e:
            return f"Error searching files: {str(e)}"

    @tool("search_replace", args_schema=SearchReplaceInput)
    def search_replace(file_path: str, search_pattern: str, replace_text: str,
                      use_regex: bool = False, preview: bool = False, 
                      max_replacements: int = -1) -> str:
        """在文件中进行搜索替换
        
        支持普通文本和正则表达式替换，可以预览更改。
        
        Args:
            file_path: 文件路径，相对于工作目录
            search_pattern: 搜索模式（文本或正则表达式）
            replace_text: 替换文本
            use_regex: 是否使用正则表达式
            preview: 是否仅预览，不实际修改文件
            max_replacements: 最大替换次数，-1 表示全部替换
            
        Returns:
            str: 操作结果或预览信息
        """
        try:
            file_full_path = Path(work_dir) / file_path
            if not file_full_path.exists():
                return f"File not found: {file_path}"
            
            content = file_full_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 执行替换
            changes = []
            new_lines = []
            replacement_count = 0
            
            for line_num, line in enumerate(lines, 1):
                if use_regex:
                    # 正则表达式替换
                    if max_replacements == -1:
                        new_line, count = re.subn(search_pattern, replace_text, line)
                    else:
                        # 限制替换次数
                        remaining = max_replacements - replacement_count
                        if remaining <= 0:
                            new_line = line
                            count = 0
                        else:
                            new_line, count = re.subn(search_pattern, replace_text, line, count=remaining)
                else:
                    # 普通文本替换
                    count = line.count(search_pattern)
                    if max_replacements != -1:
                        remaining = max_replacements - replacement_count
                        count = min(count, remaining)
                    
                    if count > 0:
                        new_line = line.replace(search_pattern, replace_text, count)
                    else:
                        new_line = line
                
                if count > 0:
                    changes.append(f"Line {line_num}: {line} -> {new_line}")
                    replacement_count += count
                
                new_lines.append(new_line)
            
            if not changes:
                return f"No matches found for pattern: {search_pattern}"
            
            result = f"Found {replacement_count} matches in {len(changes)} lines\n"
            
            if preview:
                result += "\nPreview of changes:\n"
                result += "\n".join(changes[:10])  # 显示前10个变更
                if len(changes) > 10:
                    result += f"\n... and {len(changes) - 10} more lines"
            else:
                # 实际写入文件
                new_content = '\n'.join(new_lines)
                file_full_path.write_text(new_content, encoding='utf-8')
                result += f"\nSuccessfully replaced {replacement_count} occurrences in {file_path}"
            
            return result
            
        except re.error as e:
            return f"Regex error: {str(e)}"
        except Exception as e:
            return f"Error in search_replace: {str(e)}"

    @tool("edit_lines", args_schema=EditLinesInput)
    def edit_lines(file_path: str, start_line: int, end_line: int, 
                  new_content: str = "") -> str:
        """编辑文件的指定行范围
        
        可以替换或删除指定行范围的内容。
        
        Args:
            file_path: 相对于工作目录的文件路径
            start_line: 起始行号（从1开始）
            end_line: 结束行号（包含）
            new_content: 新内容，如果为None则删除这些行
            
        Returns:
            str: 操作结果
        """
        try:
            file_full_path = Path(work_dir) / file_path
            if not file_full_path.exists():
                return f"File not found: {file_path}"
            
            content = file_full_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 验证行号
            if start_line < 1 or end_line < 1:
                return "Error: Line numbers must be >= 1"
            if start_line > len(lines):
                return f"Error: start_line {start_line} exceeds file length {len(lines)}"
            if end_line > len(lines):
                end_line = len(lines)  # 调整到文件末尾
            if start_line > end_line:
                return "Error: start_line must be <= end_line"
            
            # 准备新内容
            new_lines = []
            # 添加开始行之前的内容
            new_lines.extend(lines[:start_line - 1])
            
            # 添加新内容（如果有）
            if new_content is not None:
                # 确保新内容不以换行符结尾（避免多余空行）
                new_content = new_content.rstrip('\n')
                if new_content:
                    new_lines.extend(new_content.split('\n'))
            
            # 添加结束行之后的内容
            new_lines.extend(lines[end_line:])
            
            # 写入文件
            new_file_content = '\n'.join(new_lines)
            file_full_path.write_text(new_file_content, encoding='utf-8')
            
            # 生成操作描述
            old_line_count = end_line - start_line + 1
            new_line_count = len(new_content.split('\n')) if new_content else 0
            
            if new_content is None or new_content == "":
                action = f"Deleted lines {start_line}-{end_line} ({old_line_count} lines)"
            elif old_line_count == new_line_count:
                action = f"Replaced lines {start_line}-{end_line}"
            else:
                action = f"Replaced lines {start_line}-{end_line} ({old_line_count} lines) with {new_line_count} lines"
            
            return f"Successfully edited {file_path}: {action}"
            
        except Exception as e:
            return f"Error in edit_lines: {str(e)}"

    @tool("find_symbol", args_schema=FindSymbolInput)
    def find_symbol(symbol_name: str, symbol_type: str = "all", 
                   search_dir: str = ".", include_imports: bool = False) -> str:
        """查找代码中的符号定义和引用
        
        在指定目录中查找函数、类、变量的定义和使用位置。
        支持Python文件的智能解析。
        
        Args:
            symbol_name: 要查找的符号名称
            symbol_type: 符号类型 (function/class/variable/all)
            search_dir: 搜索目录，相对于工作目录
            include_imports: 是否包含导入语句中的引用
            
        Returns:
            str: 符号的定义位置和引用列表
        """
        try:
            search_path = Path(work_dir) / search_dir
            if not search_path.exists():
                return f"Directory not found: {search_dir}"
            
            results = {
                "definitions": [],
                "references": [],
                "imports": []
            }
            
            # 定义搜索模式
            patterns = {
                "function": [
                    rf"^\s*def\s+{symbol_name}\s*\(",          # 函数定义
                    rf"^\s*async\s+def\s+{symbol_name}\s*\("   # 异步函数定义
                ],
                "class": [
                    rf"^\s*class\s+{symbol_name}\s*[\(:]"      # 类定义
                ],
                "variable": [
                    rf"^\s*{symbol_name}\s*=",                  # 变量赋值
                    rf"^\s*{symbol_name}\s*:",                  # 类型注解
                    rf"^\s*self\.{symbol_name}\s*="             # 实例变量
                ]
            }
            
            # 如果是 all，使用所有模式
            if symbol_type == "all":
                all_patterns = []
                for pats in patterns.values():
                    all_patterns.extend(pats)
                search_patterns = all_patterns
            else:
                search_patterns = patterns.get(symbol_type, [])
            
            # 引用模式（更宽松的匹配）
            reference_pattern = rf"\b{symbol_name}\b"
            
            # 导入模式
            import_patterns = [
                rf"^\s*from\s+.*\s+import\s+.*\b{symbol_name}\b",
                rf"^\s*import\s+.*\b{symbol_name}\b"
            ]
            
            # 递归搜索 Python 文件
            for py_file in search_path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    relative_path = py_file.relative_to(Path(work_dir))
                    
                    for line_num, line in enumerate(lines, 1):
                        # 检查定义
                        for pattern in search_patterns:
                            if re.search(pattern, line, re.MULTILINE):
                                results["definitions"].append({
                                    "file": str(relative_path),
                                    "line": line_num,
                                    "text": line.strip()
                                })
                                break
                        
                        # 检查引用（排除定义行）
                        if re.search(reference_pattern, line):
                            # 检查是否是定义行
                            is_definition = False
                            for pattern in search_patterns:
                                if re.search(pattern, line, re.MULTILINE):
                                    is_definition = True
                                    break
                            
                            if not is_definition:
                                # 检查是否是导入
                                is_import = False
                                for import_pat in import_patterns:
                                    if re.search(import_pat, line, re.MULTILINE):
                                        is_import = True
                                        if include_imports:
                                            results["imports"].append({
                                                "file": str(relative_path),
                                                "line": line_num,
                                                "text": line.strip()
                                            })
                                        break
                                
                                if not is_import:
                                    results["references"].append({
                                        "file": str(relative_path),
                                        "line": line_num,
                                        "text": line.strip()
                                    })
                
                except Exception as e:
                    continue  # 跳过无法读取的文件
            
            # 格式化结果
            output = []
            
            if results["definitions"]:
                output.append(f"=== Definitions of '{symbol_name}' ===")
                for item in results["definitions"]:
                    output.append(f"{item['file']}:{item['line']} - {item['text']}")
            else:
                output.append(f"No definitions found for '{symbol_name}'")
            
            if results["references"]:
                output.append(f"\n=== References to '{symbol_name}' ({len(results['references'])} found) ===")
                # 只显示前20个引用
                for item in results["references"][:20]:
                    output.append(f"{item['file']}:{item['line']} - {item['text']}")
                if len(results["references"]) > 20:
                    output.append(f"... and {len(results['references']) - 20} more references")
            
            if include_imports and results["imports"]:
                output.append(f"\n=== Imports of '{symbol_name}' ===")
                for item in results["imports"]:
                    output.append(f"{item['file']}:{item['line']} - {item['text']}")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"Error in find_symbol: {str(e)}"

    @tool("extract_code", args_schema=ExtractCodeInput)
    def extract_code(file_path: str, target: str, 
                    include_docstring: bool = True, 
                    include_decorators: bool = True) -> str:
        """提取指定函数或类的完整代码
        
        从文件中提取完整的函数或类定义，包括装饰器、文档字符串和所有内容。
        
        Args:
            file_path: 文件路径，相对于工作目录
            target: 要提取的函数名或类名
            include_docstring: 是否包含文档字符串
            include_decorators: 是否包含装饰器
            
        Returns:
            str: 提取的代码内容
        """
        try:
            file_full_path = Path(work_dir) / file_path
            if not file_full_path.exists():
                return f"File not found: {file_path}"
            
            content = file_full_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 查找目标定义
            target_line = -1
            target_type = None
            indent_level = 0
            
            # 搜索函数或类定义
            for i, line in enumerate(lines):
                # 检查函数定义
                if re.match(rf"^\s*def\s+{target}\s*\(", line) or \
                   re.match(rf"^\s*async\s+def\s+{target}\s*\(", line):
                    target_line = i
                    target_type = "function"
                    indent_level = len(line) - len(line.lstrip())
                    break
                # 检查类定义
                elif re.match(rf"^\s*class\s+{target}\s*[\(:]", line):
                    target_line = i
                    target_type = "class"
                    indent_level = len(line) - len(line.lstrip())
                    break
            
            if target_line == -1:
                return f"Target '{target}' not found in {file_path}"
            
            # 收集代码行
            code_lines = []
            
            # 向上查找装饰器
            if include_decorators:
                decorator_start = target_line
                for i in range(target_line - 1, -1, -1):
                    line = lines[i]
                    stripped = line.strip()
                    # 检查是否是装饰器或多行装饰器的延续
                    if stripped.startswith('@') or (stripped and lines[i+1].strip().startswith('@')):
                        decorator_start = i
                    elif stripped == "":
                        continue  # 跳过空行
                    else:
                        break  # 遇到非装饰器内容停止
            else:
                decorator_start = target_line
            
            # 从装饰器或定义行开始收集
            start_line = decorator_start
            code_lines.extend(lines[start_line:target_line + 1])
            
            # 收集函数/类体
            i = target_line + 1
            while i < len(lines):
                line = lines[i]
                
                # 空行或仍在当前块内的行
                if not line.strip() or (line and len(line) - len(line.lstrip()) > indent_level):
                    code_lines.append(line)
                    i += 1
                else:
                    # 达到相同或更低缩进级别，结束收集
                    break
            
            # 处理文档字符串
            if not include_docstring and code_lines:
                # 查找并移除文档字符串
                in_docstring = False
                docstring_start = -1
                docstring_quotes = None
                cleaned_lines = []
                
                for i, line in enumerate(code_lines):
                    stripped = line.strip()
                    
                    # 检查文档字符串开始
                    if not in_docstring and i > 0:  # 跳过定义行
                        if stripped.startswith('"""') or stripped.startswith("'''"):
                            in_docstring = True
                            docstring_start = i
                            docstring_quotes = '"""' if stripped.startswith('"""') else "'''"
                            # 检查单行文档字符串
                            if stripped.endswith(docstring_quotes) and len(stripped) > 6:
                                in_docstring = False
                                continue  # 跳过单行文档字符串
                            continue
                    
                    # 检查文档字符串结束
                    if in_docstring and stripped.endswith(docstring_quotes):
                        in_docstring = False
                        continue
                    
                    # 如果不在文档字符串中，添加行
                    if not in_docstring:
                        cleaned_lines.append(line)
                
                code_lines = cleaned_lines
            
            # 去除尾部空行
            while code_lines and not code_lines[-1].strip():
                code_lines.pop()
            
            # 组合结果
            extracted_code = '\n'.join(code_lines)
            
            result = f"=== Extracted {target_type} '{target}' from {file_path} ===\n"
            result += f"Location: {file_path}:{start_line + 1}\n\n"
            result += extracted_code
            
            return result
            
        except Exception as e:
            return f"Error in extract_code: {str(e)}"

    @tool("apply_diff", args_schema=DiffInput)
    def apply_diff(file_path: str, diff_content: str, reverse: bool = False) -> str:
        """应用 diff 补丁到文件
        
        将 unified diff 格式的补丁应用到指定文件。
        支持正向和反向应用补丁。
        
        Args:
            file_path: 相对文件路径
            diff_content: unified diff 格式的补丁内容
            reverse: 是否反向应用补丁
            
        Returns:
            str: 成功或错误消息
        """
        try:
            import difflib
            
            file_full_path = Path(work_dir) / file_path
            
            # 如果文件不存在且不是反向应用，尝试创建新文件
            if not file_full_path.exists() and not reverse:
                # 解析 diff 以获取新文件内容
                lines = diff_content.strip().split('\n')
                new_content = []
                in_hunk = False
                
                for line in lines:
                    if line.startswith('+') and not line.startswith('+++'):
                        new_content.append(line[1:])
                    elif line.startswith('@@'):
                        in_hunk = True
                    elif in_hunk and not line.startswith('-') and not line.startswith('\\'):
                        if line.startswith(' '):
                            new_content.append(line[1:])
                
                if new_content:
                    file_full_path.parent.mkdir(parents=True, exist_ok=True)
                    file_full_path.write_text('\n'.join(new_content), encoding='utf-8')
                    return f"Successfully created new file: {file_path}"
                else:
                    return f"Error: Could not extract content from diff for new file: {file_path}"
            
            if not file_full_path.exists():
                return f"File not found: {file_path}"
            
            # 读取当前文件内容
            original_content = file_full_path.read_text(encoding='utf-8')
            original_lines = original_content.splitlines(keepends=True)
            
            # 解析 unified diff
            diff_lines = diff_content.strip().split('\n')
            
            # 应用补丁
            result_lines = original_lines.copy()
            hunks = []
            current_hunk = None
            
            for line in diff_lines:
                # 解析 hunk 头部
                hunk_match = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
                if hunk_match:
                    if current_hunk:
                        hunks.append(current_hunk)
                    
                    old_start = int(hunk_match.group(1))
                    old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                    new_start = int(hunk_match.group(3))
                    new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1
                    
                    current_hunk = {
                        'old_start': old_start - 1,  # 转换为 0-based
                        'old_count': old_count,
                        'new_start': new_start - 1,
                        'new_count': new_count,
                        'lines': []
                    }
                elif current_hunk is not None:
                    if line and line[0] in ' +-':
                        current_hunk['lines'].append(line)
            
            if current_hunk:
                hunks.append(current_hunk)
            
            # 反向应用 hunks（从后往前，避免行号偏移）
            if reverse:
                # 反向模式：交换 + 和 -
                for hunk in hunks:
                    hunk['lines'] = [
                        '-' + line[1:] if line.startswith('+') else
                        '+' + line[1:] if line.startswith('-') else
                        line
                        for line in hunk['lines']
                    ]
            
            # 从后往前应用 hunks
            for hunk in reversed(hunks):
                old_start = hunk['old_start']
                old_lines = []
                new_lines = []
                
                for line in hunk['lines']:
                    if line.startswith('-'):
                        old_lines.append(line[1:])
                    elif line.startswith('+'):
                        new_lines.append(line[1:])
                    elif line.startswith(' '):
                        old_lines.append(line[1:])
                        new_lines.append(line[1:])
                
                # 验证原始内容匹配
                expected_lines = result_lines[old_start:old_start + len(old_lines)]
                if len(expected_lines) != len(old_lines):
                    return f"Error: Line count mismatch at line {old_start + 1}"
                
                # 比较时忽略换行符差异
                for i, (expected, actual) in enumerate(zip(expected_lines, old_lines)):
                    if expected.rstrip('\n\r') != actual.rstrip('\n\r'):
                        return f"Error: Content mismatch at line {old_start + i + 1}\nExpected: {expected.rstrip()}\nActual: {actual.rstrip()}"
                
                # 应用更改
                result_lines[old_start:old_start + len(old_lines)] = [
                    line if not line.endswith('\n') else line
                    for line in new_lines
                ]
            
            # 写入结果
            result_content = ''.join(result_lines)
            file_full_path.write_text(result_content, encoding='utf-8')
            
            action = "reverse applied" if reverse else "applied"
            return f"Successfully {action} diff to {file_path} ({len(hunks)} hunks)"
            
        except Exception as e:
            return f"Error applying diff: {str(e)}"

    @tool("google_search", args_schema=GoogleSearchInput)
    def google_search(query: str, site: Optional[str] = None, num: int = 10) -> str:
        """使用 Google Custom Search API 搜索信息
        
        使用 Google 搜索引擎查找相关信息。需要设置 GOOGLE_API_KEY 和 GOOGLE_CSE_ID 环境变量。
        
        Args:
            query: 搜索关键词
            site: 限定搜索的网站域名（可选）
            num: 返回结果数量（默认10）
            
        Returns:
            str: 搜索结果的格式化字符串
        """
        if not GOOGLE_SEARCH_AVAILABLE:
            return "Error: Google search dependencies not installed. Please install: pip install google-api-python-client requests beautifulsoup4"
        
        try:
            # 获取 API 凭证
            api_key = os.getenv('GOOGLE_API_KEY')
            cse_id = os.getenv('GOOGLE_CSE_ID')
            
            if not api_key or not cse_id:
                return "Error: GOOGLE_API_KEY or GOOGLE_CSE_ID not set in environment variables"
            
            # 设置代理（如果需要）
            proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
            if proxy:
                import googleapiclient.http
                import httplib2
                # 增加超时时间
                http = httplib2.Http(timeout=30, proxy_info=httplib2.ProxyInfo(
                    httplib2.socks.PROXY_TYPE_HTTP,
                    proxy.split('://')[1].split(':')[0],
                    int(proxy.split(':')[-1])
                ))
                service = build("customsearch", "v1", developerKey=api_key, http=http)
            else:
                # 即使没有代理也设置超时
                http = httplib2.Http(timeout=30)
                service = build("customsearch", "v1", developerKey=api_key, http=http)
            
            # 构建查询
            if site:
                query = f"{query} site:{site}"
            
            # 执行搜索
            res = service.cse().list(q=query, cx=cse_id, num=num).execute()
            
            if 'items' not in res:
                return "No search results found"
            
            # 格式化结果
            results = []
            for i, item in enumerate(res['items'], 1):
                title = item.get('title', 'No title')
                link = item.get('link', 'No link')
                snippet = item.get('snippet', 'No description')
                
                results.append(f"{i}. {title}\n   URL: {link}\n   Description: {snippet}")
            
            return f"=== Google Search Results for '{query}' ===\n\n" + "\n\n".join(results)
            
        except Exception as e:
            return f"Error performing Google search: {str(e)}"
    
    @tool("read_web_page", args_schema=WebPageInput)
    def read_web_page(url: str) -> str:
        """读取网页内容并提取纯文本
        
        获取指定 URL 的网页内容，去除 HTML 标签和 JavaScript，返回纯文本内容。
        
        Args:
            url: 要读取的网页 URL
            
        Returns:
            str: 网页的纯文本内容
        """
        if not GOOGLE_SEARCH_AVAILABLE:
            return "Error: Web scraping dependencies not installed. Please install: pip install requests beautifulsoup4"
        
        try:
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 设置代理（如果需要）
            proxies = {}
            proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
            if proxy:
                proxies = {
                    'http': proxy,
                    'https': proxy
                }
            
            # 发送请求
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            response.raise_for_status()
            
            # 自动检测编码
            response.encoding = response.apparent_encoding
            
            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除 script 和 style 标签
            for script_or_style in soup(['script', 'style']):
                script_or_style.extract()
            
            # 提取文本
            text = soup.get_text()
            
            # 清理文本（移除多余的空行和空格）
            lines = [line.strip() for line in text.splitlines()]
            lines = [line for line in lines if line]  # 移除空行
            text = '\n'.join(lines)
            
            # 限制文本长度（避免过长）
            max_length = 50000
            if len(text) > max_length:
                text = text[:max_length] + f"\n\n[Content truncated... Original length: {len(text)} characters]"
            
            return f"=== Web Page Content from {url} ===\n\n{text}"
            
        except requests.exceptions.Timeout:
            return f"Error: Request timeout when accessing {url}"
        except requests.exceptions.RequestException as e:
            return f"Error fetching web page: {str(e)}"
        except Exception as e:
            return f"Error reading web page: {str(e)}"

    # 构建工具列表
    tools = [
        write_file,
        read_file,
        create_directory,
        list_directory,
        execute_command,
        search_files,
        search_replace,
        edit_lines,
        find_symbol,
        extract_code,
        apply_diff
    ]
    
    # 只有在依赖可用时才添加搜索工具
    if GOOGLE_SEARCH_AVAILABLE:
        tools.extend([google_search, read_web_page])
    
    return tools