"""
中间表示（IR）类型定义

使用 Python 作为 IR，保留语义信息，同时支持分层表示。
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


class CompilabilityLevel(Enum):
    """可编译性级别"""
    FULLY_COMPILABLE = "fully_compilable"      # 决策树很小，可完全编译
    PARTIALLY_COMPILABLE = "partially_compilable"  # 部分可编译
    REQUIRES_EXPLORATION = "requires_exploration"  # 决策树太大，需要探索


class LayerType(Enum):
    """层次类型"""
    COMPILED = "compiled"    # 可编译层（条件反射）
    REACT = "react"         # 需要探索层（ReAct）


@dataclass
class Layer:
    """抽象层次"""
    level: int                      # 层次级别（1是最高层）
    name: str                       # 层次名称
    description: str                # 层次描述
    type: LayerType                # 层次类型
    code: Optional[str] = None      # Python代码（编译层）
    task: Optional[str] = None      # 任务描述（ReAct层）
    metadata: Dict[str, Any] = None # 元数据
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LayeredIR:
    """分层中间表示"""
    task: str                      # 原始任务
    layers: List[Layer]            # 层次列表
    metadata: Dict[str, Any]       # 元数据
    
    def get_compiled_layers(self) -> List[Layer]:
        """获取所有可编译层"""
        return [l for l in self.layers if l.type == LayerType.COMPILED]
    
    def get_react_layers(self) -> List[Layer]:
        """获取所有需要探索的层"""
        return [l for l in self.layers if l.type == LayerType.REACT]
    
    def get_deepest_compiled_level(self) -> int:
        """获取最深的可编译层级"""
        compiled = self.get_compiled_layers()
        return max([l.level for l in compiled]) if compiled else 0


@dataclass
class ExecutionResult:
    """执行结果"""
    level: int                     # 执行的层级
    type: LayerType               # 执行类型
    success: bool                 # 是否成功
    output: Any                   # 输出结果
    context: Dict[str, Any]       # 执行上下文
    error: Optional[str] = None   # 错误信息


@dataclass
class LayeredExecutionResult:
    """分层执行结果"""
    task: str                            # 原始任务
    results: List[ExecutionResult]       # 各层执行结果
    final_output: Any                    # 最终输出
    total_llm_calls: int = 0            # LLM调用次数
    execution_time: float = 0.0         # 总执行时间
    
    def is_success(self) -> bool:
        """判断整体是否成功"""
        return all(r.success for r in self.results)