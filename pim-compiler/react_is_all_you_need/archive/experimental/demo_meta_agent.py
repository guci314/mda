#!/usr/bin/env python3
"""
演示：Meta Agent = 普通Agent + 知识 + CreateAgentTool
证明不需要特殊的MetaAgent类
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent_minimal import ReactAgentMinimal
from tools.create_agent_tool import create_agent_tool


def main():
    """演示如何用普通Agent + 知识 + 工具 = Meta Agent"""
    
    print("🎯 Meta Agent演示：普通Agent + 知识 + 工具")
    print("=" * 60)
    
    # 1. 创建一个普通的ReactAgentMinimal
    print("\n1️⃣ 创建普通的ReactAgentMinimal...")
    
    meta_agent = ReactAgentMinimal(
        work_dir="/tmp/meta_demo",
        name="project_coordinator",
        description="项目协调者 - 分析任务并创建专门的Agent团队",
        model="deepseek-chat",  # 需要理解和分析能力
        knowledge_files=[
            "knowledge/meta/meta_agent_knowledge.md",
            "knowledge/meta/llm_selection_knowledge.md"
        ],
        minimal_mode=True
    )
    
    print("  ✅ 创建了普通的Agent")
    print(f"  📝 名称: {meta_agent.name}")
    print(f"  🧠 模型: {meta_agent.model}")
    
    # 2. 添加CreateAgentTool，让它具有创建Agent的能力
    print("\n2️⃣ 添加CreateAgentTool...")
    
    # ReactAgentMinimal有add_function方法，可以添加任何函数作为工具
    # 我们只需要创建一个包装函数
    class CreateAgentFunction:
        def __init__(self):
            self.name = "create_agent"
            self.description = "创建新的Agent - 根据任务自动选择合适的LLM"
            self.parameters = {
                "name": {"type": "string", "description": "Agent名称"},
                "description": {"type": "string", "description": "Agent描述"},
                "task_analysis": {"type": "string", "description": "任务分析，用于自动选择LLM"},
            }
            self.return_type = "object"
        
        def execute(self, **kwargs):
            return create_agent_tool(**kwargs)
    
    # 添加到Agent
    create_agent_func = CreateAgentFunction()
    meta_agent.add_function(create_agent_func)
    
    print("  ✅ 添加了create_agent工具")
    print("  🔧 现在Agent可以创建其他Agent了")
    
    # 3. 现在这个普通Agent就是Meta Agent了！
    print("\n3️⃣ 测试Meta Agent能力...")
    print("-" * 40)
    
    # 让Meta Agent执行任务（会自动使用create_agent工具）
    task = """
    请帮我创建一个Agent团队来完成博客系统开发：
    
    1. 创建一个file_cleaner agent，负责清理工作目录
    2. 创建一个psm_generator agent，负责生成PSM文档
    3. 创建一个code_generator agent，负责生成代码
    4. 创建一个test_fixer agent，负责修复测试
    
    注意：
    - 根据每个Agent的任务特点选择合适的LLM
    - 文件操作用快速模型
    - 调试修复用深度模型
    - 文档生成用擅长文档的模型
    """
    
    print("📋 任务：创建Agent团队")
    print("\n执行中...")
    
    # 直接调用工具演示（实际使用时Meta Agent会在execute中自动调用）
    agents_created = []
    
    # 创建文件清理Agent
    result1 = create_agent_tool(
        name="file_cleaner",
        description="负责清理工作目录和文件操作",
        task_analysis="文件操作任务，需要快速执行"
    )
    agents_created.append(result1)
    print(f"\n{result1['message']}")
    
    # 创建PSM生成Agent
    result2 = create_agent_tool(
        name="psm_generator",
        description="负责生成PSM平台特定模型文档",
        task_analysis="文档生成任务，需要处理长文本"
    )
    agents_created.append(result2)
    print(f"{result2['message']}")
    
    # 创建代码生成Agent
    result3 = create_agent_tool(
        name="code_generator",
        description="负责生成FastAPI代码实现",
        task_analysis="代码生成任务，需要架构设计能力"
    )
    agents_created.append(result3)
    print(f"{result3['message']}")
    
    # 创建测试修复Agent
    result4 = create_agent_tool(
        name="test_fixer",
        description="负责调试和修复pytest测试错误",
        task_analysis="调试修复任务，需要深度分析能力"
    )
    agents_created.append(result4)
    print(f"{result4['message']}")
    
    # 4. 展示结果
    print("\n" + "=" * 60)
    print("📊 Agent团队创建完成!")
    print("=" * 60)
    
    print("\n🤖 创建的Agent团队：")
    for i, result in enumerate(agents_created, 1):
        if result["status"] == "success":
            print(f"\n{i}. {result['agent_name']}")
            print(f"   模型: {result['model']}")
            print(f"   职责: {result['description']}")
            print(f"   知识: {len(result.get('knowledge_files', []))}个文件")
    
    # 5. 核心洞察
    print("\n" + "=" * 60)
    print("💡 核心洞察")
    print("=" * 60)
    
    print("""
1. ✅ Meta Agent = 普通Agent + 知识 + 工具
   - 不需要特殊的MetaAgent类
   - ReactAgentMinimal已经足够
   
2. ✅ 知识驱动LLM选择
   - 通过knowledge文件定义选择逻辑
   - 不是硬编码在代码中
   
3. ✅ 工具提供能力
   - create_agent_tool让Agent能创建Agent
   - 就像给人类一个"招聘"的能力
   
4. ✅ 组合大于继承
   - 不需要复杂的继承体系
   - 简单的组合就能实现强大功能
   
5. ✅ 常识即智能
   - "人类不会安排文盲当美国总统"
   - LLM选择基于任务特性的常识
""")
    
    print("=" * 60)
    print("🎯 结论：简单即是美，组合即是力量")
    print("=" * 60)


if __name__ == "__main__":
    main()