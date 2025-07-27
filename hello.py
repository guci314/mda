#!/usr/bin/env python3
# hello.py - 一个简单的Python程序

# 导入必要的模块
import datetime
import sys

def main():
    """主函数，打印问候语和系统信息"""
    # 1. 打印Hello World
    print("Hello, World!")
    
    # 2. 打印当前日期和时间
    now = datetime.datetime.now()
    print(f"Current date and time: {now}")
    
    # 3. 打印Python版本
    print(f"Python version: {sys.version}")

if __name__ == "__main__":
    main()