"""
基于LLM的自然语言编译器

使用连接主义方法，通过LLM理解任务语义并生成代码。
"""

import os
import json
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from .ir_types import LayeredIR, Layer, LayerType


class LLMCompiler:
    """基于LLM的编译器"""
    
    def __init__(self, 
                 llm_model: str = "gemini-2.0-flash-exp",
                 llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
                 llm_api_key_env: str = "GEMINI_API_KEY",
                 temperature: float = 0,
                 use_proxy: bool = True):
        """初始化LLM编译器"""
        # 配置httpx客户端（如果需要代理）
        http_client = None
        if use_proxy:
            try:
                import httpx
                http_client = httpx.Client(
                    proxy='socks5://127.0.0.1:7890',
                    timeout=30,
                    verify=False
                )
            except ImportError:
                print("警告: httpx未安装，无法使用代理")
        
        self.llm = ChatOpenAI(
            model=llm_model,
            base_url=llm_base_url,
            api_key=os.getenv(llm_api_key_env),
            temperature=temperature,
            http_client=http_client
        )
        
    def analyze_compilability(self, task: str) -> Dict[str, Any]:
        """使用LLM分析任务的可编译性"""
        
        system_prompt = """你是一个自然语言编译器分析器。
        
分析给定任务的可编译性，判断其决策树大小。

只输出JSON，不要有其他内容。输出格式：
{
    "decision_tree_size": 100,
    "compilable": true,
    "reasoning": "任务有确定的输入输出映射",
    "confidence": 0.95
}

判断标准：
- 如果任务有确定的输入输出映射，且状态空间有限（<10000），则可编译
- 如果任务需要探索未知状态空间，或涉及创造性工作，则不可编译
- 数据处理、统计、格式转换等任务通常可编译（decision_tree_size: 10-1000）
- 调试、设计、创作等任务通常不可编译（decision_tree_size: 1000000+）
"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"分析任务：{task}")
            ])
            
            # 解析LLM响应
            content = response.content.strip()
            # 尝试提取JSON部分
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(content)
            return analysis
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {response.content if 'response' in locals() else 'No response'}")
            # 如果解析失败，返回默认值
            return {
                "decision_tree_size": 100000,
                "compilable": False,
                "reasoning": "JSON解析失败",
                "confidence": 0.5
            }
        except Exception as e:
            print(f"LLM调用错误: {e}")
            return {
                "decision_tree_size": 100000,
                "compilable": False,
                "reasoning": f"LLM调用失败: {str(e)}",
                "confidence": 0.5
            }
    
    def compile_task(self, task: str) -> Optional[str]:
        """使用LLM将任务编译为Python代码"""
        
        system_prompt = """你是一个自然语言到Python代码的编译器。

将用户的任务描述编译为可执行的Python代码。

要求：
1. 生成完整的、可直接执行的Python代码
2. 包含必要的import语句
3. 将最终结果存储在名为'result'的变量中
4. 处理可能的异常情况
5. 只生成代码，不要解释
6. 如果代码中有代码块标记(```)，不要包含它们

如果任务不适合编译（需要人工判断或创造性工作），只返回单词: None
"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"编译任务：{task}")
            ])
            
            code = response.content.strip()
            
            # 去除代码块标记
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()
            
            # 如果LLM返回None或表示无法编译
            if code.lower() == "none" or "无法编译" in code:
                return None
                
            return code
        except Exception as e:
            print(f"代码生成错误: {e}")
            return None
    
    def compile(self, task: str) -> LayeredIR:
        """完整的编译流程"""
        # 1. 分析可编译性
        analysis = self.analyze_compilability(task)
        
        # 2. 如果可编译，生成代码
        if analysis["compilable"]:
            code = self.compile_task(task)
            if code:
                layer = Layer(
                    level=1,
                    name="编译执行",
                    description=task,
                    type=LayerType.COMPILED,
                    code=code,
                    metadata={
                        "tree_size": analysis["decision_tree_size"],
                        "confidence": analysis["confidence"],
                        "reasoning": analysis["reasoning"]
                    }
                )
            else:
                layer = Layer(
                    level=1,
                    name="探索执行",
                    description=task,
                    type=LayerType.REACT,
                    task=task,
                    metadata={
                        "tree_size": analysis["decision_tree_size"],
                        "reasoning": "代码生成失败，需要探索执行"
                    }
                )
        else:
            # 不可编译，使用ReAct
            layer = Layer(
                level=1,
                name="探索执行",
                description=task,
                type=LayerType.REACT,
                task=task,
                metadata={
                    "tree_size": analysis["decision_tree_size"],
                    "reasoning": analysis["reasoning"]
                }
            )
        
        return LayeredIR(
            task=task,
            layers=[layer],
            metadata={
                "compilation_analysis": analysis,
                "compiled": analysis["compilable"] and code is not None
            }
        )