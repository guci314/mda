#!/usr/bin/env python3
"""
Agent CLI 主入口

提供智能体命令行接口
"""

import click
import sys
from pathlib import Path

# 添加项目路径到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent_cli.commands.agent_command import agent
from agent_cli.commands.run_command import run
from agent_cli.commands.test_command import test


@click.group()
@click.version_option(version='1.0.0', prog_name='agent-cli')
def cli():
    """Agent CLI - 智能体开发和测试工具
    
    一个支持多动作执行的智能体框架，提供开发、运行和测试功能。
    """
    pass


# 注册命令
cli.add_command(agent)
cli.add_command(run)
cli.add_command(test)


if __name__ == '__main__':
    cli()