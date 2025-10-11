#!/usr/bin/env python3
"""临时版本：使用stateful=False避免卡住问题"""
import sys
import os

# 复用agent_cli.py的代码，只修改stateful参数
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并patch
import agent_cli

# Patch初始化方法
original_init = agent_cli.AgentCLI.initialize_agent

def patched_init(self):
    """修改后的初始化 - 使用stateful=False"""
    try:
        from core.react_agent_minimal import ReactAgentMinimal
        from rich.console import Console
        console = Console()

        model_key = self.model.split('/')[0] if '/' in self.model else self.model
        if model_key in self.model_configs:
            config = self.model_configs[model_key]
            model = config['model']
            base_url = config['base_url']
            api_key = os.getenv(config['api_key_env'])
        else:
            model = self.model
            base_url = 'https://api.deepseek.com/v1'
            api_key = os.getenv('DEEPSEEK_API_KEY')

        if not api_key:
            console.print(f"[red]错误：未找到API密钥[/red]")
            return False

        # 关键修改：stateful=False
        self.agent = ReactAgentMinimal(
            name=self.agent_name,
            description=f"CLI Agent - {self.agent_name}",
            work_dir=self.work_dir,
            model=model,
            base_url=base_url,
            api_key=api_key,
            knowledge_files=['knowledge/learning_functions.md'],
            stateful=False  # 临时修改
        )

        console.print("[yellow]⚠️  临时使用stateful=False模式[/yellow]")
        console.print("[dim]Agent已自动包含create_agent工具（分形同构原则）[/dim]")
        return True

    except Exception as e:
        console.print(f"[red]初始化失败：{e}[/red]")
        return False

agent_cli.AgentCLI.initialize_agent = patched_init

if __name__ == "__main__":
    agent_cli.main()
