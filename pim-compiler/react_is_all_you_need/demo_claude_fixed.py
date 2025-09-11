#!/usr/bin/env python3
"""
修复版Claude Code演示 - 解决超时问题
"""

from core.react_agent_minimal import ReactAgentMinimal

def main():
    print("🚀 Claude Code演示（修复超时问题）")
    print("="*60)
    
    # 创建Agent，加载更新后的知识文件
    agent = ReactAgentMinimal(
        work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need",
        name="claude_fixed_demo",
        description="修复超时问题的演示",
        knowledge_files=[
            "knowledge/tools/claude_code_cli.md"
        ],
        model="deepseek-chat",
        max_rounds=8
    )
    
    # 演示1: 使用claude_code工具（推荐）
    print("\n📝 演示1: 使用claude_code工具（避免超时）")
    print("-"*40)
    
    result1 = agent.execute(task="""
    根据知识文件的重要提示，优先使用claude_code工具。
    使用claude_code工具，action设为custom，
    custom_command设为: claude -p "解释什么是Python装饰器"
    """)
    
    print("结果:", result1[:400] if len(result1) > 400 else result1)
    
    # 演示2: 异步执行（备选方案）
    print("\n\n📝 演示2: 异步执行避免超时")
    print("-"*40)
    
    result2 = agent.execute(task="""
    根据知识文件的异步执行方法，执行以下步骤：
    1. 使用execute_command执行: echo "生成快速排序函数" | claude -p > /tmp/claude_result.txt 2>&1 &
    2. 使用execute_command执行: sleep 5
    3. 使用execute_command执行: cat /tmp/claude_result.txt
    4. 如果有生成的代码，保存到quicksort.py
    """)
    
    print("结果:", result2[:400] if len(result2) > 400 else result2)
    
    # 演示3: 使用脚本方式（最稳定）
    print("\n\n📝 演示3: 脚本方式（最稳定）")
    print("-"*40)
    
    result3 = agent.execute(task="""
    创建并执行一个脚本来调用Claude：
    1. 创建脚本claude_test.sh，内容：
       #!/bin/bash
       claude -p "生成冒泡排序函数" > bubble_sort_result.txt 2>&1
    2. 使用execute_command执行: chmod +x claude_test.sh
    3. 使用execute_command执行: ./claude_test.sh &
    4. 等待3秒: sleep 3
    5. 读取结果: cat bubble_sort_result.txt
    """)
    
    print("结果:", result3[:400] if len(result3) > 400 else result3)
    
    print("\n\n✨ 演示完成！")
    print("="*60)
    print("解决超时的三种方法：")
    print("1. ✅ 使用claude_code工具（最简单）")
    print("2. ✅ 异步执行命令（灵活）")
    print("3. ✅ 脚本方式（最稳定）")

if __name__ == "__main__":
    main()