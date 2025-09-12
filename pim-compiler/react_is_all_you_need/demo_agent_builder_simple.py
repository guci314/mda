#!/usr/bin/env python3
"""
Agent Builder Demo - 简洁版
Agent Builder根据需求描述，自动构建满足需求的Agent
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent_minimal import ReactAgentMinimal


def main():
    """主函数 - 演示Agent Builder根据需求构建Agent"""
    
    print("\n" + "="*60)
    print("🚀 Agent Builder Demo")
    print("="*60)
    
    # 创建工作目录
    work_dir = "/tmp/agent_builder_workspace"
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    
    # 创建Agent Builder
    print("\n📦 初始化Agent Builder...")
    agent_builder = ReactAgentMinimal(
        work_dir=work_dir,
        name="agent_builder",
        description="Agent Builder - 根据需求构建其他Agent的元Agent",
        model="deepseek-chat",
        knowledge_files=[
            "knowledge/agent_builder_knowledge.md"
        ],
        max_rounds=100
    )
    print("  ✅ Agent Builder就绪")
    
    # 需求描述（类似软件需求说明书）
    requirements = """
# Debug Agent需求说明书

## 产品名称
Python Debug Agent

## 目标用户
Python开发者

## 核心功能
自动修复Python代码中的测试失败问题

## 功能需求
1. 能够运行pytest发现失败的测试
2. 能够理解测试错误信息
3. 能够定位错误代码位置
4. 能够修复语法错误（如 = vs ==）
5. 能够修复逻辑错误（如错误的运算符）
6. 修复后能验证所有测试通过

## 使用场景
用户有一个包含bug的Python文件和对应的测试文件，
希望Agent能自动修复所有bug，让测试全部通过。

## 成功标准
给定任何包含bug的Python代码，Agent能够：
- 识别所有测试失败
- 逐个修复错误
- 最终所有pytest测试通过

## 示例场景
一个calculator.py文件包含除法和幂运算的bug，
Agent应该能修复这些bug，让test_calculator.py的所有测试通过。
"""
    
    print("\n📋 需求描述：")
    print("  产品：Python Debug Agent")
    print("  功能：自动修复测试失败")
    print("  目标：所有pytest测试通过")
    
    print("\n🎯 Agent Builder开始工作...")
    print("-" * 60)
    
    # Agent Builder根据需求构建Debug Agent
    result = agent_builder.execute(task=requirements)
    
    print("\n" + "="*60)
    print("✅ 构建完成！")
    print("="*60)
    
    if result:
        print("\n📊 构建结果：")
        if len(result) > 500:
            print(result[:500] + "...")
        else:
            print(result)
    
    print("\n💡 核心理念：")
    print("  📝 需求驱动：只提供What，不指定How")
    print("  🧠 知识迭代：Agent Builder自主决定实现方式")
    print("  🔄 测试驱动：通过测试验证是否满足需求")
    print("  ✨ 自主进化：知识文件逐步优化直到成功")
    
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