#!/usr/bin/env python3
"""ReactAgent v3 - 无记忆模式专用版本（避免版本冲突）"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 直接运行原版，强制使用无记忆模式
sys.argv = [sys.argv[0], '--memory', 'none'] + sys.argv[1:]

# 导入并运行
from direct_react_agent_v3_fixed import main
sys.exit(main())