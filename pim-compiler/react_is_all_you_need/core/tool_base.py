#!/usr/bin/env python3
"""
Function基础类和通用工具类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    'Function',
    'ReadFileTool', 
    'WriteFileTool',
    'ExecuteCommandTool',
    'SessionQueryTool'
]


class Function(ABC):
    """函数基类 - 可被调用的函数/工具"""
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 parameters: Optional[Dict[str, Dict]] = None,
                 return_type: str = "Any"):
        """
        初始化函数
        
        Args:
            name: 函数名称
            description: 函数描述
            parameters: 参数定义 (OpenAI function格式)
                       {"param_name": {"type": "string", "description": "..."}}
            return_type: 返回值类型
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.return_type = return_type
        
        # 提取参数类型信息
        self.parameter_types = {}
        for param_name, param_def in self.parameters.items():
            if isinstance(param_def, dict):
                self.parameter_types[param_name] = param_def.get("type", "string")
            else:
                self.parameter_types[param_name] = "string"
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        执行函数 - 子类必须实现
        
        Args:
            **kwargs: 函数参数
            
        Returns:
            执行结果
        """
        pass
    
    def __call__(self, **kwargs) -> Any:
        """使Function可以像函数一样调用"""
        return self.execute(**kwargs)
    
    def to_openai_function(self) -> Dict:
        """
        转换为OpenAI function calling格式
        
        Returns:
            OpenAI格式的函数定义
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": []  # Grok可能对required字段敏感，先设为空数组
                }
            }
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


# ============= 通用工具类 =============

class ReadFileTool(Function):
    """读取文件工具"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="read_file",
            description="读取文件内容，支持分段读取大文件",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "文件路径。可以是相对路径（如'src/main.py'）或绝对路径（如'/home/user/file.txt'或'~/.agent/xxx/output.log'）"
                },
                "offset": {
                    "type": "integer",
                    "description": "起始字符位置（0表示文件开头，负数表示从文件末尾倒数）。用于分段读取大文件，默认0"
                },
                "limit": {
                    "type": "integer",
                    "description": "最多读取的字符数。默认2000字符，足够显示代码的关键部分。读取大文件时可分多次读取"
                }
            }
        )
        self.work_dir = Path(work_dir)
    
    def execute(self, **kwargs) -> str:
        path_str = kwargs["file_path"]
        
        # 处理绝对路径和~路径
        if path_str.startswith('~') or path_str.startswith('/'):
            # 绝对路径或用户目录路径
            file_path = Path(path_str).expanduser()
        else:
            # 相对路径
            file_path = self.work_dir / path_str
        
        if file_path.exists():
            # 确保offset和limit是整数
            offset = int(kwargs.get("offset", 0))
            limit = int(kwargs.get("limit", 2000))
            
            # 读取整个文件内容（这样可以按字符而不是字节处理）
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取文件的字节大小（用于显示）
            file_size = file_path.stat().st_size
            content_length = len(content)
            
            # 处理负偏移（从文件末尾开始）
            if offset < 0:
                offset = max(0, content_length + offset)
            
            # 确保offset不超过文件长度
            if offset >= content_length:
                return f"偏移量{offset}超过文件长度{content_length}字符"
            
            # 按字符切片（而不是字节）
            end_pos = min(offset + limit, content_length)
            result = content[offset:end_pos]
            
            # 添加位置信息（仅在分段读取时）
            if offset > 0 or end_pos < content_length:
                return f"[读取范围: {offset}-{end_pos}/{content_length}字符]\n{result}"
            
            return result
        return f"文件不存在: {path_str}"


class WriteFileTool(Function):
    """写入文件工具"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="write_file",
            description="创建或覆盖文件内容",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "相对于工作目录的文件路径，如'app/main.py'。如果目录不存在会自动创建"
                },
                "content": {
                    "type": "string",
                    "description": "完整的文件内容。注意：会完全覆盖原文件。如要追加请用append_file"
                }
            }
        )
        self.work_dir = Path(work_dir)
    
    def execute(self, **kwargs) -> str:
        file_path = self.work_dir / kwargs["file_path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(kwargs["content"])
        return f"文件已写入: {kwargs['file_path']}"


class AppendFileTool(Function):
    """追加文件工具"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="append_file",
            description="追加内容到文件末尾（如果文件不存在则创建）",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "相对于工作目录的文件路径，如'log.txt'、'data/output.md'。文件不存在会自动创建"
                },
                "content": {
                    "type": "string",
                    "description": "要追加到文件末尾的内容。不会覆盖原有内容，适合增量写入日志或文档"
                }
            }
        )
        self.work_dir = Path(work_dir)
    
    def execute(self, **kwargs) -> str:
        file_path = self.work_dir / kwargs["file_path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(kwargs["content"])
        return f"内容已追加到: {kwargs['file_path']}"


class ExecuteCommandTool(Function):
    """执行命令工具"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="execute_command",
            description="执行shell命令",
            parameters={
                "command": {
                    "type": "string",
                    "description": "Shell命令，如'ls -la'、'python test.py'、'npm install'。在工作目录执行，超时10秒"
                }
            }
        )
        self.work_dir = Path(work_dir)
    
    def execute(self, **kwargs) -> str:
        import subprocess
        result = subprocess.run(
            kwargs["command"],
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.work_dir,
            timeout=10
        )
        return result.stdout[:500] if result.stdout else "命令执行完成"


class SessionQueryTool(Function):
    """查询历史session工具"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="query_sessions",
            description="查询历史任务记录，获取之前的解决方案和经验。可用于：查找相似问题的处理方法、追溯文件修改历史、回顾错误和修复记录",
            parameters={
                "pattern": {
                    "type": "string",
                    "description": "搜索模式（可选）"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回数量限制",
                    "default": 10
                }
            }
        )
        self.work_dir = Path(work_dir)
        self.sessions_dir = self.work_dir / ".sessions"
    
    def execute(self, **kwargs) -> str:
        pattern = kwargs.get("pattern", None)
        limit = kwargs.get("limit", 10)
        
        if not self.sessions_dir.exists():
            return "没有找到session记录"
        
        # 获取所有session文件，按时间倒序
        session_files = sorted(self.sessions_dir.glob("*.md"), reverse=True)
        
        if pattern:
            # 如果提供了搜索模式，过滤文件
            import re
            regex = re.compile(pattern, re.IGNORECASE)
            filtered = []
            for f in session_files:
                try:
                    if regex.search(f.read_text(encoding='utf-8')):
                        filtered.append(f)
                except:
                    continue
            session_files = filtered
        
        # 限制返回数量
        session_files = session_files[:limit]
        
        if not session_files:
            return "没有找到匹配的session"
        
        # 构建结果
        results = []
        for session_file in session_files:
            # 读取文件前几行获取摘要
            try:
                lines = session_file.read_text(encoding='utf-8').split('\n')[:10]
                summary = '\n'.join(lines)
                results.append(f"## {session_file.name}\n{summary}\n...")
            except:
                continue
        
        return '\n\n'.join(results) if results else "无法读取session文件"