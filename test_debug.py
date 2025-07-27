#!/usr/bin/env python3
"""测试调试快捷键的文件"""

def main():
    print("开始测试调试功能")
    
    # 在这里设置断点
    x = 10
    y = 20
    
    # 将光标放在这里，然后按 Ctrl+F10
    result = x + y
    
    print(f"结果: {result}")
    
    # 另一个测试点
    for i in range(5):
        print(f"循环 {i}")
    
    print("测试完成")

if __name__ == "__main__":
    main() 