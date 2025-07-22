#!/usr/bin/env python3
"""MDA - 模型驱动架构命令行工具"""

import sys
import asyncio
from pathlib import Path

# 添加 pim-engine/src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "pim-engine" / "src"))

from mda_orchestrator import main

if __name__ == "__main__":
    asyncio.run(main())