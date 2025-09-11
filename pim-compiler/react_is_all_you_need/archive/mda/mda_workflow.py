#!/usr/bin/env python3
"""
MDA工作流演示 - Agent作为Function的组合模式
演示如何通过add_function把Agent添加为可调用的函数，实现天然的LLM切换
"""

import os
import sys
from pathlib import Path
import time

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent_minimal import ReactAgentMinimal


def main():
    """主函数 - 演示Agent作为Function的组合模式"""
    
    print("🚀 MDA工作流演示 - Agent作为Function")
    print("=" * 60)
    
    # 工作目录
    work_dir = "/home/guci/robot_projects/blog/"
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    
    # ============================================================
    # 1. 创建各个专家Agent（使用不同的LLM）
    # ============================================================
    print("\n📦 创建专家Agent...")
    
    # General Agent - 通用任务（快速模型）
    general_agent = ReactAgentMinimal(
        work_dir=work_dir,
        name="general_agent",
        description="通用任务处理专家 - 处理文件操作等基础任务",
        model="deepseek-chat",  # kimi模型
    )
    print("  ✅ general_agent (x-ai/grok-code-fast-1)")
    
    # PSM Generation Agent - PSM生成（快速模型）
    psm_generation_agent = ReactAgentMinimal(
        work_dir=work_dir,
        name="psm_generation_agent",
        description="PSM生成专家 - 根据PIM生成平台特定模型文档",
        model="deepseek-chat",  # kimi模型
        knowledge_files=[
            "knowledge/mda/pim_to_psm_knowledge.md",
            "knowledge/large_file_handling.md"
        ],
    )
    print("  ✅ psm_generation_agent (x-ai/grok-code-fast-1)")
    
    # Code Generation Agent - 代码生成（快速模型）
    code_generation_agent = ReactAgentMinimal(
        work_dir=work_dir,
        name="code_generation_agent",
        description="代码生成专家 - 根据PSM生成FastAPI代码文件。仅负责生成新代码，不处理测试调试、错误修复等任务",
        model="deepseek-chat",  # Grok模型，通过OpenRouter
        knowledge_files=[
            "knowledge/mda/generation_knowledge.md"
        ],
        max_rounds=300  # 增加到300轮，确保能完成所有文件生成
    )
    print("  ✅ code_generation_agent (x-ai/grok-code-fast-1)")
    
    # Debug Agent - 调试修复（智能模型）
    debug_agent = ReactAgentMinimal(
        work_dir=work_dir,
        name="debug_agent",
        description="调试修复专家 - 修复代码和测试问题，需要深度理解",
        model="deepseek-chat",  # DeepSeek模型
        knowledge_files=[
            "knowledge/mda/debugging_unified.md"
        ],
        max_rounds=300  # 增加到300轮，确保能完成复杂调试任务
    )
    print("  ✅ debug_agent (deepseek-chat)")
    
    # ============================================================
    # 2. 创建Project Manager Agent
    # ============================================================
    print("\n👔 创建Project Manager...")
    
    project_manager = ReactAgentMinimal(
        work_dir=work_dir,
        name="project_manager",
        description="项目经理 - 协调其他Agent完成MDA工作流",
        model="x-ai/grok-code-fast-1",  # PM使用kimi模型做协调
    )
    print("  ✅ project_manager (x-ai/grok-code-fast-1)")
    
    # ============================================================
    # 3. 将其他Agent作为Function添加到Project Manager
    # ============================================================
    print("\n🔗 将专家Agent添加为Project Manager的Function...")
    
    # 使用add_function方法添加Agent
    # 每个Agent的execute方法成为可调用的函数
    project_manager.add_function(general_agent)
    print(f"  ✅ 添加 {general_agent.name}")
    
    project_manager.add_function(psm_generation_agent)
    print(f"  ✅ 添加 {psm_generation_agent.name}")
    
    project_manager.add_function(code_generation_agent)
    print(f"  ✅ 添加 {code_generation_agent.name}")
    
    project_manager.add_function(debug_agent)
    print(f"  ✅ 添加 {debug_agent.name}")
    
    # ============================================================
    # 4. Project Manager执行完整工作流
    # ============================================================
    print("\n" + "=" * 60)
    print("🎯 Project Manager执行MDA工作流")
    print("=" * 60)
    
    # PIM文件路径
    pim_file = "/home/guci/aiProjects/mda/pim-compiler/examples/blog.md"
    
    # Project Manager的任务：用户只需要描述需求，PM自动协调内部Agent
    pm_task = f"""
# MDA完整工作流任务

## 需求
从零开始，基于PIM文件生成一个完整的博客系统，包括代码实现和测试。

## Agent能力说明
- **general_agent**: 通用任务处理，擅长文件操作
- **psm_generation_agent**: PSM文档生成专家
- **code_generation_agent**: 代码生成（注意：能力有限，只负责生成代码文件，不要让它修复测试或调试错误）
- **debug_agent**: 调试专家（智能），负责所有测试修复、错误调试、代码优化等高难度任务

## 执行步骤
1. **清空工作目录** - 删除所有现有文件，从干净环境开始
2. **生成PSM文档** - 基于PIM生成平台特定模型
3. **分阶段生成代码** - 根据PSM分三个阶段生成代码：
   - 阶段1：生成数据模型（models.py、schemas.py、database.py）
   - 阶段2：生成API和业务逻辑（main.py、services.py、repositories.py、routers/）
   - 阶段3：生成测试和文档（tests/、README.md、requirements.txt）
4. **修复测试** - 使用debug_agent确保所有测试通过（重要：不要让code_generation_agent处理测试问题）

## 输入
- PIM文件: {pim_file}

## 期望输出
1. PSM文档 (blog_psm.md) - 包含完整的平台特定模型设计
2. 代码实现 - FastAPI应用，包含models、schemas、API endpoints
3. 测试用例 - 单元测试100%通过
4. 项目文档 - README文件

## 验收标准
- 工作目录干净，只包含新生成的文件
- PSM文档完整（包含Domain Models、Service Layer、REST API Design等章节）
- 代码结构清晰（app/目录下有main.py、models.py、schemas.py）
- 测试全部通过（pytest执行无错误）
- 文档齐全（有readme.md说明如何运行）

请从清空目录开始，完成整个MDA工作流。
"""
    
    print("\n📋 用户视角：")
    print("  输入: PIM文件 (blog.md)")
    print("  输出: 完整的博客系统")
    print("\n🎭 Project Manager内部会协调：")
    print("  - 文件操作 (kimi)")
    print("  - PSM生成 (kimi)")
    print("  - 代码生成 (grok-code-fast-1)")
    print("  - 测试修复 (deepseek)")
    print("\n⚡ LLM自动切换，用户无感知")
    print("-" * 60)
    
    # 执行工作流
    start_time = time.time()
    result = project_manager.execute(task=pm_task)
    elapsed = time.time() - start_time
    
    # ============================================================
    # 5. 总结
    # ============================================================
    print("\n" + "=" * 60)
    print("✅ MDA工作流完成!")
    print("=" * 60)
    print(f"\n⏱️ 总耗时: {elapsed:.1f}秒")
    
    if result:
        print(f"\n📊 执行结果摘要:")
        print(result[:500] + "..." if len(result) > 500 else result)
    
    print("\n💡 关键洞察:")
    print("  1. ✅ Project Manager是黑盒子 - 用户只描述需求")
    print("  2. ✅ 内部Agent自动选择 - PM智能调度")
    print("  3. ✅ LLM透明切换 - 用户无需关心")
    print("  4. ✅ 通过add_function组合不同LLM的Agent")
    print("  5. ✅ 每个Agent独立配置，按需调用")
    
    print("\n🎯 这证明了:")
    print("  - Agent作为Function是正确的抽象")
    print("  - 组合模式优于内部切换逻辑")
    print("  - 用户体验简洁，内部实现灵活")
    print("  - 移除内部LLM切换，通过组合实现更优雅")


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