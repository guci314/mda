#!/usr/bin/env python3
"""
gemini_stateful_simple.py - 简单版本的有状态 Gemini CLI 封装
"""

import subprocess


def gemini_chat(message: str) -> str:
    """使用 gemini -c -p 发送消息并返回响应"""
    result = subprocess.run(
        ['gemini', '-c', '-p', message],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


# 测试记忆功能
print("=== 测试 Gemini CLI 记忆功能 ===\n")

# 第一步：告诉电话号码
print("步骤1: 告诉电话号码")
response1 = gemini_chat("我的电话号码是18674048895，请记住它。")
print(f"Gemini: {response1}\n")

# 第二步：询问电话号码
print("步骤2: 询问电话号码")
response2 = gemini_chat("我刚才告诉你的电话号码是什么？")
print(f"Gemini: {response2}\n")

# 检查结果
if "18674048895" in response2:
    print("✅ 成功！Gemini 记住了电话号码。")
else:
    print("❌ 失败！Gemini 没有记住电话号码。")