#!/usr/bin/env python3
"""
使用扩展版execute_command工具的Claude Code演示
解决10秒超时限制问题
"""

from core.react_agent_minimal import ReactAgentMinimal
from core.tools.execute_command_extended import ExecuteCommandExtended

def main():
    print("🚀 Claude Code演示（扩展版工具）")
    print("="*60)
    
    # 创建Agent
    agent = ReactAgentMinimal(
        work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need",
        name="claude_extended_demo",
        description="使用扩展工具的演示",
        knowledge_files=[
            "knowledge/tools/claude_code_cli.md"
        ],
        model="deepseek-chat",
        max_rounds=8
    )
    
    # 注册扩展版execute_command工具
    ext_tool = ExecuteCommandExtended(agent.work_dir)
    agent.append_tool(ext_tool)
    
    # 演示1: 使用扩展工具，设置更长超时
    print("\n📝 演示1: 使用扩展工具（30秒超时）")
    print("-"*40)
    
    result1 = agent.execute(task="""
    使用execute_command_ext工具（注意是_ext版本），设置timeout参数为30：
    command: claude -p "解释什么是函数式编程"
    timeout: 30
    """)
    
    print("结果:", result1[:400] if len(result1) > 400 else result1)
    
    # 演示2: 后台执行模式
    print("\n\n📝 演示2: 后台执行模式")
    print("-"*40)
    
    result2 = agent.execute(task="""
    使用execute_command_ext工具的后台模式：
    1. 第一步，后台执行Claude：
       command: echo "生成归并排序函数" | claude -p > /tmp/merge_sort.txt 2>&1
       background: true
    
    2. 第二步，等待5秒：
       command: sleep 5
       timeout: 10
    
    3. 第三步，读取结果：
       使用read_file读取 /tmp/merge_sort.txt
    """)
    
    print("结果:", result2[:400] if len(result2) > 400 else result2)
    
    # 演示3: 长时间任务
    print("\n\n📝 演示3: 长时间任务（60秒超时）")
    print("-"*40)
    
    result3 = agent.execute(task="""
    使用execute_command_ext工具执行长时间任务：
    command: claude -p "分析React Agent架构的优缺点，详细说明"
    timeout: 60
    
    如果成功，总结Claude的分析。
    """)
    
    print("结果:", result3[:400] if len(result3) > 400 else result3)
    
    print("\n\n✨ 演示完成！")
    print("="*60)
    print("扩展工具的优势：")
    print("✅ 支持自定义超时（最大300秒）")
    print("✅ 支持后台执行模式")
    print("✅ 完美解决10秒限制问题")

if __name__ == "__main__":
    main()