"""
层次分类器

识别任务的抽象层次，判断每层的可编译性。
核心：判断决策树是否小到可以实际编译。
"""

import re
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from .ir_types import CompilabilityLevel, Layer, LayerType


@dataclass
class TaskPattern:
    """任务模式"""
    pattern: str                    # 正则表达式
    category: str                   # 任务类别
    typical_tree_size: str         # 典型决策树规模：small/medium/large/astronomical


class LayerClassifier:
    """层次分类器"""
    
    def __init__(self):
        # 定义常见任务模式及其决策树规模
        self.task_patterns = [
            # 小决策树 - 可编译
            TaskPattern(r"读取.*文件", "file_read", "small"),
            TaskPattern(r"计算.*总和|平均", "calculation", "small"),
            TaskPattern(r"创建.*目录", "file_operation", "small"),
            TaskPattern(r"解析.*JSON", "data_parsing", "small"),
            TaskPattern(r"按.*统计|分组|汇总", "data_analysis", "small"),
            TaskPattern(r"分析.*数据", "data_analysis", "small"),
            
            # 中等决策树 - 高层可编译
            TaskPattern(r"创建.*API", "api_creation", "medium"),
            TaskPattern(r"实现.*CRUD", "crud_implementation", "medium"),
            TaskPattern(r"生成.*报告", "report_generation", "medium"),
            
            # 大决策树 - 需要分层
            TaskPattern(r"优化.*性能", "optimization", "large"),
            TaskPattern(r"设计.*系统", "system_design", "large"),
            TaskPattern(r"重构.*代码", "refactoring", "large"),
            
            # 天文数字决策树 - 主要靠探索
            TaskPattern(r"调试.*问题", "debugging", "astronomical"),
            TaskPattern(r"修复.*bug", "bug_fixing", "astronomical"),
            TaskPattern(r"找出.*原因", "root_cause_analysis", "astronomical"),
        ]
        
        # 编译阈值（简化的决策树大小估算）
        self.TREE_SIZE_THRESHOLDS = {
            "small": 100,        # 可以完全枚举
            "medium": 10000,     # 可以部分编译
            "large": 1000000,    # 只能编译顶层
            "astronomical": float('inf')  # 无法编译
        }
    
    def classify_task(self, task: str) -> Tuple[str, str]:
        """分类任务，返回(类别, 决策树规模)"""
        task_lower = task.lower()
        
        for pattern in self.task_patterns:
            if re.search(pattern.pattern, task_lower):
                return pattern.category, pattern.typical_tree_size
        
        # 默认假设是中等复杂度
        return "general", "medium"
    
    def decompose_into_layers(self, task: str) -> List[Layer]:
        """将任务分解为抽象层次"""
        category, tree_size = self.classify_task(task)
        
        if category == "file_read":
            return self._decompose_file_read(task)
        elif category == "api_creation":
            return self._decompose_api_creation(task)
        elif category == "optimization":
            return self._decompose_optimization(task)
        elif category == "debugging":
            return self._decompose_debugging(task)
        elif category == "data_analysis":
            return self._decompose_data_analysis(task)
        else:
            return self._decompose_general(task, tree_size)
    
    def _decompose_file_read(self, task: str) -> List[Layer]:
        """分解文件读取任务 - 通常完全可编译"""
        return [
            Layer(
                level=1,
                name="文件操作",
                description="读取和处理文件",
                type=LayerType.COMPILED,
                code='''
import os

def read_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

# 执行任务
result = read_file('target_file.txt')
''',
                metadata={"tree_size": "small", "confidence": 0.95}
            )
        ]
    
    def _decompose_api_creation(self, task: str) -> List[Layer]:
        """分解API创建任务 - 分层编译"""
        return [
            Layer(
                level=1,
                name="架构设计",
                description="API整体架构",
                type=LayerType.COMPILED,
                code='''
# API架构 - 标准RESTful模式
architecture = {
    "framework": "FastAPI",
    "pattern": "REST",
    "components": ["models", "routes", "services", "database"]
}
''',
                metadata={"tree_size": "small", "confidence": 0.9}
            ),
            Layer(
                level=2,
                name="框架代码",
                description="生成API框架代码",
                type=LayerType.COMPILED,
                code='''
# 标准CRUD模板
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    description: str

@app.get("/items", response_model=List[Item])
async def read_items():
    pass

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    pass
''',
                metadata={"tree_size": "medium", "confidence": 0.85}
            ),
            Layer(
                level=3,
                name="业务逻辑",
                description="实现具体业务逻辑",
                type=LayerType.REACT,
                task="根据具体需求实现业务规则、数据验证和权限控制",
                metadata={"tree_size": "large", "reason": "需要理解具体业务需求"}
            )
        ]
    
    def _decompose_optimization(self, task: str) -> List[Layer]:
        """分解优化任务 - 顶层可编译，底层探索"""
        return [
            Layer(
                level=1,
                name="优化流程",
                description="标准优化流程",
                type=LayerType.COMPILED,
                code='''
# 性能优化标准流程
optimization_steps = [
    "profile_performance()",
    "identify_bottlenecks()",
    "generate_optimization_strategies()",
    "implement_optimizations()",
    "measure_improvements()"
]
''',
                metadata={"tree_size": "small", "confidence": 0.95}
            ),
            Layer(
                level=2,
                name="优化策略",
                description="常见优化模式",
                type=LayerType.COMPILED,
                code='''
# 优化模式库
optimization_patterns = {
    "n+1_queries": "implement_eager_loading",
    "slow_loops": "vectorize_operations",
    "memory_leak": "fix_circular_references",
    "blocking_io": "use_async_operations"
}
''',
                metadata={"tree_size": "medium", "confidence": 0.8}
            ),
            Layer(
                level=3,
                name="具体实施",
                description="分析代码并实施优化",
                type=LayerType.REACT,
                task="分析具体代码结构，识别性能瓶颈，选择并实施最合适的优化方案",
                metadata={"tree_size": "astronomical", "reason": "代码结构的组合爆炸"}
            )
        ]
    
    def _decompose_debugging(self, task: str) -> List[Layer]:
        """分解调试任务 - 主要依赖探索"""
        return [
            Layer(
                level=1,
                name="调试方法论",
                description="系统化调试流程",
                type=LayerType.COMPILED,
                code='''
# 调试方法论 - 可编译的高层流程
debug_methodology = [
    "reproduce_issue()",
    "collect_diagnostics()",
    "form_hypotheses()",
    "test_hypotheses()",
    "implement_fix()",
    "verify_fix()"
]
''',
                metadata={"tree_size": "small", "confidence": 0.9}
            ),
            Layer(
                level=2,
                name="诊断和修复",
                description="具体的调试过程",
                type=LayerType.REACT,
                task="重现问题，收集信息，形成假设，验证假设，实施修复",
                metadata={"tree_size": "astronomical", "reason": "状态空间组合爆炸"}
            )
        ]
    
    def _decompose_general(self, task: str, tree_size: str) -> List[Layer]:
        """通用任务分解"""
        if tree_size == "small":
            # 小决策树 - 直接编译
            return [
                Layer(
                    level=1,
                    name="直接执行",
                    description=task,
                    type=LayerType.COMPILED,
                    code=f"# TODO: 实现 {task}",
                    metadata={"tree_size": tree_size}
                )
            ]
        else:
            # 大决策树 - 需要探索
            return [
                Layer(
                    level=1,
                    name="任务执行",
                    description=task,
                    type=LayerType.REACT,
                    task=task,
                    metadata={"tree_size": tree_size}
                )
            ]
    
    def estimate_decision_tree_size(self, layer: Layer) -> int:
        """估算层的决策树大小"""
        tree_size_str = layer.metadata.get("tree_size", "medium")
        
        if tree_size_str in self.TREE_SIZE_THRESHOLDS:
            return self.TREE_SIZE_THRESHOLDS[tree_size_str]
        
        # 基于一些启发式规则估算
        if layer.type == LayerType.COMPILED and layer.code:
            # 编译代码的复杂度估算
            lines = len(layer.code.split('\n'))
            branches = layer.code.count('if ') + layer.code.count('elif ')
            loops = layer.code.count('for ') + layer.code.count('while ')
            
            # 简化的复杂度计算
            return lines * (1 + branches * 2 + loops * 10)
        
        return self.TREE_SIZE_THRESHOLDS["medium"]