"""
hello.py - 基础Python程序示例

功能：
1. 打印Hello World
2. 显示当前日期时间
3. 显示Python版本

作者: [你的名字]
创建日期: [今天的日期]
"""

import sys
import datetime

def main():
    """主程序入口"""
    # 打印Hello World
    print("Hello, World!")
    
    # 打印当前日期和时间
    now = datetime.datetime.now()
    print(f"当前时间: {now}")
    
    # 打印Python版本
    print(f"Python版本: {sys.version}")

if __name__ == "__main__":
    main()