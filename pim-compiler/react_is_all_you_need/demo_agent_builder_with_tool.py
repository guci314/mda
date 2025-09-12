#!/usr/bin/env python3
"""
Agent Builder Demo - 使用CreateAgentTool
Agent Builder通过CreateAgentTool动态创建和测试Agent
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent_minimal import ReactAgentMinimal
from core.tools.create_agent_tool import CreateAgentTool


def main():
    """主函数 - 演示Agent Builder使用CreateAgentTool构建Agent"""
    
    print("\n" + "="*60)
    print("🚀 Agent Builder Demo (with CreateAgentTool)")
    print("="*60)
    
    # 创建工作目录
    work_dir = "/tmp/agent_builder_workspace"
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    
    # 创建Agent Builder
    print("\n📦 初始化Agent Builder...")
    agent_builder = ReactAgentMinimal(
        work_dir=work_dir,
        name="agent_builder",
        description="Agent Builder - 使用知识驱动方法构建其他Agent",
        model="deepseek-chat",
        knowledge_files=[
            "knowledge/agent_builder_knowledge.md"  # 包含ReactAgentMinimal架构和知识驱动理念
        ],
        max_rounds=100
    )
    
    # 添加CreateAgentTool到Agent Builder
    print("  ✅ 添加CreateAgentTool...")
    create_agent_tool = CreateAgentTool(work_dir=work_dir, parent_agent=agent_builder)
    agent_builder.add_function(create_agent_tool)
    
    print("  ✅ Agent Builder就绪")
    print("  📚 已加载ReactAgentMinimal架构知识")
    print("  🔧 已配备CreateAgentTool")
    
    # 需求描述（纯需求，不包含实现）
    requirements = """
# 构建Debug Agent

## 需求描述
我需要一个能自动修复Python测试错误的Debug Agent。

## 功能要求
1. 能运行pytest发现测试失败
2. 能理解错误信息（SyntaxError、AssertionError等）
3. 能定位并修复代码错误
4. 能验证修复后所有测试通过

## 测试场景
创建一个有bug的calculator.py和对应的test_calculator.py，
Debug Agent应该能自动修复所有bug让测试通过。

## 构建要求
1. 使用CreateAgentTool创建Debug Agent
2. 通过knowledge_str参数动态传入知识（而不是文件）
3. 迭代优化知识内容直到Agent能成功完成任务
4. 每次迭代要测试Agent的实际表现

## 预期结果
最终得到一个能修复Python测试的Debug Agent，并且记录下完整的知识演化过程。
"""
    
    print("\n📋 任务需求：")
    print("  目标：构建Debug Agent")
    print("  方法：知识驱动迭代")
    print("  工具：CreateAgentTool")
    
    print("\n🎯 Agent Builder开始工作...")
    print("-" * 60)
    
    # Agent Builder执行任务
    result = agent_builder.execute(task=requirements)
    
    print("\n" + "="*60)
    print("✅ 构建完成！")
    print("="*60)
    
    if result:
        print("\n📊 构建结果：")
        if len(result) > 800:
            print(result[:800] + "...")
        else:
            print(result)
    
    print("\n💡 关键特性：")
    print("  🧠 理解ReactAgentMinimal架构")
    print("  📝 动态生成知识内容")
    print("  🔧 使用CreateAgentTool创建Agent")
    print("  🔄 迭代测试和优化")
    print("  ✨ 知识驱动的Agent构建")
    
    print(f"\n💾 工作目录: {work_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()