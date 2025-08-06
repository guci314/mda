"""
纯LLM模板编译器

仅使用LLM进行模板匹配和参数提取，删除了向量相似度匹配功能。
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .template_aware_compiler import TemplateAwareCompiler
from .llm_template_matcher import LLMTemplateMatcher
from .template_manager import TemplateManager, TaskTemplate
from .ir_types import LayeredIR, Layer, LayerType


class LLMOnlyCompiler(TemplateAwareCompiler):
    """纯LLM模板编译器"""
    
    def __init__(self,
                 template_storage_path: str = "templates.json",
                 **kwargs):
        """
        初始化LLM编译器
        
        Args:
            template_storage_path: 模板存储路径
        """
        # 调用基类初始化
        super().__init__(template_storage_path=template_storage_path, **kwargs)
        
        self.stats = {
            'total_compilations': 0,
            'template_reuses': 0,
            'new_templates': 0
        }
    
    def compile(self, task: str) -> LayeredIR:
        """编译任务（仅使用LLM匹配）"""
        self.stats['total_compilations'] += 1
        
        # 获取所有模板摘要
        templates_summary = self.template_manager.get_templates_summary()
        
        # 使用LLM匹配
        if templates_summary:
            match_result = self.template_matcher.match(task, templates_summary)
            
            if match_result and match_result.can_reuse:
                # 获取匹配的模板
                matched_template = self.template_manager.get_template(match_result.template_id)
                
                print(f"\n✓ 找到匹配模板: {match_result.template_id}")
                print(f"  置信度: {match_result.confidence:.2f}")
                print(f"  原因: {match_result.reasoning}")
                
                # 应用模板
                code = self._apply_template(matched_template, match_result.extracted_parameters)
                
                # 更新使用统计
                self.template_manager.update_usage(match_result.template_id)
                self.stats['template_reuses'] += 1
                
                # 创建IR
                layer = Layer(
                    level=1,
                    name="模板执行",
                    description=task,
                    type=LayerType.COMPILED,
                    code=code,
                    metadata={
                        "template_id": match_result.template_id,
                        "parameters": match_result.extracted_parameters,
                        "reused": True
                    }
                )
                
                return LayeredIR(
                    task=task,
                    layers=[layer],
                    metadata={
                        "compiled": True,
                        "template_reused": True,
                        "template_id": match_result.template_id
                    }
                )
        
        # 没有找到匹配的模板，进行新编译
        print(f"\n→ 没有找到匹配的模板，进行新编译...")
        return self._compile_new_task(task)
    
    def _compile_new_task(self, task: str) -> LayeredIR:
        """编译新任务并添加到模板库"""
        compilation_result = self._compile_with_parameterization(task)
        
        # 如果可参数化，创建新模板
        if compilation_result.get('is_parameterizable'):
            template = self._create_template_from_compilation(task, compilation_result)
            self.template_manager.add_template(template)
            self.stats['new_templates'] += 1
            print(f"✓ 创建新模板: {template.id}")
        
        # 创建IR
        layer = Layer(
            level=1,
            name="新编译执行",
            description=task,
            type=LayerType.COMPILED,
            code=compilation_result['code'],
            metadata={
                "parameterizable": compilation_result.get('is_parameterizable', False)
            }
        )
        
        return LayeredIR(
            task=task,
            layers=[layer],
            metadata={
                "compiled": True,
                "template_reused": False,
                "new_template_created": compilation_result.get('is_parameterizable', False)
            }
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取编译统计信息"""
        stats = dict(self.stats)
        
        # 计算重用率
        if stats['total_compilations'] > 0:
            reuse_rate = stats['template_reuses'] / stats['total_compilations']
            stats['reuse_rate'] = f"{reuse_rate:.1%}"
        else:
            stats['reuse_rate'] = "0.0%"
        
        # 添加模板库信息
        stats['total_templates'] = len(self.template_manager.templates)
        
        return stats