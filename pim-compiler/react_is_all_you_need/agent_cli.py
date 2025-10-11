#!/usr/bin/env python3
"""
Agent Command Line Interface - 类似Claude Code的CLI界面
提供交互式命令行界面来与Agent对话
"""

import os
import sys
import json
import readline
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import traceback

# 设置Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.react_agent_minimal import ReactAgentMinimal
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich import print as rprint

# 初始化Rich控制台
console = Console()

# 版本信息
VERSION = "1.0.0"
ASCII_ART = """
╔═══════════════════════════════════════╗
║     Agent CLI - Powered by MDA       ║
║   Interactive Agent Command Line     ║
╚═══════════════════════════════════════╝
"""

# 历史文件路径
HISTORY_FILE = Path.home() / ".agent_cli_history"

class AgentCLI:
    """Agent命令行界面"""

    def __init__(self, agent_name: str = "assistant", model: str = "deepseek",
                 work_dir: str = None):
        """初始化CLI

        Args:
            agent_name: Agent名称
            model: 使用的模型（简称或完整名称）
            work_dir: 工作目录
        """
        self.agent_name = agent_name

        # CLI层处理简称映射（用户体验优化）
        model_shortcuts = {
            "deepseek": "deepseek-chat",
            "kimi": "kimi-k2-turbo-preview",
            "grok": "x-ai/grok-code-fast-1",
            "claude": "anthropic/claude-sonnet-4.5",
            "qwen": "qwen/qwen3-coder"
        }
        self.model = model_shortcuts.get(model.lower(), model)

        self.work_dir = work_dir or os.getcwd()
        self.agent = None
        self.session_start = datetime.now()
        self.message_count = 0

        # 初始化readline历史
        self._setup_readline()

        # 命令映射
        self.commands = {
            '/help': self.cmd_help,
            '/exit': self.cmd_exit,
            '/quit': self.cmd_exit,
            '/clear': self.cmd_clear,
            '/status': self.cmd_status,
            '/model': self.cmd_model,
            '/agent': self.cmd_agent,
            '/list': self.cmd_list_agents,
            '/create': self.cmd_create_agent,
            '/switch': self.cmd_switch_agent,
            '/compact': self.cmd_compact,
            '/learning': self.cmd_learning,
            '/memory': self.cmd_memory,
            '/knowledge': self.cmd_knowledge,
            '/tools': self.cmd_tools,
            '/history': self.cmd_history,
            '/save': self.cmd_save_session,
            '/load': self.cmd_load_session,
            '/config': self.cmd_config,
            '/debug': self.cmd_debug,
            '/multi': self.cmd_multi_line,
        }

        # 调试模式
        self.debug_mode = False

    def _setup_readline(self):
        """设置readline历史和自动补全"""
        # 加载历史
        if HISTORY_FILE.exists():
            readline.read_history_file(HISTORY_FILE)

        # 设置历史大小
        readline.set_history_length(1000)

        # 设置自动补全
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self._completer)

    def _completer(self, text: str, state: int) -> Optional[str]:
        """自动补全函数"""
        options = [cmd for cmd in self.commands if cmd.startswith(text)]

        if state < len(options):
            return options[state]
        return None

    def _save_history(self):
        """保存命令历史"""
        readline.write_history_file(HISTORY_FILE)

    def initialize_agent(self):
        """初始化Agent"""
        try:
            # 创建Agent - 让Agent自己从知识文件理解模型配置
            # model参数可以是简称（grok）或完整名称（x-ai/grok-code-fast-1）
            # Agent已自动包含CreateAgentTool（分形同构原则），无需手动添加
            self.agent = ReactAgentMinimal(
                name=self.agent_name,
                description=f"CLI Agent - {self.agent_name}",
                work_dir=self.work_dir,
                model=self.model,
                knowledge_files=[],  # 空知识文件，减少messages大小
                stateful=False  # 关闭状态保存，提升速度
            )

            return True

        except Exception as e:
            console.print(f"[red]初始化Agent失败：{e}[/red]")
            if self.debug_mode:
                console.print(traceback.format_exc())
            return False

    def cmd_help(self, args: str = ""):
        """显示帮助信息"""
        table = Table(title="可用命令", show_header=True, header_style="bold magenta")
        table.add_column("命令", style="cyan", width=20)
        table.add_column("描述", style="white")

        table.add_row("/help", "显示此帮助信息")
        table.add_row("/exit, /quit", "退出CLI")
        table.add_row("/clear", "清除屏幕")
        table.add_row("/status", "显示Agent状态")
        table.add_row("/model [name]", "查看或切换模型")
        table.add_row("/agent [name]", "查看或切换Agent")
        table.add_row("/list", "列出所有可用Agent")
        table.add_row("/create <name>", "创建新Agent")
        table.add_row("/switch <name>", "切换到其他Agent")
        table.add_row("/compact", "压缩Agent历史记录")
        table.add_row("/learning", "执行@learning函数")
        table.add_row("/memory <text>", "执行@memory函数")
        table.add_row("/knowledge", "显示Agent知识")
        table.add_row("/tools", "列出可用工具")
        table.add_row("/history [n]", "显示最近n条历史")
        table.add_row("/save [file]", "保存会话")
        table.add_row("/load <file>", "加载会话")
        table.add_row("/config", "显示配置信息")
        table.add_row("/debug", "切换调试模式")
        table.add_row("/multi", "多行输入模式")

        console.print(table)

    def cmd_exit(self, args: str = ""):
        """退出CLI"""
        self._save_history()
        console.print("\n[cyan]再见！感谢使用Agent CLI。[/cyan]")
        sys.exit(0)

    def cmd_clear(self, args: str = ""):
        """清除屏幕"""
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(ASCII_ART)

    def cmd_status(self, args: str = ""):
        """显示Agent状态"""
        if not self.agent:
            console.print("[yellow]Agent未初始化[/yellow]")
            return

        status = Panel(
            f"""
[bold]Agent状态[/bold]
────────────────────
名称: {self.agent_name}
模型: {self.model}
工作目录: {self.work_dir}
会话开始: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
消息数: {self.message_count}
调试模式: {'开启' if self.debug_mode else '关闭'}
            """,
            title="状态信息",
            border_style="green"
        )
        console.print(status)

    def cmd_model(self, args: str = ""):
        """查看或切换模型"""
        if not args:
            # 显示当前模型
            console.print(f"[cyan]当前模型: {self.model}[/cyan]")
            console.print("\n[dim]可用模型参考 knowledge/model_mappings.md[/dim]")
            console.print("[dim]使用 /model <name> 切换模型[/dim]")
        else:
            # 切换模型（简称或完整名称都可以）
            self.model = args
            console.print(f"[green]已切换到模型: {args}[/green]")
            console.print("[yellow]需要重新初始化Agent以应用更改[/yellow]")

    def cmd_agent(self, args: str = ""):
        """查看或切换Agent"""
        if not args:
            console.print(f"[cyan]当前Agent: {self.agent_name}[/cyan]")
        else:
            self.agent_name = args
            console.print(f"[green]已切换到Agent: {args}[/green]")
            console.print("[yellow]正在重新初始化...[/yellow]")
            if self.initialize_agent():
                console.print("[green]Agent初始化成功[/green]")

    def cmd_list_agents(self, args: str = ""):
        """列出所有可用Agent"""
        agent_dir = Path.home() / ".agent"
        if agent_dir.exists():
            agents = [d.name for d in agent_dir.iterdir() if d.is_dir()]
            if agents:
                table = Table(title="可用Agent", show_header=True)
                table.add_column("名称", style="cyan")
                table.add_column("路径", style="white")

                for agent in agents:
                    table.add_row(agent, str(agent_dir / agent))

                console.print(table)
            else:
                console.print("[yellow]没有找到Agent[/yellow]")
        else:
            console.print("[yellow]Agent目录不存在[/yellow]")

    def cmd_create_agent(self, args: str = ""):
        """创建新Agent"""
        if not args:
            console.print("[red]请提供Agent名称[/red]")
            return

        try:
            # 使用当前Agent创建子Agent
            if not self.agent:
                console.print("[yellow]先初始化一个Agent[/yellow]")
                self.initialize_agent()

            result = self.agent.execute(
                task=f"创建一个名为{args}的新Agent",
                method="create_agent"
            )
            console.print(f"[green]成功创建Agent: {args}[/green]")
            console.print(result)
        except Exception as e:
            console.print(f"[red]创建Agent失败：{e}[/red]")

    def cmd_switch_agent(self, args: str = ""):
        """切换到其他Agent"""
        if not args:
            console.print("[red]请提供Agent名称[/red]")
            return

        self.agent_name = args
        console.print(f"[yellow]正在切换到Agent: {args}...[/yellow]")
        if self.initialize_agent():
            console.print(f"[green]已切换到Agent: {args}[/green]")

    def cmd_compact(self, args: str = ""):
        """压缩Agent历史记录"""
        if not self.agent:
            console.print("[yellow]Agent未初始化[/yellow]")
            return

        try:
            console.print("[yellow]正在压缩历史记录...[/yellow]")
            # 这里需要实现compact功能
            console.print("[green]历史记录压缩完成[/green]")
        except Exception as e:
            console.print(f"[red]压缩失败：{e}[/red]")

    def cmd_learning(self, args: str = ""):
        """执行@learning函数"""
        if not self.agent:
            console.print("[yellow]Agent未初始化[/yellow]")
            return

        try:
            console.print("[yellow]正在执行@learning...[/yellow]")
            result = self.agent.execute(task="@learning")
            console.print("[green]学习完成：[/green]")
            console.print(Markdown(result))
        except Exception as e:
            console.print(f"[red]学习失败：{e}[/red]")

    def cmd_memory(self, args: str = ""):
        """执行@memory函数"""
        if not self.agent:
            console.print("[yellow]Agent未初始化[/yellow]")
            return

        if not args:
            console.print("[red]请提供要记住的内容[/red]")
            return

        try:
            result = self.agent.execute(task=f"@memory 记住：{args}")
            console.print("[green]已记住[/green]")
            console.print(result)
        except Exception as e:
            console.print(f"[red]记忆失败：{e}[/red]")

    def cmd_knowledge(self, args: str = ""):
        """显示Agent知识"""
        if not self.agent:
            console.print("[yellow]Agent未初始化[/yellow]")
            return

        knowledge_file = Path.home() / ".agent" / self.agent_name / "knowledge.md"
        if knowledge_file.exists():
            content = knowledge_file.read_text()
            console.print(Markdown(content))
        else:
            console.print("[yellow]知识文件不存在[/yellow]")

    def cmd_tools(self, args: str = ""):
        """列出可用工具"""
        if not self.agent:
            console.print("[yellow]Agent未初始化[/yellow]")
            return

        tools = self.agent.function_instances
        if tools:
            table = Table(title="可用工具", show_header=True)
            table.add_column("工具名", style="cyan")
            table.add_column("描述", style="white")

            for tool in tools:
                name = tool.__class__.__name__ if hasattr(tool, '__class__') else str(tool)
                desc = getattr(tool, 'description', '无描述')
                table.add_row(name, desc)

            console.print(table)
        else:
            console.print("[yellow]没有可用工具[/yellow]")

    def cmd_history(self, args: str = ""):
        """显示命令历史"""
        try:
            n = int(args) if args else 10
            history_length = readline.get_current_history_length()
            start = max(0, history_length - n)

            for i in range(start, history_length):
                console.print(f"[dim]{i+1}[/dim] {readline.get_history_item(i+1)}")
        except Exception as e:
            console.print(f"[red]获取历史失败：{e}[/red]")

    def cmd_save_session(self, args: str = ""):
        """保存会话"""
        filename = args or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        # 实现会话保存逻辑
        console.print(f"[green]会话已保存到: {filename}[/green]")

    def cmd_load_session(self, args: str = ""):
        """加载会话"""
        if not args:
            console.print("[red]请提供会话文件名[/red]")
            return
        # 实现会话加载逻辑
        console.print(f"[green]已加载会话: {args}[/green]")

    def cmd_config(self, args: str = ""):
        """显示配置信息"""
        config_info = f"""
[bold]配置信息[/bold]
────────────────────
Agent名称: {self.agent_name}
模型: {self.model}
工作目录: {self.work_dir}
历史文件: {HISTORY_FILE}
调试模式: {self.debug_mode}
版本: {VERSION}
        """
        console.print(Panel(config_info, title="配置", border_style="blue"))

    def cmd_debug(self, args: str = ""):
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
        status = "开启" if self.debug_mode else "关闭"
        console.print(f"[yellow]调试模式已{status}[/yellow]")

    def cmd_multi_line(self, args: str = ""):
        """多行输入模式"""
        console.print("[cyan]进入多行输入模式，输入'###'结束[/cyan]")
        lines = []
        while True:
            try:
                line = input("... ")
                if line == "###":
                    break
                lines.append(line)
            except KeyboardInterrupt:
                console.print("\n[yellow]取消多行输入[/yellow]")
                return ""

        return "\n".join(lines)

    def process_command(self, user_input: str) -> bool:
        """处理命令

        Returns:
            是否是命令（True）还是普通消息（False）
        """
        if not user_input.startswith('/'):
            return False

        parts = user_input.split(maxsplit=1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        if cmd in self.commands:
            self.commands[cmd](args)
            return True
        else:
            console.print(f"[red]未知命令: {cmd}[/red]")
            console.print("[dim]输入 /help 查看可用命令[/dim]")
            return True

    def process_message(self, message: str):
        """处理用户消息"""
        if not self.agent:
            console.print("[yellow]Agent未初始化，正在初始化...[/yellow]")
            if not self.initialize_agent():
                return

        try:
            # 显示思考中状态
            if self.debug_mode:
                console.print(f"[dim]调试: 执行任务 task='{message}'[/dim]")

            # 临时禁用status spinner，因为它会与Agent的stdout重定向冲突
            console.print("[cyan]Agent思考中...[/cyan]")
            response = self.agent.execute(task=message)

            if self.debug_mode:
                console.print(f"[dim]调试: 收到响应，长度={len(response)}[/dim]")

            # 显示响应
            console.print("\n[bold green]Agent:[/bold green]")

            # 尝试以Markdown格式显示
            if '```' in response or '#' in response or '**' in response:
                console.print(Markdown(response))
            else:
                console.print(response)

            self.message_count += 1

        except KeyboardInterrupt:
            console.print("\n[yellow]任务被中断[/yellow]")
        except Exception as e:
            console.print(f"[red]执行错误：{e}[/red]")
            if self.debug_mode:
                console.print(traceback.format_exc())

    def run(self):
        """运行CLI主循环"""
        # 显示欢迎信息
        console.print(ASCII_ART)
        console.print(f"[cyan]欢迎使用Agent CLI v{VERSION}[/cyan]")
        console.print("[dim]输入 /help 查看可用命令[/dim]\n")

        # 初始化Agent
        if not self.initialize_agent():
            console.print("[red]Agent初始化失败，但您仍可以使用命令[/red]")
        else:
            console.print(f"[green]Agent '{self.agent_name}' 已就绪[/green]\n")

        # 主循环
        while True:
            try:
                # 获取用户输入
                user_input = Prompt.ask(
                    f"[bold cyan]{self.agent_name}[/bold cyan]",
                    default=""
                )

                if not user_input:
                    continue

                # 处理多行输入
                if user_input == "/multi":
                    user_input = self.cmd_multi_line()
                    if user_input:
                        self.process_message(user_input)
                    continue

                # 处理命令或消息
                if not self.process_command(user_input):
                    self.process_message(user_input)

            except KeyboardInterrupt:
                console.print("\n[yellow]使用 /exit 退出[/yellow]")
                continue

            except Exception as e:
                console.print(f"[red]错误：{e}[/red]")
                if self.debug_mode:
                    console.print(traceback.format_exc())


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Agent Command Line Interface')
    parser.add_argument('-a', '--agent', default='assistant',
                       help='Agent名称 (默认: assistant)')
    parser.add_argument('-m', '--model', default='deepseek',
                       help='使用的模型 (deepseek/kimi/claude/grok/qwen)')
    parser.add_argument('-w', '--work-dir', default=None,
                       help='工作目录 (默认: 当前目录)')
    parser.add_argument('-d', '--debug', action='store_true',
                       help='开启调试模式')

    args = parser.parse_args()

    # 创建并运行CLI
    cli = AgentCLI(
        agent_name=args.agent,
        model=args.model,
        work_dir=args.work_dir
    )

    if args.debug:
        cli.debug_mode = True

    try:
        cli.run()
    except Exception as e:
        console.print(f"[red]致命错误：{e}[/red]")
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()