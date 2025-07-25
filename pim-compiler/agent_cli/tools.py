"""
LangChain Tools for agent_cli
使用 LangChain 的标准工具协议实现各种操作
"""
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import subprocess
import sys
import os

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field


# Input schemas for tools
class ReadFileInput(BaseModel):
    """读取文件的输入参数"""
    path: str = Field(description="要读取的文件路径")


class WriteFileInput(BaseModel):
    """写入文件的输入参数"""
    path: str = Field(description="要写入的文件路径")
    content: str = Field(description="要写入的内容")


class ListFilesInput(BaseModel):
    """列出文件的输入参数"""
    path: str = Field(default=".", description="要列出的目录路径")
    pattern: Optional[str] = Field(default=None, description="文件匹配模式，如 '*.py'")


# 注释掉冗余的输入模型
# class AnalyzeInput(BaseModel):
#     """分析内容的输入参数"""
#     content: str = Field(description="要分析的内容")
#     analysis_type: str = Field(description="分析类型")
#
#
# class GenerateInput(BaseModel):
#     """生成内容的输入参数"""
#     prompt: str = Field(description="生成提示")
#     context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class PythonCodeInput(BaseModel):
    """执行 Python 代码的输入参数"""
    code: str = Field(description="要执行的 Python 代码")


class BashCommandInput(BaseModel):
    """执行 Bash 命令的输入参数"""
    command: str = Field(description="要执行的 Bash 命令")
    cwd: Optional[str] = Field(default=None, description="工作目录")


# Tool implementations
def read_file_func(path: str) -> str:
    """读取文件内容"""
    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"Error: File '{path}' does not exist"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file_func(path: str, content: str) -> str:
    """写入文件内容"""
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def list_files_func(path: str = ".", pattern: Optional[str] = None) -> str:
    """列出目录中的文件"""
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return f"Error: Directory '{path}' does not exist"
        
        if not dir_path.is_dir():
            return f"Error: '{path}' is not a directory"
        
        files = []
        if pattern:
            files = list(dir_path.glob(pattern))
        else:
            files = list(dir_path.iterdir())
        
        result = f"Files in {path}:\n"
        for f in sorted(files):
            if f.is_dir():
                result += f"  [DIR] {f.name}\n"
            else:
                result += f"  {f.name}\n"
        
        return result
    except Exception as e:
        return f"Error listing files: {str(e)}"


# 注释掉冗余的工具函数
# def analyze_func(content: str, analysis_type: str) -> str:
#     """分析内容（这是一个模拟实现，实际应该调用 LLM）"""
#     # 这里应该调用 LLM 进行分析
#     # 目前只是返回一个模拟结果
#     return f"Analysis of type '{analysis_type}':\n- Content length: {len(content)} characters\n- Analysis complete"
#
#
# def generate_func(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
#     """生成内容（这是一个模拟实现，实际应该调用 LLM）"""
#     # 这里应该调用 LLM 生成内容
#     # 目前只是返回一个模拟结果
#     context_str = json.dumps(context) if context else "No context"
#     return f"Generated content based on prompt: {prompt[:50]}...\nContext: {context_str}"


def run_python_func(code: str) -> str:
    """执行 Python 代码"""
    try:
        # 创建一个新的字典作为执行环境
        exec_globals = {}
        exec_locals = {}
        
        # 捕获输出
        from io import StringIO
        import contextlib
        
        output = StringIO()
        with contextlib.redirect_stdout(output):
            exec(code, exec_globals, exec_locals)
        
        result = output.getvalue()
        if not result:
            # 如果没有输出，尝试返回最后一个表达式的值
            if exec_locals:
                last_value = list(exec_locals.values())[-1]
                result = str(last_value)
            else:
                result = "Code executed successfully (no output)"
        
        return result
    except Exception as e:
        return f"Error executing Python code: {str(e)}"


def run_bash_func(command: str, cwd: Optional[str] = None) -> str:
    """执行 Bash 命令 - 修复了大括号扩展问题"""
    try:
        # 检测是否包含大括号扩展
        if '{' in command and '}' in command and ',' in command:
            # 使用 bash -c 确保大括号扩展正常工作
            # 使用 /bin/bash 而不是默认的 /bin/sh
            result = subprocess.run(
                ['/bin/bash', '-c', command],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, 'SHELL': '/bin/bash'}  # 确保使用 bash
            )
        else:
            # 普通命令直接执行
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30,
                executable='/bin/bash'  # 明确指定使用 bash
            )
        
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        
        if result.returncode != 0:
            output += f"\nCommand failed with return code: {result.returncode}"
        
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


# Create LangChain tools
read_file_tool = StructuredTool.from_function(
    func=read_file_func,
    name="read_file",
    description="读取文件内容。用于查看代码、配置文件或任何文本文件。",
    args_schema=ReadFileInput,
    return_direct=False
)

write_file_tool = StructuredTool.from_function(
    func=write_file_func,
    name="write_file",
    description="写入内容到文件。用于创建新文件或覆盖现有文件。",
    args_schema=WriteFileInput,
    return_direct=False
)

list_files_tool = StructuredTool.from_function(
    func=list_files_func,
    name="list_files",
    description="列出目录中的文件和子目录。用于探索项目结构。",
    args_schema=ListFilesInput,
    return_direct=False
)

# 注释掉冗余的工具定义
# analyze_tool = StructuredTool.from_function(
#     func=analyze_func,
#     name="analyze",
#     description="分析给定内容。用于理解代码、文档或数据。",
#     args_schema=AnalyzeInput,
#     return_direct=False
# )
#
# generate_tool = StructuredTool.from_function(
#     func=generate_func,
#     name="generate",
#     description="基于提示生成内容。用于创建代码、文档或其他文本。",
#     args_schema=GenerateInput,
#     return_direct=False
# )

python_repl_tool = StructuredTool.from_function(
    func=run_python_func,
    name="python_repl",
    description="执行 Python 代码并返回结果。用于测试、计算或运行脚本。",
    args_schema=PythonCodeInput,
    return_direct=False
)

bash_tool = StructuredTool.from_function(
    func=run_bash_func,
    name="bash",
    description="执行 Bash 命令。用于系统操作、运行程序或管理文件。",
    args_schema=BashCommandInput,
    return_direct=False
)


# Tool registry
AVAILABLE_TOOLS = {
    "read_file": read_file_tool,
    "write_file": write_file_tool,
    "list_files": list_files_tool,
    "python_repl": python_repl_tool,
    "bash": bash_tool,
}


def get_all_tools() -> List[StructuredTool]:
    """获取所有可用的工具"""
    return list(AVAILABLE_TOOLS.values())


def get_tool_by_name(name: str) -> Optional[StructuredTool]:
    """根据名称获取工具"""
    return AVAILABLE_TOOLS.get(name)


def get_tools_description() -> str:
    """获取所有工具的描述信息"""
    descriptions = []
    for name, tool in AVAILABLE_TOOLS.items():
        descriptions.append(f"- {name}: {tool.description}")
    return "\n".join(descriptions)