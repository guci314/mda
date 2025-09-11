#!/usr/bin/env python3
"""
扩展版ExecuteCommand工具 - 支持自定义超时
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from tool_base import Function


class ExecuteCommandExtended(Function):
    """执行命令工具（支持自定义超时）"""
    
    def __init__(self, work_dir):
        super().__init__(
            name="execute_command_ext",
            description="执行shell命令（支持自定义超时）",
            parameters={
                "command": {
                    "type": "string",
                    "description": "Shell命令，如'ls -la'、'python test.py'、'npm install'"
                },
                "timeout": {
                    "type": "integer",
                    "description": "超时时间（秒），默认30秒，最大300秒",
                    "default": 30
                },
                "background": {
                    "type": "boolean",
                    "description": "是否后台执行（立即返回），默认False",
                    "default": False
                }
            }
        )
        self.work_dir = Path(work_dir)
    
    def execute(self, **kwargs) -> str:
        import subprocess
        
        command = kwargs["command"]
        timeout = min(kwargs.get("timeout", 30), 300)  # 最大300秒
        background = kwargs.get("background", False)
        
        if background:
            # 后台执行，立即返回
            try:
                subprocess.Popen(
                    command,
                    shell=True,
                    cwd=self.work_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return f"✅ 命令已在后台执行: {command}"
            except Exception as e:
                return f"❌ 后台执行失败: {e}"
        else:
            # 前台执行，等待结果
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.work_dir,
                    timeout=timeout
                )
                output = result.stdout[:1000] if result.stdout else "命令执行完成"
                if result.returncode != 0 and result.stderr:
                    output += f"\n错误: {result.stderr[:500]}"
                return output
            except subprocess.TimeoutExpired:
                return f"❌ 命令超时（{timeout}秒）: {command}"
            except Exception as e:
                return f"❌ 执行失败: {e}"