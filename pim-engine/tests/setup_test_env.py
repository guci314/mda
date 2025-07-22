"""设置测试环境"""

import os
import sys
from pathlib import Path

def setup_test_env():
    """设置测试所需的环境变量"""
    # 检查是否已经设置了 API key
    if "GEMINI_API_KEY" in os.environ:
        print("✓ GEMINI_API_KEY 已设置")
        return True
    
    # 尝试从用户输入获取
    print("请设置 GEMINI_API_KEY 环境变量")
    print("例如: export GEMINI_API_KEY=your_api_key_here")
    print("或者在 ~/.env 文件中添加: GEMINI_API_KEY=your_api_key_here")
    
    # 提示用户
    response = input("\n是否要跳过需要 API key 的测试? (y/n): ")
    if response.lower() == 'y':
        return False
    else:
        sys.exit(1)

if __name__ == "__main__":
    setup_test_env()