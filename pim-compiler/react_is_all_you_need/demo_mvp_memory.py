#!/usr/bin/env python3
"""MVP 异步记忆演示 - 最简实现

展示经验主义的实现方式：
1. 第一版：就是 print
2. 用户反馈后加开关
3. 发现错误必须显示后的改进
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


def demo():
    """演示 MVP 异步记忆"""
    print("=== MVP 异步记忆演示 ===\n")
    print("v0.0.1 版本特性：")
    print("✅ 异步提取完成后会打印通知") 
    print("✅ 错误纠正用 🚨 标记（始终显示）")
    print("✅ 普通学习用 💭 标记（可配置）")
    print("✅ 就这么简单！\n")
    
    # 创建输出目录
    output_dir = Path("output/mvp_demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建 Agent（默认显示更新）
    config = ReactAgentConfig(
        work_dir=str(output_dir),
        memory_level=MemoryLevel.SMART,
        llm_model="deepseek-chat"
        # show_memory_updates=True  # 默认值，不需要显式设置
    )
    
    agent = GenericReactAgent(config, name="mvp_agent")
    
    # 执行任务
    print("执行任务：创建一个简单的 Python 函数...\n")
    
    result = agent.execute_task(
        "创建一个 calculate_area.py 文件，包含计算矩形面积的函数。"
        "函数签名：def calculate_area(width, height)"
    )
    
    print("\n任务完成！现在等待异步记忆更新...\n")
    
    # 等待几秒，让异步更新完成
    for i in range(3, 0, -1):
        print(f"等待中... {i}")
        time.sleep(1)
    
    print("\n" + "="*50)
    print("演示完成！")
    print("\n注意观察上面的记忆更新通知：")
    print("- 如果看到 💭，说明 Agent 学到了新东西")
    print("- 如果看到 🚨，说明 Agent 发现了需要纠正的错误")
    print("\n这就是 MVP：最简单，但够用！")


def demo_with_config():
    """演示如何通过配置控制显示"""
    print("\n\n=== 演示配置控制 ===\n")
    
    # 创建不显示普通更新的 Agent
    config = ReactAgentConfig(
        work_dir="output/mvp_demo_quiet",
        memory_level=MemoryLevel.SMART,
        llm_model="deepseek-chat",
        show_memory_updates=False  # 关闭普通更新显示
    )
    
    agent = GenericReactAgent(config, name="quiet_agent")
    
    print("这次关闭了普通记忆更新显示...")
    print("执行任务：分析代码...\n")
    
    agent.execute_task("简单分析一下 Python 的列表推导式用法")
    
    print("\n等待异步更新（应该很安静）...")
    time.sleep(3)
    
    print("\n如果没有看到 💭 通知，说明配置生效了！")
    print("但如果有错误纠正，仍然会看到 🚨 通知。")


if __name__ == "__main__":
    # 检查 API key
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("请设置 DEEPSEEK_API_KEY 环境变量")
        print("export DEEPSEEK_API_KEY='your-api-key'")
        sys.exit(1)
    
    # 运行演示
    demo()
    
    # 可选：演示配置控制
    # demo_with_config()
    
    print("\n\n💡 经验主义心得：")
    print("- 不要过度设计，先 print 再说")
    print("- 用户说太吵？加个开关")  
    print("- 错误必须显示？特殊处理")
    print("- 代码虽简单，但解决了实际问题！")