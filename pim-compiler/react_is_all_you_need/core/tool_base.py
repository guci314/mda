#!/usr/bin/env python3
"""
Function基础类和通用工具类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path


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
                    "required": [
                        key for key, param in self.parameters.items() 
                        if (param.get("required", True) if isinstance(param, dict) else True)
                    ]
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
                    "description": "要读取的文件路径"
                },
                "offset": {
                    "type": "integer",
                    "description": "起始字符位置，默认0"
                },
                "limit": {
                    "type": "integer",
                    "description": "读取字符数限制，默认2000"
                }
            }
        )
        self.work_dir = Path(work_dir)
    
    def execute(self, **kwargs) -> str:
        file_path = self.work_dir / kwargs["file_path"]
        if file_path.exists():
            # 确保offset和limit是整数
            offset = int(kwargs.get("offset", 0))
            limit = int(kwargs.get("limit", 2000))
            
            with open(file_path, 'r', encoding='utf-8') as f:
                file_size = file_path.stat().st_size
                
                # 处理负偏移（从文件末尾开始）
                if offset < 0:
                    offset = max(0, file_size + offset)
                
                # 移动到指定位置
                if offset > 0:
                    f.seek(offset)
                
                # 读取指定长度
                content = f.read(limit)
                
                # 添加位置信息（仅在分段读取时）
                if offset > 0 or (len(content) == limit and file_size > limit):
                    end_pos = offset + len(content)
                    return f"[读取范围: {offset}-{end_pos}/{file_size}字节]\n{content}"
                
                return content
        return f"文件不存在: {kwargs['file_path']}"


class WriteFileTool(Function):
    """写入文件工具"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="write_file",
            description="创建或覆盖文件内容",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "要写入的文件路径"
                },
                "content": {
                    "type": "string",
                    "description": "要写入的文件内容"
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


class ExecuteCommandTool(Function):
    """执行命令工具"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="execute_command",
            description="执行shell命令",
            parameters={
                "command": {
                    "type": "string",
                    "description": "要执行的命令"
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