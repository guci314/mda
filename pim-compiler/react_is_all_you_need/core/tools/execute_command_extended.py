#!/usr/bin/env python3
"""
扩展版ExecuteCommand工具 - 支持自定义超时
修复版：解决PTY实现的死锁问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from tool_base import Function
import subprocess
import time
import threading


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
                # 特殊处理claude命令 - 使用-p选项确保非交互式
                if 'claude' in command and '-p' not in command:
                    # 如果是claude命令但没有-p选项，添加提示
                    return f"⚠️ 检测到claude命令。请使用 'claude -p \"your question\"' 格式以避免交互式模式。\n当前命令: {command}"

                # 使用subprocess.run，对于需要交互的命令会自动失败而不是卡住
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.work_dir,
                    # 设置环境变量，确保非交互式
                    env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
                )

                # 组合stdout和stderr
                output = result.stdout
                if result.stderr:
                    output += f"\n{result.stderr}"

                # 限制输出长度
                if len(output) > 1000:
                    output = output[:1000] + "\n... (输出过长，已截断)"

                if result.returncode != 0:
                    return f"❌ 命令执行失败 (退出码: {result.returncode})\n{output}"

                return output if output.strip() else "命令执行完成"

            except subprocess.TimeoutExpired:
                return f"❌ 命令超时（{timeout}秒）: {command}"
            except Exception as e:
                return f"❌ 执行失败: {e}\n提示: 如果是交互式命令，请确保使用非交互模式"