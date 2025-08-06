"""
模板重用机制演示

展示如何通过LLM语义理解实现代码模板的智能重用。
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.llm_only_compiler import LLMOnlyCompiler
from compiler.hierarchical_executor import HierarchicalExecutor


def demo_docker_size_tasks():
    """演示Docker镜像大小筛选任务的模板重用"""
    print("Docker镜像筛选任务演示")
    print("=" * 60)
    
    # 创建编译器
    compiler = LLMOnlyCompiler(
        template_storage_path="demo_templates.json"
    )
    
    # 一系列相似的任务
    tasks = [
        "列出本机size大于50m的docker image",
        "列出本机size大于100m的docker image",
        "显示docker镜像中超过200MB的",
        "查看大于1G的docker images",
        "docker镜像里哪些占用超过500兆",
    ]
    
    print(f"\n将依次编译{len(tasks)}个任务，观察模板重用效果\n")
    
    for i, task in enumerate(tasks, 1):
        print(f"\n任务{i}: {task}")
        print("-" * 50)
        
        # 编译
        ir = compiler.compile(task)
        
        # 显示编译结果
        if ir.metadata.get('template_reused'):
            print(f"结果: 重用了模板 {ir.metadata.get('template_id')}")
        else:
            if ir.metadata.get('new_template_created'):
                print("结果: 创建了新的参数化模板")
            else:
                print("结果: 普通编译（未参数化）")
    
    # 显示统计
    print(f"\n\n编译统计:")
    print("-" * 30)
    stats = compiler.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


def demo_file_operations():
    """演示文件操作任务的模板重用"""
    print("\n\n文件操作任务演示")
    print("=" * 60)
    
    # 使用新的存储文件
    compiler = LLMOnlyCompiler(
        template_storage_path="demo_templates_file.json"
    )
    
    tasks = [
        "查找当前目录下所有的.py文件",
        "查找当前目录下所有的.js文件",
        "列出所有的.txt文件",
        "找出所有.md格式的文件",
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n任务{i}: {task}")
        print("-" * 50)
        
        ir = compiler.compile(task)
        
        if ir.metadata.get('template_reused'):
            print(f"✓ 重用模板，节省了LLM调用")
            # 执行看看效果
            executor = HierarchicalExecutor()
            result = executor.execute(ir)
            if result.is_success():
                print(f"执行成功！")
        else:
            print("→ 创建新模板")


def demo_data_analysis():
    """演示数据分析任务的模板重用"""
    print("\n\n数据分析任务演示")
    print("=" * 60)
    
    compiler = LLMOnlyCompiler(
        template_storage_path="demo_templates_analysis.json"
    )
    
    # 先创建一些测试数据
    import json
    test_data = {
        "sales": [100, 200, 150, 300, 250],
        "costs": [80, 150, 120, 200, 180],
        "profits": [20, 50, 30, 100, 70]
    }
    with open("test_data.json", "w") as f:
        json.dump(test_data, f)
    
    tasks = [
        "计算test_data.json中sales的平均值",
        "计算test_data.json中costs的平均值",
        "计算test_data.json中profits的平均值",
        "求test_data.json里sales的总和",
        "统计test_data.json中costs的总数",
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n任务{i}: {task}")
        print("-" * 50)
        
        ir = compiler.compile(task)
        
        # 执行并显示结果
        executor = HierarchicalExecutor()
        result = executor.execute(ir)
        
        if ir.metadata.get('template_reused'):
            print("✓ 模板重用成功")
        
        if result.is_success() and result.final_output:
            print(f"执行结果: {result.final_output}")
    
    # 清理
    if os.path.exists("test_data.json"):
        os.remove("test_data.json")
    
    # 最终统计
    print(f"\n\n总体统计:")
    print("-" * 30)
    stats = compiler.get_stats()
    print(f"总编译次数: {stats['total_compilations']}")
    print(f"模板重用次数: {stats['template_reuses']}")
    print(f"创建模板数: {stats['new_templates']}")
    print(f"重用率: {stats['reuse_rate']}")
    
    # 显示核心优势
    print("\n\n核心优势:")
    print("1. LLM能理解语义变化（显示/列出/查看）")
    print("2. 自动处理单位转换（50m/50MB/50兆）")
    print("3. 首次编译后，相似任务直接重用")
    print("4. 显著减少LLM调用和响应时间")


def cleanup_demo_files():
    """清理演示文件"""
    demo_files = [
        "demo_templates.json",
        "demo_templates_file.json", 
        "demo_templates_analysis.json"
    ]
    
    for file in demo_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"已删除: {file}")


if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv("GEMINI_API_KEY"):
        print("错误: 请设置GEMINI_API_KEY环境变量")
        sys.exit(1)
    
    try:
        # 运行演示
        demo_docker_size_tasks()
        demo_file_operations()
        demo_data_analysis()
        
    finally:
        # 清理
        print("\n\n清理演示文件...")
        cleanup_demo_files()