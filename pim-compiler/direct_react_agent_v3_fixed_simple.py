#!/usr/bin/env python3
"""简化版本 - 使用近似的 token 计数避免错误"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 复制原文件内容
exec(open('direct_react_agent_v3_fixed.py').read().replace(
    'ConversationSummaryBufferMemory',
    'ConversationBufferWindowMemory'
).replace(
    'max_token_limit=self.config.max_token_limit',
    'k=50'  # 使用固定窗口大小而不是 token 限制
))