"""
自然语言分层编译器

基于条件反射 vs 探索的二分法，实现分层编译机制。
核心思想：在每个抽象层次上判断决策树是否小到可以编译。
"""

from .hierarchical_compiler import HierarchicalCompiler
from .layer_classifier import LayerClassifier
from .hierarchical_executor import HierarchicalExecutor
from .ir_types import LayeredIR, CompilabilityLevel, LayerType
from .llm_compiler import LLMCompiler
from .template_manager import TemplateManager, TaskTemplate, Parameter
from .llm_template_matcher import LLMTemplateMatcher
from .template_aware_compiler import TemplateAwareCompiler
from .llm_only_compiler import LLMOnlyCompiler

__all__ = [
    'HierarchicalCompiler',
    'LayerClassifier', 
    'HierarchicalExecutor',
    'LayeredIR',
    'CompilabilityLevel',
    'LayerType',
    'LLMCompiler',
    'TemplateManager',
    'TaskTemplate',
    'Parameter',
    'LLMTemplateMatcher',
    'TemplateAwareCompiler',
    'LLMOnlyCompiler'
]