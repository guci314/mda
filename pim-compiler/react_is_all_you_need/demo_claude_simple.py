#!/usr/bin/env python3
"""
简化版Claude Code知识文件演示
"""

from core.react_agent_minimal import ReactAgentMinimal

def main():
    print("🚀 Claude Code知识文件方式演示（简化版）")
    print("="*60)
    
    # 创建Agent，加载知识文件
    agent = ReactAgentMinimal(
        work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need",
        name="claude_simple_demo",
        description="简单演示",
        knowledge_files=[
            "knowledge/tools/claude_code_cli.md"
        ],
        model="deepseek-chat",
        max_rounds=5
    )
    
    # 演示: 快速生成代码
    print("\n📝 任务: 生成一个简单函数")
    print("-"*40)
    
    result = agent.execute(task="""
    使用claude_code工具，action设置为custom，
    custom_command设置为：claude -p "生成一个Python函数add(a,b)返回两数之和"
    """)
    
    # 只显示前500个字符
    if len(result) > 500:
        print(result[:500] + "\n...[输出已截断]")
    else:
        print(result)
    
    print("\n✨ 演示完成！")
    print("知识文件方式让Agent学会了如何正确使用Claude CLI")

if __name__ == "__main__":
    main()