#!/usr/bin/env python3
"""
斜杠命令条件反射拦截器
让Agent创建的工具可以通过斜杠命令直接触发，实现脊髓反射
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class SlashCommandInterceptor:
    """斜杠命令拦截器（条件反射）"""

    def __init__(self, agent_name: str):
        """
        初始化拦截器

        Args:
            agent_name: Agent名称，用于定位home目录
        """
        self.agent_name = agent_name
        self.agent_home = Path(f"~/.agent/{agent_name}").expanduser()
        self.registry_file = self.agent_home / "slash_commands.json"
        self.usage_log = self.agent_home / "slash_usage.log"

        # 确保目录存在
        self.agent_home.mkdir(parents=True, exist_ok=True)

        # 加载命令注册表
        self.load_registry()

    def load_registry(self) -> None:
        """加载斜杠命令注册表"""
        if self.registry_file.exists():
            try:
                self.commands = json.loads(self.registry_file.read_text())
            except:
                self.commands = {}
        else:
            self.commands = {}
            self.save_registry()

    def save_registry(self) -> None:
        """保存注册表到文件"""
        self.registry_file.write_text(
            json.dumps(self.commands, indent=2, ensure_ascii=False)
        )

    def register(self, command: str, tool_path: str,
                description: str = "", aliases: list = None) -> bool:
        """
        注册新的斜杠命令

        Args:
            command: 命令名（不含斜杠）
            tool_path: 工具路径
            description: 命令描述
            aliases: 命令别名列表

        Returns:
            是否注册成功
        """
        # 主命令注册
        self.commands[command] = {
            "tool": str(Path(tool_path).expanduser()),
            "description": description,
            "created": datetime.now().isoformat(),
            "usage_count": 0
        }

        # 注册别名
        if aliases:
            for alias in aliases:
                self.commands[alias] = {
                    "tool": str(Path(tool_path).expanduser()),
                    "description": f"{description} (alias of /{command})",
                    "alias_of": command,
                    "created": datetime.now().isoformat(),
                    "usage_count": 0
                }

        self.save_registry()
        return True

    def intercept(self, message: str) -> Optional[str]:
        """
        拦截并处理斜杠命令

        Args:
            message: 用户输入消息

        Returns:
            处理结果，如果不是斜杠命令返回None
        """
        # 检查是否是斜杠命令
        if not message.startswith("/"):
            return None

        # 解析命令和参数
        parts = message.strip().split()
        command = parts[0][1:]  # 去掉斜杠
        args = parts[1:] if len(parts) > 1 else []

        # 查找命令
        if command not in self.commands:
            # 尝试模糊匹配
            similar = self.find_similar_commands(command)
            if similar:
                return f"❓ 未知命令: /{command}\n💡 你是想用: {', '.join(f'/{cmd}' for cmd in similar)}?"
            return f"❓ 未知命令: /{command}\n使用 /help 查看所有可用命令"

        # 特殊命令处理
        if command == "help":
            return self.show_help()

        if command == "list":
            return self.list_commands()

        # 执行工具
        tool_info = self.commands[command]
        tool_path = Path(tool_info["tool"])

        # 检查工具是否存在
        if not tool_path.exists():
            return f"❌ 工具不存在: {tool_path}"

        # 执行工具（条件反射）
        result = self.execute_tool(tool_path, args)

        # 记录使用
        self.log_usage(command, args, result)

        # 更新使用统计
        self.commands[command]["usage_count"] += 1
        self.commands[command]["last_used"] = datetime.now().isoformat()
        self.save_registry()

        return result

    def execute_tool(self, tool_path: Path, args: list) -> str:
        """
        执行外部工具

        Args:
            tool_path: 工具路径
            args: 命令参数

        Returns:
            执行结果
        """
        try:
            # 构建命令
            if tool_path.suffix == ".py":
                cmd = ["python3", str(tool_path)] + args
            elif tool_path.suffix == ".sh":
                cmd = ["bash", str(tool_path)] + args
            else:
                # 假设是可执行文件
                cmd = [str(tool_path)] + args

            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.agent_home
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip() or f"Exit code: {result.returncode}"
                return f"❌ 执行失败: {error_msg}"

        except subprocess.TimeoutExpired:
            return "❌ 执行超时（10秒）"
        except Exception as e:
            return f"❌ 执行错误: {str(e)}"

    def show_help(self) -> str:
        """显示帮助信息"""
        help_text = ["📚 可用的斜杠命令：\n"]

        # 按使用频率排序
        sorted_cmds = sorted(
            self.commands.items(),
            key=lambda x: x[1].get("usage_count", 0),
            reverse=True
        )

        for cmd, info in sorted_cmds:
            if "alias_of" not in info:  # 主命令
                # 查找别名
                aliases = [
                    k for k, v in self.commands.items()
                    if v.get("alias_of") == cmd
                ]

                alias_text = f" (别名: {', '.join(f'/{a}' for a in aliases)})" if aliases else ""
                usage = info.get("usage_count", 0)

                help_text.append(
                    f"  /{cmd}{alias_text}\n"
                    f"    {info.get('description', '无描述')}\n"
                    f"    使用次数: {usage}\n"
                )

        help_text.append("\n💡 使用 /list 查看详细统计")
        return "\n".join(help_text)

    def list_commands(self) -> str:
        """列出所有命令及统计"""
        stats = ["📊 斜杠命令统计：\n"]

        total_usage = sum(
            info.get("usage_count", 0)
            for info in self.commands.values()
            if "alias_of" not in info
        )

        stats.append(f"总调用次数: {total_usage}\n")
        stats.append(f"注册命令数: {len([c for c in self.commands if 'alias_of' not in self.commands[c]])}\n")

        # 最常用命令
        top_commands = sorted(
            [(k, v) for k, v in self.commands.items() if "alias_of" not in v],
            key=lambda x: x[1].get("usage_count", 0),
            reverse=True
        )[:5]

        if top_commands:
            stats.append("\n🏆 最常用命令：")
            for cmd, info in top_commands:
                count = info.get("usage_count", 0)
                if count > 0:
                    stats.append(f"  /{cmd}: {count}次")

        return "\n".join(stats)

    def find_similar_commands(self, input_cmd: str) -> list:
        """查找相似的命令"""
        similar = []
        for cmd in self.commands:
            if input_cmd in cmd or cmd in input_cmd:
                similar.append(cmd)
        return similar[:3]  # 最多返回3个

    def log_usage(self, command: str, args: list, result: str) -> None:
        """记录命令使用"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "args": args,
            "success": not result.startswith("❌")
        }

        # 追加到日志文件
        with self.usage_log.open("a") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def auto_register_from_tools_dir(self) -> int:
        """
        自动从external_tools目录注册所有工具

        Returns:
            注册的工具数量
        """
        tools_dir = self.agent_home / "external_tools"
        if not tools_dir.exists():
            return 0

        registered = 0
        for tool_file in tools_dir.glob("*"):
            if tool_file.is_file() and tool_file.suffix in [".py", ".sh"]:
                cmd_name = tool_file.stem.replace("_", "-")

                # 跳过已注册的
                if cmd_name in self.commands:
                    continue

                self.register(
                    command=cmd_name,
                    tool_path=str(tool_file),
                    description=f"Auto-registered from {tool_file.name}"
                )
                registered += 1

        return registered

    def suggest_new_commands(self) -> list:
        """
        基于使用模式建议新命令

        Returns:
            建议列表
        """
        suggestions = []

        # 分析日志找出频繁的参数组合
        if self.usage_log.exists():
            patterns = {}

            with self.usage_log.open() as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        cmd = entry["command"]
                        args_key = " ".join(entry.get("args", []))

                        key = f"{cmd} {args_key}"
                        patterns[key] = patterns.get(key, 0) + 1
                    except:
                        continue

            # 找出高频模式
            for pattern, count in patterns.items():
                if count >= 5:  # 使用5次以上
                    suggestions.append({
                        "pattern": pattern,
                        "count": count,
                        "suggestion": f"可以创建专门的命令来优化"
                    })

        return suggestions


def create_slash_command_tool_generator():
    """创建一个生成斜杠命令工具的辅助函数"""

    template = '''#!/usr/bin/env python3
"""
{description}
Generated by Agent: {agent_name}
Created: {timestamp}
"""

import sys
import json
from pathlib import Path


def main():
    """主函数"""
    # 解析参数
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    # TODO: 实现具体功能
    {implementation}

    # 返回结果
    print(result)


if __name__ == "__main__":
    main()
'''

    return template


# 使用示例
if __name__ == "__main__":
    # 测试拦截器
    interceptor = SlashCommandInterceptor("test_agent")

    # 注册命令
    interceptor.register(
        command="hello",
        tool_path="/tmp/hello.sh",
        description="Say hello",
        aliases=["hi", "hey"]
    )

    # 测试拦截
    print(interceptor.intercept("/hello world"))
    print(interceptor.intercept("/help"))
    print(interceptor.intercept("not a command"))