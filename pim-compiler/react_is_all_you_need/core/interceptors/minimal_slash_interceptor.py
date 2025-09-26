#!/usr/bin/env python3
"""
极简斜杠命令拦截器
/工具名 参数 → 执行 ~/.agent/{agent_name}/external_tools/工具名.py 参数
"""

import subprocess
from pathlib import Path
from typing import Optional


class MinimalSlashInterceptor:
    """极简斜杠命令拦截器"""

    def __init__(self, agent_name: str):
        """
        Args:
            agent_name: Agent名字，用于构造工具路径
        """
        self.agent_name = agent_name
        self.tools_dir = Path(f"~/.agent/{agent_name}/external_tools").expanduser()

    def intercept(self, message: str) -> Optional[str]:
        """
        拦截斜杠命令，直接执行对应Python文件

        Args:
            message: 用户输入，如 "/inventory_manager list"

        Returns:
            执行结果，如果不是斜杠命令返回None
        """
        if not message.startswith("/"):
            return None

        # 解析命令：/inventory_manager list → inventory_manager.py list
        parts = message[1:].split()
        if not parts:
            return None

        # 处理文件扩展名（支持 /order_tool 和 /order_tool.py）
        tool_name = parts[0]
        if '.' in tool_name:
            tool_name = tool_name.split('.')[0]  # 去掉扩展名
        args = parts[1:] if len(parts) > 1 else []

        # 构造完整路径：~/.agent/{agent_name}/external_tools/{tool_name}.py
        tool_path = self.tools_dir / f"{tool_name}.py"

        if not tool_path.exists():
            # 文件不存在，不是工具命令，返回None让LLM处理
            return None

        # 执行工具（条件反射）
        try:
            result = subprocess.run(
                ["python3", str(tool_path)] + args,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.tools_dir)
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"❌ 执行失败: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return "❌ 执行超时"
        except Exception as e:
            return f"❌ 错误: {str(e)}"


# 使用示例
if __name__ == "__main__":
    # 创建拦截器
    interceptor = MinimalSlashInterceptor("inventory_manager_grok_code_fast__14279")

    # 测试命令
    test_commands = [
        "/inventory_manager list",
        "/inventory_manager query 001",
        "/inventory_manager update 002 +10",
        "这不是斜杠命令"
    ]

    for cmd in test_commands:
        print(f"\n>>> {cmd}")
        result = interceptor.intercept(cmd)
        if result is not None:
            print(f"⚡ 条件反射: {result}")
        else:
            print("→ 交给LLM处理")