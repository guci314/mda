#!/usr/bin/env python3
"""
系统命令拦截器 - 处理内置系统命令
优先级最高，在所有其他拦截器之前执行
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Any


class SystemInterceptor:
    """系统命令拦截器"""

    def __init__(self, agent):
        """
        Args:
            agent: ReactAgentMinimal实例的引用
        """
        self.agent = agent

    def intercept(self, command: str) -> Optional[str]:
        """
        拦截并处理系统命令

        Args:
            command: 用户输入的命令

        Returns:
            处理结果，如果不是系统命令返回None
        """
        if not command.startswith("/"):
            return None

        cmd = command.lower().strip().split()[0]

        # 系统命令映射
        handlers = {
            "/compact": self.handle_compact,
            "/save": self.handle_save,
            "/status": self.handle_status,
            "/help": self.handle_help,
            "/clear": self.handle_clear,
            "/home": self.handle_home,
        }

        handler = handlers.get(cmd)
        if handler:
            return handler(command)

        return None  # 不是系统命令

    def handle_compact(self, command: str) -> str:
        """处理/compact命令 - 触发消息压缩"""
        print("\n🧠 手动触发Compact压缩...")

        if len(self.agent.messages) <= 1:
            return "📝 当前对话历史为空，无需压缩"

        # 显示压缩前的信息
        original_count = len(self.agent.messages)
        original_tokens = self.agent._count_tokens(self.agent.messages)
        print(f"  压缩前: {original_count} 条消息, 约 {original_tokens} tokens")

        # 执行压缩
        self.agent.messages = self.agent._compact_messages(
            self.agent.messages, manual=True
        )

        # 显示压缩后的信息
        new_count = len(self.agent.messages)
        new_tokens = self.agent._count_tokens(self.agent.messages)
        print(f"  压缩后: {new_count} 条消息, 约 {new_tokens} tokens")
        print(f"  压缩率: {(1 - new_tokens/original_tokens)*100:.1f}%")

        # 保存压缩结果
        self.agent._save_compact_memory()
        agent_home = Path.home() / ".agent" / self.agent.name
        print(f"  💾 已保存到: {agent_home}/compact.md")

        # 触发自动保存状态（compact后应该保存完整状态）
        self.agent._auto_save_state()
        print(f"  💾 状态已保存到: {agent_home}/state.json")

        return f"✨ Compact压缩完成！{original_count}条消息 → {new_count}条消息"

    def handle_save(self, command: str) -> str:
        """处理/save命令 - 手动保存Agent状态（通常不需要，因为会自动保存）"""
        # 调用自动保存方法
        self.agent._auto_save_state()

        state_file = Path.home() / ".agent" / self.agent.name / "state.json"

        # 获取文件大小和任务计数
        size = state_file.stat().st_size if state_file.exists() else 0
        task_count = getattr(self.agent, '_task_count', 0)

        return f"💾 手动保存完成\n📂 文件: {state_file}\n📊 大小: {size:,} bytes\n🔢 任务数: {task_count}\n\n💡 提示: 状态会在每次执行后自动保存"

    def handle_status(self, command: str) -> str:
        """处理/status命令 - 显示Agent状态"""
        status = []
        status.append(f"🤖 Agent: {self.agent.name}")
        status.append(f"📂 Home: ~/.agent/{self.agent.name}/")
        status.append(f"💬 消息数: {len(self.agent.messages)}")

        # Token统计
        tokens = self.agent._count_tokens(self.agent.messages)
        threshold = self.agent.compress_config.get("threshold", 50000)
        status.append(f"🎯 Tokens: {tokens}/{threshold}")

        # 工具统计
        tools_dir = Path.home() / ".agent" / self.agent.name / "external_tools"
        if tools_dir.exists():
            tool_count = len(list(tools_dir.glob("*.py")))
            status.append(f"🔧 工具数: {tool_count}")

        # 记忆状态
        if self.agent.compact_memory:
            status.append("🧠 有压缩记忆")

        return "\n".join(status)

    def handle_help(self, command: str) -> str:
        """处理/help命令 - 显示帮助"""
        help_text = """
📚 系统命令帮助：

/compact   - 手动触发消息压缩
/save      - 保存Agent状态
/status    - 显示Agent状态
/home      - 显示Agent home目录
/clear     - 清空对话历史（保留系统提示）
/help      - 显示此帮助

🔧 工具命令：
/<tool_name> [args] - 执行external_tools目录中的工具

示例：
/compact
/inventory_manager list
/report generate monthly
"""
        return help_text.strip()

    def handle_clear(self, command: str) -> str:
        """处理/clear命令 - 清空对话历史"""
        # 保留系统提示词
        if self.agent.messages and self.agent.messages[0]["role"] == "system":
            self.agent.messages = [self.agent.messages[0]]
        else:
            self.agent.messages = []

        return "🗑️ 对话历史已清空"

    def handle_home(self, command: str) -> str:
        """处理/home命令 - 显示home目录信息"""
        agent_home = Path.home() / ".agent" / self.agent.name

        if not agent_home.exists():
            return f"📂 Home目录不存在: {agent_home}"

        info = [f"📂 Agent Home: {agent_home}"]

        # 列出主要文件
        files = []
        for pattern in ["*.md", "*.json", "external_tools/*.py"]:
            files.extend(agent_home.glob(pattern))

        if files:
            info.append("\n📄 文件列表:")
            for f in sorted(files)[:10]:  # 最多显示10个
                size = f.stat().st_size
                info.append(f"  - {f.name} ({size} bytes)")

            if len(files) > 10:
                info.append(f"  ... 还有 {len(files)-10} 个文件")

        return "\n".join(info)