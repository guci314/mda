#!/usr/bin/env python3
"""临时版本：禁用stdout重定向以避免卡住"""

import os
import sys

# 设置环境变量禁用stdout重定向
os.environ['AGENT_NO_REDIRECT'] = '1'

# 然后正常启动CLI
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_cli import main

if __name__ == "__main__":
    main()
