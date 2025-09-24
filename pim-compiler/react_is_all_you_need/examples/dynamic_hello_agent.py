#!/usr/bin/env python3
"""
演示如何"动态"创建Hello Agent
实际上是通过Task工具创建临时agent实例
"""

def create_hello_agent_response(greeting):
    """
    模拟动态创建hello agent并获得回应

    在实际的Claude Code中，你会说：
    "用Task工具创建hello agent，回应：[greeting]"
    """

    # 这是概念演示
    # 实际使用时，Task工具会：
    # 1. 创建一个新的agent实例
    # 2. 给它prompt（指令）
    # 3. 执行任务
    # 4. 返回结果

    prompt = f"""
    你是一个友好的打招呼助手。
    规则：
    1. 热情友好
    2. 简短回复（1-2句）
    3. 可以用emoji

    请回应："{greeting}"
    """

    # 在Claude Code中，这会通过Task工具执行
    # 返回的就是agent的回应

    print(f"动态创建Hello Agent...")
    print(f"输入: {greeting}")
    print(f"Agent将会回应...")

    return "这里会是agent的回应"

# 使用示例
if __name__ == "__main__":
    # 不同的问候，动态创建agent回应
    greetings = [
        "早上好！",
        "晚安",
        "你好吗？",
        "周末愉快！"
    ]

    for g in greetings:
        print(f"\n{'='*40}")
        response = create_hello_agent_response(g)
        print(f"回应: {response}")

    print("\n" + "="*60)
    print("💡 在Claude Code中的实际用法：")
    print("1. 直接说：'用Task工具创建hello agent回应：早上好'")
    print("2. 或者：'创建一个打招呼agent说晚安'")
    print("3. Task工具会动态创建agent并执行")