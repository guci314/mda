#!/usr/bin/env python3
"""
gemini-python-test.py - 使用 Python subprocess 测试 Gemini CLI 记忆
"""

import subprocess
import time
import sys

def test_gemini_memory():
    print("测试 Gemini CLI 记忆功能（Python 版）")
    print("=====================================\n")
    
    try:
        # 启动 Gemini CLI 进程
        process = subprocess.Popen(
            ['gemini', '-c'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        print("Gemini CLI 已启动...\n")
        time.sleep(2)
        
        # 第一次交互
        print("[步骤1] 发送：我的电话号码是18674048895，请记住它。")
        process.stdin.write("我的电话号码是18674048895，请记住它。\n")
        process.stdin.flush()
        
        # 等待响应
        time.sleep(3)
        
        # 第二次交互
        print("\n[步骤2] 发送：我刚才告诉你的电话号码是什么？")
        process.stdin.write("我刚才告诉你的电话号码是什么？\n")
        process.stdin.flush()
        
        # 等待响应
        time.sleep(3)
        
        # 退出
        process.stdin.write("exit\n")
        process.stdin.flush()
        
        # 获取所有输出
        output, error = process.communicate(timeout=5)
        
        print("\n===== Gemini 输出 =====")
        print(output)
        
        if error:
            print("\n===== 错误输出 =====")
            print(error)
            
        # 检查是否包含电话号码
        if "18674048895" in output:
            print("\n✅ 成功！Gemini 记住了电话号码。")
        else:
            print("\n❓ 无法确定 Gemini 是否记住了电话号码。")
            
    except subprocess.TimeoutExpired:
        print("\n超时！")
        process.kill()
    except Exception as e:
        print(f"\n错误：{e}")
    finally:
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    test_gemini_memory()