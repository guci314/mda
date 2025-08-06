"""
最终的LLM编译演示

展示完整的编译流程和执行效果。
"""

import csv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.llm_compiler import LLMCompiler
from compiler.hierarchical_executor import HierarchicalExecutor


def main():
    """主演示程序"""
    print("基于LLM的自然语言编译器 - 最终演示")
    print("=" * 60)
    
    # 检查API密钥
    if not os.getenv("GEMINI_API_KEY"):
        print("错误: 请设置GEMINI_API_KEY环境变量")
        return
    
    # 创建销售数据
    print("\n1. 创建示例数据:")
    data = [
        ["date", "region", "product", "quantity", "price"],
        ["2024-01-01", "华东", "产品A", "100", "50"],
        ["2024-01-01", "华北", "产品A", "80", "50"],
        ["2024-01-01", "华南", "产品A", "120", "50"],
        ["2024-01-02", "华东", "产品B", "60", "80"],
        ["2024-01-02", "华北", "产品B", "90", "80"],
        ["2024-01-02", "华南", "产品B", "75", "80"],
    ]
    
    filename = "sales_data.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print(f"   已创建文件: {filename}")
    print("   列名: date, region, product, quantity, price")
    
    # 创建LLM编译器
    compiler = LLMCompiler()
    
    # 定义任务
    task = f"""读取{filename}文件，该文件有以下列：date,region,product,quantity,price。
请使用标准库csv模块，按region列分组，统计每个地区的quantity列总和。
只使用Python标准库，不要使用pandas。"""
    
    print(f"\n2. 编译任务:")
    print(f"   {task}")
    
    # 分析可编译性
    print("\n3. 分析可编译性:")
    analysis = compiler.analyze_compilability(task)
    print(f"   - 决策树大小: {analysis.get('decision_tree_size', 'N/A')}")
    print(f"   - 可编译: {'是' if analysis.get('compilable', False) else '否'}")
    print(f"   - 置信度: {analysis.get('confidence', 0):.2f}")
    print(f"   - 理由: {analysis.get('reasoning', 'N/A')}")
    
    # 编译
    print("\n4. 编译为Python代码:")
    ir = compiler.compile(task)
    
    if ir.metadata.get('compiled'):
        print("   ✓ 编译成功!")
        print("\n   生成的代码:")
        print("   " + "-" * 50)
        code = ir.layers[0].code
        for line in code.split('\n'):
            if line.strip():
                print(f"   {line}")
        print("   " + "-" * 50)
        
        # 执行
        print("\n5. 执行编译后的代码:")
        executor = HierarchicalExecutor()
        result = executor.execute(ir)
        
        if result.is_success() and result.final_output:
            print("\n6. 执行结果:")
            output = result.final_output
            if isinstance(output, dict):
                print("   地区销售量统计:")
                for region, quantity in output.items():
                    print(f"   - {region}: {quantity}")
            else:
                print(f"   {output}")
                
            print(f"\n7. 性能统计:")
            print(f"   - 执行时间: {result.execution_time:.3f}秒")
            print(f"   - LLM调用: {result.total_llm_calls}次")
            print(f"   - 编译执行 vs ReAct探索: 编译节省了LLM调用")
    else:
        print("   ✗ 任务不可编译")
        print(f"   原因: {ir.layers[0].metadata.get('reasoning', 'N/A')}")
    
    # 清理
    if os.path.exists(filename):
        os.remove(filename)
        print(f"\n已删除临时文件: {filename}")
    
    print("\n" + "=" * 60)
    print("核心洞察：")
    print("1. LLM可以理解任务语义并判断可编译性")
    print("2. 简单的数据处理任务可以编译为确定性代码")
    print("3. 编译执行避免了运行时的LLM调用，提高效率")
    print("4. 决策树大小是判断可编译性的关键指标")


if __name__ == "__main__":
    main()