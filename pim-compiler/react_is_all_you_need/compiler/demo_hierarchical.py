"""
分层编译演示

展示如何将复杂任务分解为多个抽象层次，
高层可编译，底层需要探索。
"""

import os
import sys
import json
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.llm_compiler import LLMCompiler
from compiler.hierarchical_executor import HierarchicalExecutor
from compiler.ir_types import LayeredIR, Layer, LayerType


class HierarchicalLLMCompiler(LLMCompiler):
    """支持分层编译的LLM编译器"""
    
    def analyze_task_layers(self, task: str) -> List[Dict[str, Any]]:
        """分析任务的层次结构"""
        
        prompt = f"""分析任务的抽象层次，将其分解为从高到低的多个层次。

任务：{task}

输出JSON格式：
{{
    "layers": [
        {{
            "level": 1,
            "name": "层次名称",
            "description": "该层的任务描述",
            "decision_tree_size": 100,
            "compilable": true,
            "reason": "可编译/不可编译的原因"
        }}
    ]
}}

分层原则：
1. 高层是抽象的流程和策略（通常可编译）
2. 中层是具体的实现步骤（可能可编译）
3. 底层是需要创造性或探索的部分（通常不可编译）

只输出JSON，不要有其他内容。
"""
        
        try:
            from langchain.schema import SystemMessage, HumanMessage
            response = self.llm.invoke([
                SystemMessage(content=prompt),
                HumanMessage(content="开始分析")
            ])
            
            content = response.content.strip()
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            result = json.loads(content)
            return result.get("layers", [])
            
        except Exception as e:
            print(f"层次分析错误: {e}")
            # 返回默认的单层结构
            return [{
                "level": 1,
                "name": "任务执行",
                "description": task,
                "decision_tree_size": 10000,
                "compilable": False,
                "reason": "无法分析层次结构"
            }]
    
    def compile_layer(self, layer_info: Dict[str, Any]) -> Layer:
        """编译单个层次"""
        
        if layer_info["compilable"]:
            # 生成该层的代码
            prompt = f"""为以下层次生成Python代码：

层次：{layer_info['name']}
描述：{layer_info['description']}
抽象级别：第{layer_info['level']}层

要求：
1. 只使用Python标准库
2. 生成可执行的代码片段
3. 如果需要下层的结果，使用context字典获取
4. 将本层结果存储在result变量中
5. 只生成代码，不要解释

context字典中可能包含：
- 上层传递的参数
- 下层返回的结果（如context['layer_2_result']）
"""
            
            try:
                from langchain.schema import SystemMessage, HumanMessage
                response = self.llm.invoke([
                    SystemMessage(content=prompt),
                    HumanMessage(content="生成代码")
                ])
                
                code = response.content.strip()
                if '```python' in code:
                    code = code.split('```python')[1].split('```')[0].strip()
                elif '```' in code:
                    code = code.split('```')[1].split('```')[0].strip()
                
                return Layer(
                    level=layer_info["level"],
                    name=layer_info["name"],
                    description=layer_info["description"],
                    type=LayerType.COMPILED,
                    code=code,
                    metadata={
                        "tree_size": layer_info["decision_tree_size"],
                        "reason": layer_info["reason"]
                    }
                )
                
            except Exception as e:
                print(f"代码生成错误: {e}")
        
        # 不可编译的层，返回ReAct任务
        return Layer(
            level=layer_info["level"],
            name=layer_info["name"],
            description=layer_info["description"],
            type=LayerType.REACT,
            task=layer_info["description"],
            metadata={
                "tree_size": layer_info["decision_tree_size"],
                "reason": layer_info["reason"]
            }
        )
    
    def compile_hierarchical(self, task: str) -> LayeredIR:
        """分层编译任务"""
        
        # 1. 分析层次结构
        print("1. 分析任务层次...")
        layers_info = self.analyze_task_layers(task)
        
        # 2. 逐层编译
        print("\n2. 逐层编译...")
        layers = []
        for layer_info in layers_info:
            print(f"   编译第{layer_info['level']}层: {layer_info['name']}")
            layer = self.compile_layer(layer_info)
            layers.append(layer)
        
        # 3. 创建分层IR
        return LayeredIR(
            task=task,
            layers=layers,
            metadata={
                "total_layers": len(layers),
                "compiled_layers": len([l for l in layers if l.type == LayerType.COMPILED])
            }
        )


def demo_hierarchical_task():
    """演示分层编译的效果"""
    
    print("分层编译演示")
    print("=" * 60)
    
    # 检查API密钥
    if not os.getenv("GEMINI_API_KEY"):
        print("错误: 请设置GEMINI_API_KEY环境变量")
        return
    
    # 创建编译器
    compiler = HierarchicalLLMCompiler()
    
    # 定义一个复杂的多层任务
    task = """开发一个Web应用的用户认证系统，包括：
1. 设计认证架构（JWT vs Session）
2. 实现用户注册和登录API
3. 添加密码加密和验证
4. 实现会话管理
5. 添加安全措施（防暴力破解、CSRF保护）"""
    
    print(f"任务: {task}")
    print("\n" + "-" * 60)
    
    # 分层编译
    ir = compiler.compile_hierarchical(task)
    
    # 显示编译结果
    print("\n3. 编译结果:")
    print(f"   总层数: {len(ir.layers)}")
    print(f"   已编译: {len([l for l in ir.layers if l.type == LayerType.COMPILED])}层")
    print(f"   需探索: {len([l for l in ir.layers if l.type == LayerType.REACT])}层")
    
    print("\n4. 各层详情:")
    for layer in ir.layers:
        status = "✓ 已编译" if layer.type == LayerType.COMPILED else "✗ 需探索"
        print(f"\n   第{layer.level}层 - {layer.name}: {status}")
        print(f"   描述: {layer.description}")
        print(f"   决策树: {layer.metadata.get('tree_size', 'N/A')}")
        print(f"   原因: {layer.metadata.get('reason', 'N/A')}")
        
        if layer.type == LayerType.COMPILED and layer.code:
            print(f"   生成的代码:")
            print("   " + "-" * 40)
            for line in layer.code.split('\n')[:10]:  # 只显示前10行
                if line.strip():
                    print(f"   {line}")
            if len(layer.code.split('\n')) > 10:
                print("   ...")
    
    # 执行分层IR
    print("\n5. 执行分层IR:")
    print("-" * 60)
    
    executor = HierarchicalExecutor()
    result = executor.execute(ir)
    
    # 分析效果
    print("\n6. 分层编译的优势:")
    print(f"   - 高层架构设计可以编译为标准模式")
    print(f"   - 中层实现可以部分编译")
    print(f"   - 底层细节保留探索的灵活性")
    print(f"   - 减少了{ir.metadata['compiled_layers']}次LLM调用")
    
    # 对比纯ReAct
    print("\n7. 对比分析:")
    print("   纯ReAct方式: 每个步骤都需要LLM调用")
    print(f"   分层编译方式: {ir.metadata['compiled_layers']}/{len(ir.layers)}层已编译")
    print(f"   效率提升: 约{(ir.metadata['compiled_layers']/len(ir.layers)*100):.0f}%的工作无需LLM")


def demo_simple_hierarchical():
    """演示一个简单的分层任务"""
    
    print("\n\n简单分层任务演示")
    print("=" * 60)
    
    # 创建测试数据
    data = {
        "users": [
            {"id": 1, "name": "Alice", "age": 25, "city": "北京"},
            {"id": 2, "name": "Bob", "age": 30, "city": "上海"},
            {"id": 3, "name": "Charlie", "age": 35, "city": "北京"},
            {"id": 4, "name": "David", "age": 28, "city": "广州"},
            {"id": 5, "name": "Eve", "age": 32, "city": "上海"}
        ]
    }
    
    # 保存为JSON文件
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("已创建测试数据: users.json")
    
    # 定义分层任务
    task = """分析users.json文件中的用户数据：
1. 统计每个城市的用户数量
2. 计算平均年龄
3. 找出年龄最大的用户
4. 生成分析报告"""
    
    print(f"\n任务: {task}")
    
    # 手动构建分层IR（演示概念）
    layers = [
        Layer(
            level=1,
            name="数据加载层",
            description="读取JSON文件并解析数据",
            type=LayerType.COMPILED,
            code="""
import json

# 读取用户数据
with open('users.json', 'r', encoding='utf-8') as f:
    users_data = json.load(f)
    
result = users_data['users']
next_context = {'users': result}
""",
            metadata={"tree_size": 10, "reason": "文件读取是确定性操作"}
        ),
        Layer(
            level=2,
            name="统计分析层",
            description="执行各种统计分析",
            type=LayerType.COMPILED,
            code="""
from collections import defaultdict

users = context.get('users', [])

# 1. 统计每个城市的用户数量
city_count = defaultdict(int)
for user in users:
    city_count[user['city']] += 1

# 2. 计算平均年龄
ages = [user['age'] for user in users]
avg_age = sum(ages) / len(ages) if ages else 0

# 3. 找出年龄最大的用户
oldest_user = max(users, key=lambda u: u['age']) if users else None

result = {
    'city_statistics': dict(city_count),
    'average_age': avg_age,
    'oldest_user': oldest_user,
    'total_users': len(users)
}

next_context = {'analysis_result': result}
""",
            metadata={"tree_size": 100, "reason": "统计计算是确定性的"}
        ),
        Layer(
            level=3,
            name="报告生成层",
            description="生成易读的分析报告",
            type=LayerType.COMPILED,
            code="""
analysis = context.get('analysis_result', {})

# 生成分析报告
report_lines = [
    "用户数据分析报告",
    "=" * 40,
    f"总用户数: {analysis.get('total_users', 0)}",
    f"平均年龄: {analysis.get('average_age', 0):.1f}岁",
    "",
    "城市分布:"
]

for city, count in analysis.get('city_statistics', {}).items():
    report_lines.append(f"  - {city}: {count}人")

if analysis.get('oldest_user'):
    user = analysis['oldest_user']
    report_lines.extend([
        "",
        f"年龄最大的用户: {user['name']} ({user['age']}岁, {user['city']})"
    ])

result = "\\n".join(report_lines)
print(result)
""",
            metadata={"tree_size": 50, "reason": "报告格式是预定义的"}
        )
    ]
    
    # 创建IR并执行
    ir = LayeredIR(
        task=task,
        layers=layers,
        metadata={
            "total_layers": 3,
            "compiled_layers": 3
        }
    )
    
    print("\n执行分层编译结果:")
    print("-" * 60)
    
    executor = HierarchicalExecutor()
    result = executor.execute(ir)
    
    # 清理
    if os.path.exists("users.json"):
        os.remove("users.json")
    
    print("\n分层编译的关键优势:")
    print("1. 每一层都是独立的、可测试的")
    print("2. 高层的抽象（如统计逻辑）可以重用")
    print("3. 层与层之间通过context传递数据")
    print("4. 完全避免了LLM调用，实现毫秒级执行")


if __name__ == "__main__":
    # 运行两个演示
    demo_hierarchical_task()
    demo_simple_hierarchical()