#!/usr/bin/env python3
"""
Agent Simple CLI - 无需额外依赖的简化版CLI
"""

import os
import sys
import readline
from pathlib import Path
from datetime import datetime

# 设置Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.react_agent_minimal import ReactAgentMinimal

# 历史文件
HISTORY_FILE = Path.home() / ".agent_simple_history"

class SimpleAgentCLI:
    """简化版Agent CLI - 无需rich库"""

    def __init__(self, agent_name="assistant", model="deepseek"):
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

        self.work_dir = os.getcwd()
        self.agent = None
        self.setup_history()

    def setup_history(self):
        """设置命令历史"""
        if HISTORY_FILE.exists():
            readline.read_history_file(HISTORY_FILE)
        readline.set_history_length(1000)

    def save_history(self):
        """保存命令历史"""
        readline.write_history_file(HISTORY_FILE)

    def initialize_agent(self):
        """初始化Agent"""
        try:
            # 创建Agent - 让Agent从知识文件理解配置
            # Agent已自动包含CreateAgentTool（分形同构原则）
            self.agent = ReactAgentMinimal(
                name=self.agent_name,
                description=f"CLI Agent - {self.agent_name}",
                work_dir=self.work_dir,
                model=self.model,  # 直接使用用户指定的模型
                knowledge_files=[],  # 空知识文件，更快
                stateful=False  # 临时：避免超时问题
            )

            print(f"✅ Agent '{self.agent_name}' 初始化成功")
            return True

        except Exception as e:
            print(f"❌ 初始化失败：{e}")
            return False

    def show_help(self):
        """显示帮助"""
        help_text = """
可用命令：
  /help         - 显示此帮助
  /exit, /quit  - 退出
  /clear        - 清屏
  /status       - 显示状态
  /model <name> - 切换模型 (deepseek/kimi/claude/grok)
  /agent <name> - 切换Agent
  /learning     - 执行@learning
  /memory <txt> - 记住信息
  /compact      - 压缩历史
  输入文本      - 与Agent对话
        """
        print(help_text)

    def show_status(self):
        """显示状态"""
        print(f"""
状态信息
--------
Agent: {self.agent_name}
模型: {self.model}
工作目录: {self.work_dir}
状态: {'已初始化' if self.agent else '未初始化'}
        """)

    def process_command(self, cmd):
        """处理命令"""
        if cmd == "/help":
            self.show_help()
        elif cmd in ["/exit", "/quit"]:
            self.save_history()
            print("\n👋 再见!")
            sys.exit(0)
        elif cmd == "/clear":
            os.system('clear' if os.name == 'posix' else 'cls')
        elif cmd == "/status":
            self.show_status()
        elif cmd.startswith("/model "):
            self.model = cmd.split()[1]
            print(f"已切换到模型: {self.model}")
            print("需要重新初始化Agent")
        elif cmd.startswith("/agent "):
            self.agent_name = cmd.split()[1]
            print(f"切换到Agent: {self.agent_name}")
            self.initialize_agent()
        elif cmd == "/learning":
            if self.agent:
                print("正在执行@learning...")
                result = self.agent.execute(task="@learning")
                print(result)
        elif cmd.startswith("/memory "):
            if self.agent:
                text = cmd[8:]
                result = self.agent.execute(task=f"@memory 记住：{text}")
                print("✅ 已记住")
        elif cmd == "/compact":
            print("压缩功能开发中...")
        else:
            return False
        return True

    def run(self):
        """运行主循环"""
        print("=" * 50)
        print("   Agent Simple CLI - 轻量级Agent对话界面")
        print("=" * 50)
        print("输入 /help 查看帮助\n")

        # 初始化Agent
        if not self.initialize_agent():
            print("⚠️  Agent初始化失败，但仍可使用命令")

        # 主循环
        while True:
            try:
                # 获取输入
                user_input = input(f"\n{self.agent_name}> ").strip()

                if not user_input:
                    continue

                # 处理命令
                if user_input.startswith("/"):
                    if self.process_command(user_input):
                        continue

                # 处理消息
                if not self.agent:
                    print("请先初始化Agent")
                    self.initialize_agent()
                    continue

                print("\n🤔 思考中...")
                response = self.agent.execute(task=user_input)
                print("\n📝 回复:")
                print("-" * 40)
                print(response)
                print("-" * 40)

            except KeyboardInterrupt:
                print("\n使用 /exit 退出")
            except Exception as e:
                print(f"❌ 错误：{e}")


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='Simple Agent CLI')
    parser.add_argument('-a', '--agent', default='assistant', help='Agent名称')
    parser.add_argument('-m', '--model', default='deepseek',
                       help='模型 (deepseek/kimi/claude/grok)')

    args = parser.parse_args()

    cli = SimpleAgentCLI(agent_name=args.agent, model=args.model)
    cli.run()


if __name__ == "__main__":
    main()