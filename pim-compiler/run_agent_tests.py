#!/usr/bin/env python3
"""
运行 Agent CLI 测试的入口脚本
这个脚本应该从项目根目录运行
"""
import sys
from pathlib import Path

# 确保可以导入 agent_cli
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入并运行测试
from agent_cli.test_cli import main

if __name__ == "__main__":
    print("运行 Agent CLI 测试...")
    print(f"项目根目录: {project_root}")
    main()