"""
分层执行器

按层次执行编译的代码和ReAct任务。
优化LLM调用，最大化编译代码的执行。
"""

import time
from typing import Dict, Any, List, Optional, Callable
from .ir_types import (
    LayeredIR, Layer, LayerType, 
    ExecutionResult, LayeredExecutionResult
)


class HierarchicalExecutor:
    """分层执行器"""
    
    def __init__(self,
                 python_executor: Optional[Callable] = None,
                 react_agent: Optional[Any] = None):
        """
        Args:
            python_executor: Python代码执行器
            react_agent: ReAct代理（用于探索性任务）
        """
        self.python_executor = python_executor or self._default_python_executor
        self.react_agent = react_agent
        self.execution_cache = {}
        
    def execute(self, ir: LayeredIR) -> LayeredExecutionResult:
        """执行分层IR"""
        start_time = time.time()
        results = []
        context = {}
        llm_calls = 0
        
        print(f"\n执行任务: {ir.task}")
        print(f"总层数: {len(ir.layers)}, 编译层: {len(ir.get_compiled_layers())}")
        print("-" * 50)
        
        for layer in ir.layers:
            print(f"\n执行第{layer.level}层: {layer.name}")
            
            if layer.type == LayerType.COMPILED:
                # 执行编译的代码
                result = self._execute_compiled_layer(layer, context)
                results.append(result)
                
                if result.success:
                    print(f"✓ 编译层执行成功")
                else:
                    print(f"✗ 编译层执行失败: {result.error}")
                    break
                    
            elif layer.type == LayerType.REACT:
                # 执行ReAct任务
                if not self.react_agent:
                    print("! 需要ReAct代理来执行探索性任务")
                    result = ExecutionResult(
                        level=layer.level,
                        type=layer.type,
                        success=False,
                        output=None,
                        context=context,
                        error="ReAct代理未配置"
                    )
                else:
                    result = self._execute_react_layer(layer, context)
                    llm_calls += result.context.get('llm_calls', 1)
                    
                results.append(result)
                
                if not result.success:
                    print(f"✗ ReAct层执行失败: {result.error}")
                    break
                else:
                    print(f"✓ ReAct层执行成功 (LLM调用: {result.context.get('llm_calls', 1)}次)")
            
            # 更新上下文
            context.update(result.context)
        
        # 汇总结果
        final_output = self._aggregate_results(results)
        
        execution_result = LayeredExecutionResult(
            task=ir.task,
            results=results,
            final_output=final_output,
            total_llm_calls=llm_calls,
            execution_time=time.time() - start_time
        )
        
        # 打印执行摘要
        self._print_execution_summary(execution_result)
        
        return execution_result
    
    def _execute_compiled_layer(self, layer: Layer, context: Dict[str, Any]) -> ExecutionResult:
        """执行编译层"""
        try:
            # 准备执行环境
            import os
            import json
            import csv
            from collections import defaultdict
            exec_globals = {
                '__builtins__': __builtins__,
                'context': context,
                'layer': layer,
                'os': os,
                'json': json,
                'csv': csv,
                'defaultdict': defaultdict
            }
            exec_locals = {}
            
            # 执行Python代码
            exec(layer.code, exec_globals, exec_locals)
            
            # 提取结果
            output = exec_locals.get('result', exec_locals)
            
            # 更新上下文
            new_context = exec_locals.get('next_context', {})
            if 'result' in exec_locals:
                new_context['layer_' + str(layer.level) + '_result'] = output
            
            return ExecutionResult(
                level=layer.level,
                type=layer.type,
                success=True,
                output=output,
                context=new_context
            )
            
        except Exception as e:
            return ExecutionResult(
                level=layer.level,
                type=layer.type,
                success=False,
                output=None,
                context=context,
                error=str(e)
            )
    
    def _execute_react_layer(self, layer: Layer, context: Dict[str, Any]) -> ExecutionResult:
        """执行ReAct层"""
        try:
            # 构建增强的任务描述
            enhanced_task = self._build_enhanced_task(layer, context)
            
            # 模拟ReAct执行（实际应调用react_agent）
            if self.react_agent:
                # 使用真实的ReAct代理
                result = self.react_agent.execute_task(enhanced_task)
                output = result.output if hasattr(result, 'output') else result
                llm_calls = getattr(result, 'llm_calls', 1)
            else:
                # 模拟执行
                output = f"ReAct执行结果: {layer.task}"
                llm_calls = 1
            
            return ExecutionResult(
                level=layer.level,
                type=layer.type,
                success=True,
                output=output,
                context={
                    'llm_calls': llm_calls,
                    f'layer_{layer.level}_output': output
                }
            )
            
        except Exception as e:
            return ExecutionResult(
                level=layer.level,
                type=layer.type,
                success=False,
                output=None,
                context=context,
                error=str(e)
            )
    
    def _build_enhanced_task(self, layer: Layer, context: Dict[str, Any]) -> str:
        """构建增强的任务描述"""
        enhanced = f"{layer.task}\n\n"
        
        if context:
            enhanced += "基于以下上下文信息：\n"
            for key, value in context.items():
                if not key.startswith('_'):  # 跳过内部变量
                    enhanced += f"- {key}: {str(value)[:100]}...\n"
        
        return enhanced
    
    def _aggregate_results(self, results: List[ExecutionResult]) -> Any:
        """聚合各层结果"""
        if not results:
            return None
        
        # 返回最后一个成功的结果
        for result in reversed(results):
            if result.success and result.output is not None:
                return result.output
        
        return None
    
    def _print_execution_summary(self, result: LayeredExecutionResult):
        """打印执行摘要"""
        print("\n" + "=" * 50)
        print("执行摘要:")
        print(f"- 总执行时间: {result.execution_time:.2f}秒")
        print(f"- LLM调用次数: {result.total_llm_calls}")
        print(f"- 执行成功: {'是' if result.is_success() else '否'}")
        
        if result.final_output:
            print(f"- 最终输出: {str(result.final_output)[:100]}...")
    
    def _default_python_executor(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """默认的Python执行器"""
        exec_globals = {'__builtins__': __builtins__, 'context': context}
        exec_locals = {}
        exec(code, exec_globals, exec_locals)
        return exec_locals
    
    def analyze_execution_efficiency(self, ir: LayeredIR) -> Dict[str, Any]:
        """分析执行效率"""
        compiled_layers = len(ir.get_compiled_layers())
        total_layers = len(ir.layers)
        
        # 估算节省的LLM调用
        saved_llm_calls = compiled_layers
        estimated_llm_calls = total_layers - compiled_layers
        
        # 估算性能提升
        # 假设LLM调用平均需要2秒，编译代码执行需要0.1秒
        estimated_time_with_llm = total_layers * 2.0
        estimated_time_with_compilation = compiled_layers * 0.1 + (total_layers - compiled_layers) * 2.0
        
        speedup = estimated_time_with_llm / estimated_time_with_compilation if estimated_time_with_compilation > 0 else 1
        
        return {
            'total_layers': total_layers,
            'compiled_layers': compiled_layers,
            'compilation_ratio': compiled_layers / total_layers if total_layers > 0 else 0,
            'saved_llm_calls': saved_llm_calls,
            'estimated_speedup': f"{speedup:.1f}x",
            'estimated_time_saved': f"{estimated_time_with_llm - estimated_time_with_compilation:.1f}秒"
        }