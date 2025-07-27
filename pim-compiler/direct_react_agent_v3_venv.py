#!/usr/bin/env python3
"""ReactAgentGenerator v3 - 虚拟环境专用版本（禁用token计数补丁）"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 暂时禁用 token 计数补丁
os.environ['DISABLE_TOKEN_PATCH'] = '1'

# 导入原始文件
exec(open('direct_react_agent_v3_fixed.py').read())