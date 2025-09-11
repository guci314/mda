#!/usr/bin/env python3
"""
演示Agent调用Claude Code的完整示例
"""

from core.react_agent_minimal import ReactAgentMinimal

def main():
    # 创建Agent实例
    agent = ReactAgentMinimal(
        work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need",
        name="claude_code_demo",
        description="演示Claude Code集成的Agent",
        model="deepseek-chat"
    )
    
    # 任务1: 使用Claude Code分析代码
    print("\n" + "="*60)
    print("任务1: 分析代码架构")
    print("="*60)
    
    result1 = agent.execute(task="""
    使用claude_code工具，action设置为analyze，
    分析core/tool_base.py文件，了解工具基类的设计。
    files参数设置为['core/tool_base.py']，
    prompt参数描述要分析的内容。
    """)
    
    print(result1)
    
    # 任务2: 使用自定义命令
    print("\n" + "="*60)
    print("任务2: 执行自定义Claude命令")
    print("="*60)
    
    result2 = agent.execute(task="""
    使用claude_code工具，action设置为custom，
    custom_command参数设置为：
    claude -p '生成一个简单的Python函数，计算斐波那契数列' --max-turns 1
    """)
    
    print(result2)
    
    print("\n✨ 演示完成！")
    print("Agent成功集成了Claude Code，可以：")
    print("1. 分析代码文件")
    print("2. 生成代码")
    print("3. 执行自定义Claude命令")

if __name__ == "__main__":
    main()