#!/usr/bin/env python3
"""
Agent Builder Demo - 正确版本
Agent Builder是一个Agent，通过知识文件指导，迭代构建Debug Agent
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent_minimal import ReactAgentMinimal


def main():
    """主函数 - 演示如何使用Agent Builder构建Debug Agent"""
    
    print("\n" + "="*60)
    print("🚀 Agent Builder Demo - 构建Debug Agent")
    print("="*60)
    
    # 创建工作目录
    work_dir = "/tmp/agent_builder_workspace"
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    
    # 创建Agent Builder（加载agent_builder_knowledge.md）
    print("\n📦 创建Agent Builder...")
    agent_builder = ReactAgentMinimal(
        work_dir=work_dir,
        name="agent_builder",
        description="Agent Builder - 用于构建、测试和优化其他Agent的元Agent",
        model="deepseek-chat",  # 使用DeepSeek
        knowledge_files=[
            "knowledge/agent_builder_knowledge.md"  # Agent Builder的知识文件
        ],
        max_rounds=100  # 需要足够的轮数来完成迭代
    )
    print("  ✅ Agent Builder已创建")
    print("  📚 已加载agent_builder_knowledge.md")
    
    # Agent Builder的任务：构建一个能修复测试的Debug Agent
    builder_task = """
# 构建Debug Agent任务

## 目标
构建一个能够修复Python测试错误的Debug Agent。

## 要求
1. **创建测试环境**
   - 创建一个有bug的calculator.py文件
   - Bug 1: 第14行，使用 `if b = 0:` 而不是 `if b == 0:`（语法错误）
   - Bug 2: 第18行，使用 `^` 而不是 `**` 进行幂运算（逻辑错误）
   - 创建test_calculator.py，包含5个测试用例

2. **迭代开发Debug知识文件**
   - 迭代0：创建初始的简单知识文件（3-5行）
   - 迭代1：添加具体执行步骤（20-30行）
   - 迭代2：添加错误分类和处理策略（50-80行）
   - 迭代3：添加完整的SOP和错误速查表（100+行）

3. **测试和评估**
   - 每次迭代后，创建新的Debug Agent实例
   - 加载当前版本的知识文件
   - 让Debug Agent执行修复任务
   - 评估成功与否（pytest是否全部通过）

4. **迭代优化流程**
   ```
   创建buggy代码 → 写v0知识 → 测试 → 分析问题 → 写v1知识 → 测试 → ... → 成功
   ```

## 具体步骤

### 步骤1：创建测试环境
在work_dir下创建：
- calculator.py（包含2个bug）
- test_calculator.py（5个测试用例）

### 步骤2：创建知识文件版本
在work_dir/knowledge_iterations/目录下创建：
- debug_knowledge_v0.md（极简版）
- debug_knowledge_v1.md（基础版）
- debug_knowledge_v2.md（增强版）
- debug_knowledge_v3.md（完整版）

### 步骤3：测试每个版本
对每个知识文件版本：
1. 说明当前是第几次迭代
2. 展示知识文件的主要改进
3. 创建Debug Agent并执行任务
4. 分析结果（成功/失败原因）

### 步骤4：总结
- 展示知识文件从简单到复杂的演化
- 说明每次迭代的关键改进
- 得出构建Agent的经验教训

## 期望输出
1. 4个版本的debug知识文件
2. 测试环境（calculator.py, test_calculator.py）
3. 每个版本的测试结果
4. 最终成功修复所有测试

请开始执行Agent Builder流程，构建一个功能完整的Debug Agent。
"""
    
    print("\n📋 Agent Builder任务：")
    print("  - 创建有bug的测试代码")
    print("  - 迭代开发debug知识文件（v0→v3）")
    print("  - 测试每个版本的效果")
    print("  - 最终构建成功的Debug Agent")
    
    print("\n🎯 开始执行...")
    print("-" * 60)
    
    # Agent Builder执行任务
    result = agent_builder.execute(task=builder_task)
    
    print("\n" + "="*60)
    print("✅ Agent Builder演示完成！")
    print("="*60)
    
    # 显示结果摘要
    if result:
        print("\n📊 执行结果：")
        if len(result) > 500:
            print(result[:500] + "...")
        else:
            print(result)
    
    print("\n💡 关键洞察：")
    print("  1. Agent Builder通过知识文件驱动")
    print("  2. 迭代优化是构建Agent的核心")
    print("  3. 从简单到复杂的渐进式开发")
    print("  4. 知识文件的质量决定Agent能力")
    
    print(f"\n💾 生成的文件保存在: {work_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断执行")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n✨ 演示结束")