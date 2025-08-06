"""
分层编译器

核心功能：
1. 分解任务为抽象层次
2. 判断每层的可编译性（决策树大小）
3. 生成分层的执行计划
"""

import time
from typing import List, Optional, Dict, Any
from .ir_types import LayeredIR, Layer, LayerType, CompilabilityLevel
from .layer_classifier import LayerClassifier


class HierarchicalCompiler:
    """分层编译器"""
    
    def __init__(self, 
                 compilation_threshold: int = 100000,
                 enable_caching: bool = True):
        """
        Args:
            compilation_threshold: 决策树大小阈值，超过则不编译
            enable_caching: 是否启用编译缓存
        """
        self.classifier = LayerClassifier()
        self.compilation_threshold = compilation_threshold
        self.enable_caching = enable_caching
        self.compilation_cache = {} if enable_caching else None
        
    def compile(self, task: str) -> LayeredIR:
        """编译任务为分层IR"""
        start_time = time.time()
        
        # 检查缓存
        if self.enable_caching and task in self.compilation_cache:
            cached_ir = self.compilation_cache[task]
            cached_ir.metadata['cache_hit'] = True
            return cached_ir
        
        # 分解任务为层次
        layers = self.classifier.decompose_into_layers(task)
        
        # 逐层判断可编译性
        compiled_layers = []
        for layer in layers:
            if self._should_compile_layer(layer):
                # 该层可编译
                compiled_layer = self._compile_layer(layer)
                compiled_layers.append(compiled_layer)
            else:
                # 该层需要探索，停止编译
                compiled_layers.append(layer)
                # 将剩余层标记为需要探索
                remaining_start = layers.index(layer) + 1
                for remaining_layer in layers[remaining_start:]:
                    remaining_layer.type = LayerType.REACT
                    compiled_layers.append(remaining_layer)
                break
        
        # 创建分层IR
        ir = LayeredIR(
            task=task,
            layers=compiled_layers,
            metadata={
                'compilation_time': time.time() - start_time,
                'total_layers': len(compiled_layers),
                'compiled_layers': len([l for l in compiled_layers if l.type == LayerType.COMPILED]),
                'cache_hit': False
            }
        )
        
        # 缓存结果
        if self.enable_caching:
            self.compilation_cache[task] = ir
        
        return ir
    
    def _should_compile_layer(self, layer: Layer) -> bool:
        """判断层是否应该编译"""
        # 如果已经是ReAct层，不编译
        if layer.type == LayerType.REACT:
            return False
        
        # 估算决策树大小
        tree_size = self.classifier.estimate_decision_tree_size(layer)
        
        # 判断是否超过阈值
        return tree_size < self.compilation_threshold
    
    def _compile_layer(self, layer: Layer) -> Layer:
        """编译单个层"""
        # 如果已经有代码，直接返回
        if layer.code:
            return layer
        
        # 根据层的描述生成代码
        # 这里简化处理，实际应该调用代码生成器
        layer.code = self._generate_code_for_layer(layer)
        layer.type = LayerType.COMPILED
        
        return layer
    
    def _generate_code_for_layer(self, layer: Layer) -> str:
        """为层生成代码（简化版本）"""
        # 在实际实现中，这里应该调用专门的代码生成器
        # 或者使用模板系统
        
        templates = {
            "统计": '''
import csv
from collections import defaultdict

def analyze_sales_by_region():
    """按地区统计销售量"""
    # 读取CSV文件
    sales_by_region = defaultdict(int)
    
    try:
        with open('sales_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                region = row['region']
                quantity = int(row['quantity'])
                sales_by_region[region] += quantity
        
        # 转换为普通字典
        result = dict(sales_by_region)
        print(f"统计完成: {result}")
        return result
    except Exception as e:
        print(f"统计失败: {e}")
        return {"error": str(e)}

result = analyze_sales_by_region()
''',
            "文件操作": '''
import os
import json

def execute_file_operation():
    # 文件操作的标准实现
    # 模拟读取文件并计算数值总和
    try:
        # 假设读取config.json
        data = {"values": [10, 20, 30, 40, 50]}  # 模拟文件内容
        total = sum(data.get("values", []))
        return {"success": True, "total": total}
    except Exception as e:
        return {"success": False, "error": str(e)}

result = execute_file_operation()
''',
            "架构设计": '''
# 系统架构设计
architecture = {
    "pattern": "microservices",
    "components": ["api", "database", "cache", "queue"],
    "deployment": "kubernetes"
}
result = architecture
''',
            "优化流程": '''
# 性能优化流程
def profile_current_performance():
    return {"cpu": 70, "memory": 80, "io": 45}

def identify_bottlenecks(metrics):
    return [k for k, v in metrics.items() if v > 75]

def generate_strategies(bottlenecks):
    strategies = {}
    for b in bottlenecks:
        if b == "cpu":
            strategies[b] = "optimize algorithms"
        elif b == "memory":
            strategies[b] = "implement caching"
        elif b == "io":
            strategies[b] = "use async operations"
    return strategies

def apply_best_strategy(strategies):
    return list(strategies.values())[0] if strategies else "no optimization needed"

def optimize_performance():
    metrics = profile_current_performance()
    bottlenecks = identify_bottlenecks(metrics)
    strategies = generate_strategies(bottlenecks)
    return apply_best_strategy(strategies)

result = optimize_performance()
'''
        }
        
        # 匹配模板
        for key, template in templates.items():
            if key in layer.name:
                return template
        
        # 默认模板
        return f'''
# {layer.name}
def execute_layer_{layer.level}():
    """自动生成的层执行代码"""
    # TODO: 实现 {layer.description}
    pass

result = execute_layer_{layer.level}()
'''
    
    def analyze_compilability(self, task: str) -> Dict[str, Any]:
        """分析任务的可编译性"""
        layers = self.classifier.decompose_into_layers(task)
        
        analysis = {
            'task': task,
            'total_layers': len(layers),
            'layer_details': []
        }
        
        for layer in layers:
            tree_size = self.classifier.estimate_decision_tree_size(layer)
            compilable = tree_size < self.compilation_threshold
            
            analysis['layer_details'].append({
                'level': layer.level,
                'name': layer.name,
                'tree_size': tree_size,
                'compilable': compilable,
                'reason': layer.metadata.get('reason', 'N/A')
            })
        
        # 计算整体可编译性
        compilable_layers = sum(1 for d in analysis['layer_details'] if d['compilable'])
        analysis['compilability_ratio'] = compilable_layers / len(layers) if layers else 0
        analysis['recommended_approach'] = self._recommend_approach(analysis['compilability_ratio'])
        
        return analysis
    
    def _recommend_approach(self, ratio: float) -> str:
        """根据可编译比例推荐执行方式"""
        if ratio >= 0.8:
            return "完全编译执行"
        elif ratio >= 0.5:
            return "混合执行（编译+ReAct）"
        elif ratio >= 0.2:
            return "以ReAct为主，顶层编译"
        else:
            return "完全ReAct执行"