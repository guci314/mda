#!/usr/bin/env python3
"""
运行 PIM Compiler Chatbot
"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置工作目录为 pim-compiler
os.chdir(project_root)

# 导入并运行
from pim_compiler_chatbot import main

if __name__ == "__main__":
    main()