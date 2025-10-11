#!/usr/bin/env python3
"""
EditFileTool - 安全的文件编辑工具
支持查找替换，避免覆盖整个文件
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from tool_base import Function


class EditFileTool(Function):
    """编辑文件工具 - 支持查找替换，避免覆盖整个文件"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="edit_file",
            description="编辑文件内容，通过查找替换的方式修改，避免覆盖整个文件",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "相对于工作目录的文件路径"
                },
                "old_text": {
                    "type": "string",
                    "description": "要查找的文本（必须完全匹配，包括缩进和空格）"
                },
                "new_text": {
                    "type": "string",
                    "description": "替换后的新文本"
                },
                "occurrence": {
                    "type": "integer",
                    "description": "替换第几个匹配项（1表示第一个，-1表示全部替换），默认1",
                    "default": 1
                }
            }
        )
        self.work_dir = Path(work_dir)
    
    def execute(self, **kwargs) -> str:
        # 处理文件路径，支持~展开和绝对路径
        input_path = kwargs["file_path"]
        if input_path.startswith("~"):
            # 展开~为用户home目录
            file_path = Path(input_path).expanduser()
        elif Path(input_path).is_absolute():
            # 如果是绝对路径，直接使用
            file_path = Path(input_path)
        else:
            # 相对路径，基于work_dir
            file_path = self.work_dir / input_path

        old_text = kwargs["old_text"]
        new_text = kwargs["new_text"]
        occurrence = kwargs.get("occurrence", 1)
        
        if not file_path.exists():
            return f"❌ 文件不存在: {kwargs['file_path']}"
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查old_text是否存在
            if old_text not in content:
                # 提供更有帮助的错误信息
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if len(old_text) > 50:  # 对于长文本，检查部分匹配
                        if old_text[:50] in line:
                            return f"❌ 找不到完全匹配的文本。在第{i+1}行找到部分匹配。请确保包含完整的缩进和空格。"
                return f"❌ 在文件中找不到要替换的文本。请确保文本完全匹配（包括缩进和换行）。"
            
            # 执行替换
            if occurrence == -1:
                # 替换所有匹配项
                new_content = content.replace(old_text, new_text)
                count = content.count(old_text)
                message = f"✅ 已替换所有{count}处匹配"
            else:
                # 替换指定的匹配项
                parts = content.split(old_text)
                if occurrence > len(parts) - 1:
                    return f"❌ 只找到{len(parts)-1}个匹配项，无法替换第{occurrence}个"
                
                # 重建内容，只替换指定位置
                new_parts = []
                for i in range(len(parts)):
                    new_parts.append(parts[i])
                    if i < len(parts) - 1:
                        if i == occurrence - 1:
                            new_parts.append(new_text)
                        else:
                            new_parts.append(old_text)
                new_content = ''.join(new_parts)
                message = f"✅ 已替换第{occurrence}个匹配项"
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return f"{message}: {kwargs['file_path']}"
            
        except Exception as e:
            return f"❌ 编辑失败: {e}"


class InsertLineTool(Function):
    """在指定行插入内容"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="insert_line",
            description="在文件的指定行号插入新内容",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "相对于工作目录的文件路径"
                },
                "line_number": {
                    "type": "integer",
                    "description": "行号（1开始），0表示文件开头，-1表示文件末尾"
                },
                "content": {
                    "type": "string",
                    "description": "要插入的内容"
                }
            }
        )
        self.work_dir = Path(work_dir)
    
    def execute(self, **kwargs) -> str:
        # 处理文件路径，支持~展开和绝对路径
        input_path = kwargs["file_path"]
        if input_path.startswith("~"):
            # 展开~为用户home目录
            file_path = Path(input_path).expanduser()
        elif Path(input_path).is_absolute():
            # 如果是绝对路径，直接使用
            file_path = Path(input_path)
        else:
            # 相对路径，基于work_dir
            file_path = self.work_dir / input_path

        line_number = kwargs["line_number"]
        content = kwargs["content"]
        
        if not file_path.exists():
            return f"❌ 文件不存在: {kwargs['file_path']}"
        
        try:
            # 读取文件行
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 处理特殊行号
            if line_number == 0:
                # 插入到文件开头
                lines.insert(0, content + '\n')
            elif line_number == -1:
                # 追加到文件末尾
                lines.append('\n' + content)
            elif 1 <= line_number <= len(lines) + 1:
                # 插入到指定行
                lines.insert(line_number - 1, content + '\n')
            else:
                return f"❌ 行号{line_number}超出范围（文件有{len(lines)}行）"
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return f"✅ 已在第{line_number}行插入内容: {kwargs['file_path']}"
            
        except Exception as e:
            return f"❌ 插入失败: {e}"


class DeleteLinesTool(Function):
    """删除指定范围的行"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="delete_lines",
            description="删除文件中指定范围的行",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "相对于工作目录的文件路径"
                },
                "start_line": {
                    "type": "integer",
                    "description": "起始行号（1开始）"
                },
                "end_line": {
                    "type": "integer",
                    "description": "结束行号（包含），如果不提供则只删除start_line",
                    "default": None
                }
            }
        )
        self.work_dir = Path(work_dir)
    
    def execute(self, **kwargs) -> str:
        # 处理文件路径，支持~展开和绝对路径
        input_path = kwargs["file_path"]
        if input_path.startswith("~"):
            # 展开~为用户home目录
            file_path = Path(input_path).expanduser()
        elif Path(input_path).is_absolute():
            # 如果是绝对路径，直接使用
            file_path = Path(input_path)
        else:
            # 相对路径，基于work_dir
            file_path = self.work_dir / input_path

        start_line = kwargs["start_line"]
        end_line = kwargs.get("end_line", start_line)
        
        if not file_path.exists():
            return f"❌ 文件不存在: {kwargs['file_path']}"
        
        try:
            # 读取文件行
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 验证行号
            if start_line < 1 or start_line > len(lines):
                return f"❌ 起始行号{start_line}超出范围（文件有{len(lines)}行）"
            if end_line < start_line or end_line > len(lines):
                return f"❌ 结束行号{end_line}无效"
            
            # 删除指定范围的行
            del lines[start_line-1:end_line]
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            if start_line == end_line:
                return f"✅ 已删除第{start_line}行: {kwargs['file_path']}"
            else:
                return f"✅ 已删除第{start_line}-{end_line}行: {kwargs['file_path']}"
            
        except Exception as e:
            return f"❌ 删除失败: {e}"