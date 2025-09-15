#!/usr/bin/env python3
"""
使用Agent智能分析并生成RDF知识图谱
让Agent调用知识文件中的自然语言函数来完成转换
展示知识驱动的Agent执行模式
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')
sys.path = [p for p in sys.path if 'pim-engine' not in p]

from core.react_agent_minimal import ReactAgentMinimal
from pathlib import Path

def convert_core_to_rdf():
    """将core目录转换为RDF知识图谱"""
    
    # 定义输入输出路径
    source_dir = "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/core"
    output_file = "/tmp/core_knowledge_graph.ttl"
    validation_script = "/tmp/validate_core_rdf.py"
    
    print("🚀 创建RDF转换Agent...")
    
    # 创建Agent
    agent = ReactAgentMinimal(
        work_dir="/tmp",
        model="x-ai/grok-code-fast-1",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        knowledge_files=[
            "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/universal_to_rdf_knowledge.md"
        ],
        max_rounds=50  # 增加轮次，确保完成验证和修复
    )
    
    # 构建任务 - 调用知识文件中的自然语言函数
    task = f"""
    执行以下步骤：
    
    1. 调用 构建知识图谱("{source_dir}", "{output_file}")
       - 特别关注提取docstring（模块级、类级、方法级）
       - 将docstring作为kg:hasModuleDocstring、kg:hasClassDocstring、kg:hasMethodDocstring属性
    
    2. 调用 符号主义验证流程("{output_file}")
       - 调用 编写RDF验证脚本("{output_file}")，保存到 {validation_script}
       - 调用 执行RDF验证("{validation_script}", "{output_file}")
       - 如果验证失败，调用 修复RDF错误("{output_file}", error_report)
       - 重复验证直到通过
    
    重点分析：
    - ReactAgentMinimal类及其方法
    - 工具类（Function基类及其子类）  
    - 模块间的导入关系和继承关系
    - 核心概念：Compact Memory、React Agent、Function Base
    """
    
    print("📂 开始分析core目录...")
    print("=" * 60)
    
    # 执行转换
    result = agent.execute(task=task)
    
    print("=" * 60)
    print("\n✅ 转换完成！")
    print("\n转换结果摘要：")
    print("-" * 40)
    # 只打印结果的前1000个字符
    print(result[:1000] if len(result) > 1000 else result)
    if len(result) > 1000:
        print("... (结果过长，已截断)")
    print("-" * 40)
    
    # 检查输出文件
    if Path(output_file).exists():
        print(f"\n📄 RDF文件已生成: {output_file}")
        
        # 显示文件大小
        file_size = Path(output_file).stat().st_size
        print(f"   文件大小: {file_size:,} 字节")
        
        # 显示前20行
        print("\n📋 Turtle文件预览（前20行）：")
        print("-" * 40)
        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if i >= 20:
                    print("... (更多内容省略)")
                    break
                print(line.rstrip())
        print("-" * 40)
        
        # 检查验证脚本（由convert_rdf函数内部生成）
        if Path(validation_script).exists():
            print(f"\n✅ 验证脚本已生成: {validation_script}")
            
            # 运行验证脚本
            print("\n🔬 运行验证脚本...")
            import subprocess
            try:
                result = subprocess.run(
                    [sys.executable, validation_script, output_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                print("\n验证结果：")
                print("-" * 40)
                print(result.stdout)
                if result.stderr:
                    print("错误信息：")
                    print(result.stderr)
                print("-" * 40)
            except subprocess.TimeoutExpired:
                print("⚠️ 验证脚本执行超时")
            except Exception as e:
                print(f"⚠️ 验证脚本执行失败: {e}")
        else:
            print("⚠️ 验证脚本未生成（应该由convert_rdf函数内部生成）")
            
    else:
        print(f"\n⚠️ RDF文件未生成: {output_file}")
    
    print("\n🎉 任务完成！")

if __name__ == "__main__":
    convert_core_to_rdf()