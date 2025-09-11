#!/usr/bin/env python3
"""
使用知识文件方式调用Claude Code的演示
这种方式更灵活、更强大
"""

from core.react_agent_minimal import ReactAgentMinimal

def main():
    print("🚀 Claude Code知识文件方式演示")
    print("="*60)
    
    # 创建Agent，加载Claude Code知识文件
    agent = ReactAgentMinimal(
        work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need",
        name="claude_knowledge_demo",
        description="通过知识文件使用Claude Code",
        knowledge_files=[
            "knowledge/tools/claude_code_cli.md"  # 加载Claude使用指南
        ],
        model="deepseek-chat",
        max_rounds=10  # 给足够的轮数
    )
    
    # 演示1: 简单调用
    print("\n📝 演示1: 快速问答")
    print("-"*40)
    
    result1 = agent.execute(task="""
    根据Claude Code CLI使用指南，使用execute_command工具
    执行命令：claude -p "用一句话解释什么是React Agent"
    """)
    
    print("结果:", result1[:300] if len(result1) > 300 else result1)
    
    # 演示2: 生成代码
    print("\n\n📝 演示2: 生成代码")
    print("-"*40)
    
    result2 = agent.execute(task="""
    使用execute_command工具执行：
    claude -p "生成一个Python函数，实现二分查找算法，包含文档字符串和测试用例"
    
    如果生成成功，将代码保存到binary_search.py文件中。
    """)
    
    print("结果:", result2[:300] if len(result2) > 300 else result2)
    
    # 演示3: 异步分析（高级）
    print("\n\n📝 演示3: 异步代码分析")
    print("-"*40)
    
    result3 = agent.execute(task="""
    根据Claude Code CLI使用指南的异步监控技巧，执行以下步骤：
    
    1. 创建一个分析脚本analyze_async.sh，内容如下：
    ```bash
    #!/bin/bash
    echo "开始分析代码库..." > /tmp/claude_analysis.log
    echo "分析core目录的Python文件" | claude -p >> /tmp/claude_analysis.log 2>&1
    echo "分析完成！" >> /tmp/claude_analysis.log
    ```
    
    2. 使用execute_command执行: chmod +x analyze_async.sh
    
    3. 使用execute_command后台执行: ./analyze_async.sh &
    
    4. 等待2秒后，使用execute_command查看输出: cat /tmp/claude_analysis.log
    
    5. 清理临时文件: rm -f analyze_async.sh /tmp/claude_analysis.log
    """)
    
    print("结果:", result3[:500] if len(result3) > 500 else result3)
    
    # 演示4: 交互式代码审查
    print("\n\n📝 演示4: 代码审查")
    print("-"*40)
    
    result4 = agent.execute(task="""
    1. 先读取test_simple.py文件的内容
    2. 然后使用execute_command执行claude -p命令，请求审查代码
    3. 命令格式：claude -p "审查以下Python代码的质量和提供改进建议：[文件内容的前100个字符]"
    """)
    
    print("结果:", result4[:500] if len(result4) > 500 else result4)
    
    print("\n\n✨ 演示完成！")
    print("="*60)
    print("知识文件方式的优势：")
    print("✅ Agent根据知识文档学会了正确使用Claude CLI")
    print("✅ 支持灵活的命令组合和异步操作")
    print("✅ 可以处理复杂的多步骤任务")
    print("✅ 错误处理更智能（Agent会尝试不同方法）")

if __name__ == "__main__":
    main()