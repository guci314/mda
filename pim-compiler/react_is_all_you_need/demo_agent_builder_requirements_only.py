#!/usr/bin/env python3
"""
Agent Builder Demo - 纯需求驱动版本
用户只提供需求，Agent Builder负责所有实现
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent_minimal import ReactAgentMinimal
from core.tools.create_agent_tool import CreateAgentTool


def main():
    """主函数 - 演示纯需求驱动的Agent构建"""
    
    print("\n" + "="*60)
    print("🚀 Agent Builder - 需求驱动构建")
    print("="*60)
    
    # 创建工作目录
    work_dir = "/tmp/agent_builder_workspace"
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    
    # 创建Agent Builder
    print("\n📦 初始化Agent Builder...")
    agent_builder = ReactAgentMinimal(
        work_dir=work_dir,
        name="agent_builder",
        description="专业的Agent构建专家，根据需求自主设计、实现和测试Agent",
        model="deepseek-chat",
        knowledge_files=[
            "knowledge/agent_builder_knowledge.md"
        ],
        max_rounds=150  # 给足够的空间让Builder自主工作
    )
    
    # 添加CreateAgentTool
    create_agent_tool = CreateAgentTool(work_dir=work_dir, parent_agent=agent_builder)
    agent_builder.add_function(create_agent_tool)
    
    print("  ✅ Agent Builder就绪")
    
    # 纯需求描述 - 只说What，不说How
    requirements = """
# 产品需求书

## 产品名称
Python测试修复助手

## 目标用户
Python开发者

## 业务价值
减少开发者修复测试的时间，提高开发效率

## 功能需求
当Python项目中存在测试失败时，能够自动分析并修复代码，使测试通过。

## 质量要求
- 准确性：能正确识别错误原因
- 完整性：修复后所有测试都应该通过
- 安全性：不破坏原有的正确功能
- 鲁棒性：能处理不同类型的错误

## 验收标准
1. 设计并实现三个不同的测试场景，每个场景代表不同类型的常见错误
2. 创建的Agent能够成功修复所有三个场景中的错误
3. 每个场景的测试都能全部通过

## 测试覆盖要求
三个测试场景应该覆盖不同类型的错误，例如：
- 逻辑错误（如计算错误、边界条件处理）
- 语法错误（如拼写错误、缩进问题）
- 类型错误（如类型不匹配、None值处理）
但具体选择哪些场景由你自主决定。
"""
    
    print("\n📋 需求描述（纯What，无How）：")
    print("  ✅ 产品定位和价值")
    print("  ✅ 功能和质量要求")
    print("  ✅ 验收标准")
    print("  ❌ 没有实现细节")
    print("  ❌ 没有技术方案")
    print("  ❌ 没有测试用例")
    
    print("\n🎯 Agent Builder开始自主工作...")
    print("  它将自己决定：")
    print("  - 用什么测试场景")
    print("  - 如何组织知识")
    print("  - 怎样验证效果")
    print("-" * 60)
    
    # Agent Builder执行 - 完全自主
    result = agent_builder.execute(task=requirements)
    
    print("\n" + "="*60)
    print("✅ 构建完成！")
    print("="*60)
    
    if result:
        print("\n📊 最终结果：")
        if len(result) > 800:
            print(result[:800] + "...")
        else:
            print(result)
    
    print("\n💡 这才是真正的需求驱动开发：")
    print("  👤 用户：只描述需求")
    print("  🤖 Builder：负责所有实现")
    print("  🎯 结果：满足需求的Agent")
    
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