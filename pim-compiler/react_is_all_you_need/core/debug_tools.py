"""
调试工具模块

提供调试Agent专用的工具集，包括：
- 调试笔记管理
- Python语法错误修复
- 调试状态压缩和归档
"""

import os
import json
import ast
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from langchain_core.tools import tool


def compress_debug_notes(notes_path: str, max_keep_errors: int = 10, max_keep_strategies: int = 20):
    """压缩调试笔记，防止文件过大
    
    Args:
        notes_path: 调试笔记文件路径
        max_keep_errors: 保留的最大错误数
        max_keep_strategies: 保留的最大策略数
    """
    try:
        with open(notes_path, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        # 归档原文件
        archive_dir = Path(notes_path).parent / "debug_archive"
        archive_dir.mkdir(exist_ok=True)
        archive_name = f"debug_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy(notes_path, archive_dir / archive_name)
        print(f"   已归档到: {archive_dir / archive_name}")
        
        # 压缩错误历史 - 只保留最近的N个
        if 'error_history' in notes and len(notes['error_history']) > max_keep_errors:
            error_items = list(notes['error_history'].items())
            notes['error_history'] = dict(error_items[-max_keep_errors:])
        
        # 压缩修复尝试 - 只保留最近的
        if 'fix_attempts' in notes and len(notes['fix_attempts']) > max_keep_strategies:
            notes['fix_attempts'] = notes['fix_attempts'][-max_keep_strategies:]
        
        # 压缩测试结果历史
        if 'test_results_history' in notes and len(notes['test_results_history']) > 10:
            notes['test_results_history'] = notes['test_results_history'][-10:]
        
        # 保留成功策略但限制数量
        if 'successful_strategies' in notes and len(notes['successful_strategies']) > max_keep_strategies:
            # 按成功率和置信度排序，保留最好的
            sorted_strategies = sorted(
                notes['successful_strategies'],
                key=lambda x: (x.get('confidence', 0), x.get('success_count', 0)),
                reverse=True
            )
            notes['successful_strategies'] = sorted_strategies[:max_keep_strategies]
        
        # 重置迭代计数
        notes['current_iteration'] = 0
        notes['created_at'] = datetime.now().isoformat()
        
        # 保存压缩后的版本
        with open(notes_path, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2)
        
        original_size = os.path.getsize(archive_dir / archive_name)
        new_size = os.path.getsize(notes_path)
        print(f"   压缩完成: {original_size//1024}KB -> {new_size//1024}KB")
        
        # 清理超过7天的归档
        cutoff = datetime.now().timestamp() - (7 * 24 * 3600)
        for old_file in archive_dir.glob("debug_notes_*.json"):
            if old_file.stat().st_mtime < cutoff:
                old_file.unlink()
                print(f"   已删除旧归档: {old_file.name}")
                
    except Exception as e:
        print(f"⚠️ 压缩调试笔记失败: {e}")


def create_init_debug_notes_tool(work_dir: str):
    """创建初始化调试笔记的工具
    
    Args:
        work_dir: 工作目录路径
    
    Returns:
        init_debug_notes工具函数
    """
    @tool
    def init_debug_notes() -> str:
        """初始化或读取调试笔记"""
        notes_path = os.path.join(work_dir, 'debug_notes.json')
        
        if os.path.exists(notes_path):
            with open(notes_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 限制返回内容大小，只返回摘要
                notes = json.loads(content)
                summary = {
                    "session_id": notes.get("session_id"),
                    "current_iteration": notes.get("current_iteration", 0),
                    "error_count": len(notes.get("error_history", {})),
                    "successful_strategies_count": len(notes.get("successful_strategies", [])),
                    "failed_strategies_count": len(notes.get("failed_strategies", []))
                }
                return f"Debug notes exists with {summary['error_count']} errors tracked, {summary['successful_strategies_count']} successful strategies"
        else:
            initial_notes = {
                "session_id": f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "current_iteration": 0,
                "error_history": {},
                "fix_attempts": [],
                "successful_strategies": [],
                "failed_strategies": [],
                "test_results_history": []
            }
            with open(notes_path, 'w', encoding='utf-8') as f:
                json.dump(initial_notes, f, indent=2)
            return f"Created new debug notes: {notes_path}"
    
    return init_debug_notes


def create_fix_python_syntax_errors_tool(work_dir: str):
    """创建修复Python语法错误的工具
    
    Args:
        work_dir: 工作目录路径
    
    Returns:
        fix_python_syntax_errors工具函数
    """
    @tool
    def fix_python_syntax_errors(file_path: str) -> str:
        """【推荐】修复Python文件的语法错误 - 重写整个文件而不是逐行修复
        
        这个工具专门用于修复Python语法错误（缩进、括号不匹配等）。
        它会读取整个文件，修复所有语法问题，然后重写整个文件。
        
        Args:
            file_path: 要修复的Python文件路径
            
        Returns:
            修复结果信息
        """
        full_path = os.path.join(work_dir, file_path)
        
        if not os.path.exists(full_path):
            return f"文件不存在: {file_path}"
        
        # 读取文件内容
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析以检测语法错误
        original_error = None
        try:
            ast.parse(content)
            return f"文件 {file_path} 没有语法错误"
        except (SyntaxError, IndentationError) as e:
            original_error = f"{e.__class__.__name__}: {e.msg} at line {e.lineno}"
        
        # 修复策略1：智能括号匹配
        def fix_brackets(text):
            """修复括号不匹配问题"""
            lines = text.split('\n')
            fixed_lines = []
            bracket_stack = []
            
            for line_num, line in enumerate(lines):
                # 统计各种括号
                for char in line:
                    if char in '({[':
                        bracket_stack.append(char)
                    elif char in ')}]':
                        expected = {'(': ')', '{': '}', '[': ']'}
                        if bracket_stack and expected.get(bracket_stack[-1]) == char:
                            bracket_stack.pop()
                        else:
                            # 发现不匹配的括号，尝试修复
                            if char == '}' and not bracket_stack:
                                # 多余的闭合括号，可能需要删除
                                line = line.replace(char, '', 1)
                
                fixed_lines.append(line)
            
            # 如果还有未闭合的括号，在文件末尾添加
            if bracket_stack:
                closing = ''
                for bracket in reversed(bracket_stack):
                    if bracket == '(':
                        closing += ')'
                    elif bracket == '{':
                        closing += '}'
                    elif bracket == '[':
                        closing += ']'
                if closing:
                    fixed_lines.append(closing)
            
            return '\n'.join(fixed_lines)
        
        # 修复策略2：修复JSON格式问题
        def fix_json_syntax(text):
            """修复JSON格式的语法问题"""
            # 修复缺少逗号的情况
            text = re.sub(r'"\s*\n\s*"', '",\n"', text)
            text = re.sub(r'(\d)\s*\n\s*"', r'\1,\n"', text)
            text = re.sub(r'}\s*\n\s*"', r'},\n"', text)
            text = re.sub(r']\s*\n\s*"', r'],\n"', text)
            return text
        
        # 修复策略3：智能缩进修复
        def fix_indentation(text):
            """修复缩进问题"""
            lines = text.split('\n')
            fixed_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    fixed_lines.append('')
                    continue
                
                # 减少缩进的情况
                if stripped.startswith(('else:', 'elif ', 'except:', 'finally:', 'except ', 'elif:')):
                    indent_level = max(0, indent_level - 1)
                    fixed_lines.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped.startswith(('return', 'break', 'continue', 'pass', 'raise')):
                    fixed_lines.append('    ' * indent_level + stripped)
                    if indent_level > 0 and not line.endswith(':'):
                        indent_level = max(0, indent_level - 1)
                elif stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'with ', 'try:')):
                    fixed_lines.append('    ' * indent_level + stripped)
                    if stripped.endswith(':'):
                        indent_level += 1
                elif stripped == '}' or stripped == ']' or stripped == ')':
                    indent_level = max(0, indent_level - 1)
                    fixed_lines.append('    ' * indent_level + stripped)
                else:
                    # 普通行
                    fixed_lines.append('    ' * indent_level + stripped)
                    if stripped.endswith(':'):
                        indent_level += 1
                    elif stripped in ('}', ']', ')'):
                        indent_level = max(0, indent_level - 1)
            
            return '\n'.join(fixed_lines)
        
        # 依次应用修复策略
        fixed_content = content
        fixed_content = fix_brackets(fixed_content)
        fixed_content = fix_json_syntax(fixed_content)
        fixed_content = fix_indentation(fixed_content)
        
        # 写回文件
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # 再次检查是否修复成功
        try:
            ast.parse(fixed_content)
            return f"成功修复 {file_path} 的语法错误:\n原始错误: {original_error}\n\n文件已完全重写。"
        except (SyntaxError, IndentationError) as e:
            new_error = f"{e.__class__.__name__}: {e.msg} at line {e.lineno}"
            return f"尝试修复 {file_path}:\n原始错误: {original_error}\n当前错误: {new_error}\n\n部分修复成功，建议使用 write_file 工具手动重写。"
    
    return fix_python_syntax_errors


def check_and_compress_debug_notes(work_dir: str, max_size_kb: int = 50):
    """检查并压缩调试笔记（如果需要）
    
    Args:
        work_dir: 工作目录
        max_size_kb: 最大文件大小（KB）
    """
    notes_path = os.path.join(work_dir, 'debug_notes.json')
    if os.path.exists(notes_path):
        size = os.path.getsize(notes_path)
        if size > max_size_kb * 1024:
            print(f"📦 调试笔记大小 {size//1024}KB，正在压缩...")
            compress_debug_notes(notes_path)


# 导出的工具创建函数
def create_debug_tools(work_dir: str):
    """创建所有调试相关的工具
    
    Args:
        work_dir: 工作目录路径
    
    Returns:
        包含所有调试工具的列表
    """
    return [
        create_init_debug_notes_tool(work_dir),
        create_fix_python_syntax_errors_tool(work_dir)
    ]