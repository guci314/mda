"""
模板感知的编译器

支持模板重用的自然语言编译器。
"""

import os
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from .llm_compiler import LLMCompiler
from .template_manager import TemplateManager, TaskTemplate, Parameter
from .llm_template_matcher import LLMTemplateMatcher
from .ir_types import LayeredIR, Layer, LayerType


class TemplateAwareCompiler(LLMCompiler):
    """支持模板重用的编译器"""
    
    def __init__(self,
                 template_storage_path: str = "templates.json",
                 **kwargs):
        """初始化模板感知编译器"""
        super().__init__(**kwargs)
        
        # 初始化组件
        self.template_manager = TemplateManager(template_storage_path)
        self.template_matcher = LLMTemplateMatcher(
            llm_model=kwargs.get('llm_model', "gemini-2.0-flash-exp"),
            llm_base_url=kwargs.get('llm_base_url', "https://generativelanguage.googleapis.com/v1beta/openai/"),
            llm_api_key_env=kwargs.get('llm_api_key_env', "GEMINI_API_KEY"),
            use_proxy=kwargs.get('use_proxy', True)
        )
        
        self.stats = {
            'total_compilations': 0,
            'template_reuses': 0,
            'new_templates': 0
        }
    
    def compile(self, task: str) -> LayeredIR:
        """编译任务（支持模板重用）"""
        self.stats['total_compilations'] += 1
        
        # 1. 获取相关模板
        templates_summary = self.template_manager.get_templates_summary()
        
        # 2. 尝试匹配模板
        if templates_summary:
            match_result = self.template_matcher.match(task, templates_summary)
            
            if match_result.can_reuse:
                # 3a. 重用模板
                print(f"\n✓ 找到匹配模板: {match_result.template_id}")
                print(f"  置信度: {match_result.confidence:.2f}")
                print(f"  原因: {match_result.reasoning}")
                
                template = self.template_manager.get_template(match_result.template_id)
                code = self._apply_template(template, match_result.extracted_parameters)
                
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
        
        # 3b. 没有匹配的模板，进行参数化编译
        print("\n→ 没有找到匹配的模板，进行新编译...")
        compilation_result = self._compile_with_parameterization(task)
        
        # 4. 如果可参数化，创建新模板
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
    
    def _compile_with_parameterization(self, task: str) -> Dict[str, Any]:
        """参数化编译"""
        prompt = f"""编译任务为Python代码，并识别可参数化的部分。

任务：{task}

要求：
1. 生成完整可执行的Python代码
2. 识别任务中的可变参数（数值、名称、条件等）
3. 将代码写成参数化函数
4. 使用标准库，避免外部依赖
5. 将结果存储在result变量中

输出JSON格式：
{{
    "code": "def task_function(param1, param2, ...):\\n    # 参数化的实现\\n    ...\\n\\n# 调用示例\\nresult = task_function(...)",
    "template_pattern": "任务的通用模式，用{{参数名}}表示参数",
    "parameters": [
        {{"name": "参数名", "type": "类型", "value": "本次的值", "description": "参数说明"}}
    ],
    "is_parameterizable": true/false,
    "examples": ["使用示例1", "使用示例2"]
}}

只输出JSON，不要有其他内容。"""
        
        try:
            from langchain.schema import SystemMessage, HumanMessage
            response = self.llm.invoke([
                SystemMessage(content="你是一个参数化代码生成器。"),
                HumanMessage(content=prompt)
            ])
            
            # 解析响应
            content = response.content.strip()
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            result = json.loads(content)
            
            # 如果不可参数化，返回简单代码
            if not result.get('is_parameterizable'):
                return {
                    'code': result.get('code', '# 无法生成代码'),
                    'is_parameterizable': False
                }
            
            return result
            
        except Exception as e:
            print(f"参数化编译失败: {e}")
            # 降级到普通编译
            code = self.compile_task(task)
            return {
                'code': code or '# 编译失败',
                'is_parameterizable': False
            }
    
    def _apply_template(self, template: TaskTemplate, parameters: Dict[str, Any]) -> str:
        """应用模板生成代码"""
        # 生成参数字符串
        param_str = ", ".join(f"{k}={repr(v)}" for k, v in parameters.items())
        
        # 生成调用代码
        code = f"""# 使用模板: {template.pattern}
# 参数: {parameters}

{template.compiled_function}

# 执行
result = task_function({param_str})
"""
        return code
    
    def _create_template_from_compilation(self, task: str, compilation: Dict[str, Any]) -> TaskTemplate:
        """从编译结果创建模板"""
        # 解析参数
        parameters = []
        for param_data in compilation.get('parameters', []):
            param = Parameter(
                name=param_data['name'],
                type=param_data.get('type', 'string'),
                description=param_data.get('description', ''),
                extraction_hints=param_data.get('hints', [])
            )
            parameters.append(param)
        
        # 创建模板
        template = TaskTemplate(
            id=self.template_manager.generate_template_id(compilation['template_pattern']),
            pattern=compilation['template_pattern'],
            parameters=parameters,
            compiled_function=compilation['code'],
            examples=[task] + compilation.get('examples', []),
            created_at=datetime.now().isoformat()
        )
        
        return template
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        reuse_rate = (
            self.stats['template_reuses'] / self.stats['total_compilations']
            if self.stats['total_compilations'] > 0 else 0
        )
        
        return {
            'total_compilations': self.stats['total_compilations'],
            'template_reuses': self.stats['template_reuses'],
            'new_templates': self.stats['new_templates'],
            'total_templates': len(self.template_manager.templates),
            'reuse_rate': f"{reuse_rate:.1%}"
        }