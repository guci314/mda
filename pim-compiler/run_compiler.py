#!/usr/bin/env python3
"""运行编译器的包装脚本"""

import sys
import os
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 现在导入并运行编译器
if __name__ == "__main__":
    # 保存原始的argv
    original_argv = sys.argv[:]
    
    # 修改argv以运行compile_with_generator.py
    sys.argv = [
        "compile_with_generator.py",
        "../models/domain/用户管理_pim.md",
        "--generator", "react-agent",
        "-o", "output/react_agent_enhanced_v3"
    ]
    
    # 导入并运行主函数
    from compile_with_generator import main
    
    sys.exit(main())