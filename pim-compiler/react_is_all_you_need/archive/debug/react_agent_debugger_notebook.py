"""GenericReactAgent 调试器 - Jupyter Notebook 版本

支持在 Jupyter Notebook 中使用，包含使用 Gemini 2.5 Flash 的智能分析功能。
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
from datetime import datetime

# 导入基础调试器
from react_agent_debugger import (
    ReactAgentDebugger,
    StepType,
    StepBreakpoint,
    ToolBreakpoint,
    ConditionalBreakpoint,
    AgentBreakpoint,
    Breakpoint
)

# Gemini API
try:
    import google.generativeai as genai
except ImportError:
    print("请安装 google-generativeai: pip install google-generativeai")
    raise


class NotebookReactAgentDebugger(ReactAgentDebugger):
    """Jupyter Notebook 版本的调试器
    
    增加了 Notebook 特有的功能：
    1. 交互式 UI
    2. 使用 Gemini 2.5 Flash 的智能分析
    3. 异步执行支持
    """
    
    def __init__(self, agent, gemini_api_key: Optional[str] = None):
        """初始化 Notebook 调试器
        
        Args:
            agent: GenericReactAgent 实例
            gemini_api_key: Gemini API 密钥，如果不提供则从环境变量读取
        """
        super().__init__(agent)
        
        # 初始化 Gemini
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("请提供 Gemini API 密钥或设置 GEMINI_API_KEY 环境变量")
        
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Notebook 特有属性
        self.output_widget = widgets.Output()
        self.control_panel = None
        self.is_paused = False
        self.analysis_results = []
        
    def analysis(self) -> Dict[str, Any]:
        """使用 Gemini 2.5 Flash 分析当前状态是否有 bug
        
        Returns:
            包含分析结果的字典
        """
        if not self.current_state:
            return {"error": "没有可分析的状态"}
        
        # 准备分析上下文
        context = self._prepare_analysis_context()
        
        # 构建分析提示词
        prompt = self._build_analysis_prompt(context)
        
        try:
            # 调用 Gemini 进行分析
            response = self.gemini_model.generate_content(prompt)
            
            # 解析分析结果
            analysis_result = self._parse_analysis_response(response.text)
            
            # 保存分析历史
            analysis_result["timestamp"] = datetime.now().isoformat()
            analysis_result["context"] = context
            self.analysis_results.append(analysis_result)
            
            # 在 Notebook 中展示结果
            self._display_analysis_result(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            error_result = {
                "error": f"分析失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            self._display_analysis_result(error_result)
            return error_result
    
    def _prepare_analysis_context(self) -> Dict[str, Any]:
        """准备用于分析的上下文信息"""
        context = {
            "current_step": self.current_state.get("step_type", "Unknown"),
            "execution_history_length": len(self.execution_history),
            "current_depth": self.current_depth,
            "has_error_keywords": False,
            "last_message_preview": "",
            "recent_tools": [],
            "message_pattern": [],
            "potential_issues": []
        }
        
        # 分析最后的消息
        if "last_message" in self.current_state:
            last_msg = self.current_state["last_message"]
            msg_content = str(last_msg)
            context["last_message_preview"] = msg_content[:500]
            
            # 检查错误关键词
            error_keywords = ["error", "failed", "exception", "not found", "denied", "失败", "错误"]
            context["has_error_keywords"] = any(kw in msg_content.lower() for kw in error_keywords)
        
        # 分析最近的工具调用
        recent_steps = self.execution_history[-10:] if len(self.execution_history) > 10 else self.execution_history
        for step in recent_steps:
            if step.step_type == StepType.ACT and "tool_calls" in step.data:
                for tc in step.data.get("tool_calls", []):
                    context["recent_tools"].append(tc.get("name", "unknown"))
        
        # 分析消息模式
        if "messages" in self.current_state:
            messages = self.current_state["messages"]
            for msg in messages[-5:]:  # 最近5条消息
                msg_type = type(msg).__name__
                context["message_pattern"].append(msg_type)
        
        # 检查潜在问题
        # 1. 重复工具调用
        if context["recent_tools"]:
            tool_counts = {}
            for tool in context["recent_tools"]:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
            repeated_tools = [tool for tool, count in tool_counts.items() if count > 2]
            if repeated_tools:
                context["potential_issues"].append(f"重复调用工具: {repeated_tools}")
        
        # 2. 执行步骤过多
        if context["execution_history_length"] > 20:
            context["potential_issues"].append(f"执行步骤过多: {context['execution_history_length']} 步")
        
        # 3. 调用深度异常
        if context["current_depth"] > 3:
            context["potential_issues"].append(f"调用深度过深: {context['current_depth']} 层")
        
        return context
    
    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """构建分析提示词"""
        prompt = f"""你是一个专业的 AI Agent 调试专家。请分析以下执行状态，判断是否存在 bug 或潜在问题。

## 当前状态
- 步骤类型: {context['current_step']}
- 执行历史长度: {context['execution_history_length']} 步
- 当前调用深度: {context['current_depth']}
- 是否包含错误关键词: {context['has_error_keywords']}

## 最近的消息
{context['last_message_preview']}

## 最近使用的工具
{', '.join(context['recent_tools']) if context['recent_tools'] else '无'}

## 消息模式
{' -> '.join(context['message_pattern']) if context['message_pattern'] else '无'}

## 已识别的潜在问题
{chr(10).join(f"- {issue}" for issue in context['potential_issues']) if context['potential_issues'] else '无'}

请分析并回答：
1. 是否存在 bug？（是/否）
2. bug 的严重程度？（如果有）[严重/中等/轻微]
3. bug 的类型是什么？（如果有）
4. 具体问题描述
5. 建议的解决方案
6. 其他观察到的问题或优化建议

请用 JSON 格式回复，包含以下字段：
{{
    "has_bug": true/false,
    "severity": "严重/中等/轻微/无",
    "bug_type": "错误类型",
    "description": "问题描述",
    "solution": "解决方案",
    "additional_observations": ["观察1", "观察2"]
}}
"""
        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """解析 Gemini 的响应"""
        try:
            # 尝试提取 JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # 如果没有找到 JSON，返回原始文本
                result = {
                    "has_bug": "unknown",
                    "raw_response": response_text
                }
        except Exception as e:
            result = {
                "has_bug": "parse_error",
                "error": str(e),
                "raw_response": response_text
            }
        
        return result
    
    def _display_analysis_result(self, result: Dict[str, Any]):
        """在 Notebook 中展示分析结果"""
        with self.output_widget:
            clear_output(wait=True)
            
            # 创建 HTML 展示
            if "error" in result:
                html = f"""
                <div style="border: 2px solid #ff4444; padding: 15px; border-radius: 5px; background-color: #ffeeee;">
                    <h3 style="color: #ff0000;">❌ 分析失败</h3>
                    <p>{result['error']}</p>
                </div>
                """
            else:
                bug_color = "#ff4444" if result.get("has_bug") else "#44ff44"
                bug_status = "🐛 发现 Bug" if result.get("has_bug") else "✅ 未发现 Bug"
                
                html = f"""
                <div style="border: 2px solid {bug_color}; padding: 15px; border-radius: 5px;">
                    <h3>{bug_status}</h3>
                    <p><strong>时间:</strong> {result.get('timestamp', 'N/A')}</p>
                """
                
                if result.get("has_bug"):
                    severity_colors = {
                        "严重": "#ff0000",
                        "中等": "#ff8800",
                        "轻微": "#ffaa00"
                    }
                    severity = result.get("severity", "未知")
                    severity_color = severity_colors.get(severity, "#888888")
                    
                    html += f"""
                    <p><strong>严重程度:</strong> <span style="color: {severity_color};">{severity}</span></p>
                    <p><strong>Bug 类型:</strong> {result.get('bug_type', 'N/A')}</p>
                    <p><strong>描述:</strong> {result.get('description', 'N/A')}</p>
                    <p><strong>解决方案:</strong> {result.get('solution', 'N/A')}</p>
                    """
                
                if result.get("additional_observations"):
                    html += "<p><strong>其他观察:</strong></p><ul>"
                    for obs in result["additional_observations"]:
                        html += f"<li>{obs}</li>"
                    html += "</ul>"
                
                html += "</div>"
            
            display(HTML(html))
    
    def create_control_panel(self):
        """创建交互式控制面板"""
        # 控制按钮
        continue_btn = widgets.Button(description="继续 (c)", button_style='success')
        step_btn = widgets.Button(description="单步 (s)", button_style='primary')
        step_in_btn = widgets.Button(description="步入 (si)", button_style='info')
        step_out_btn = widgets.Button(description="步出 (so)", button_style='info')
        step_over_btn = widgets.Button(description="步过 (sv)", button_style='info')
        analysis_btn = widgets.Button(description="分析 🔍", button_style='warning')
        quit_btn = widgets.Button(description="退出 (q)", button_style='danger')
        
        # 信息显示
        status_label = widgets.Label(value="状态: 运行中")
        
        # 按钮事件处理
        def on_continue(b):
            self.step_mode = StepMode.RUN
            self.is_paused = False
            status_label.value = "状态: 运行中"
        
        def on_step(b):
            self.step_mode = StepMode.STEP
            self.is_paused = False
            status_label.value = "状态: 单步执行"
        
        def on_step_in(b):
            self.step_mode = StepMode.STEP_IN
            self.is_paused = False
            status_label.value = "状态: 步入"
        
        def on_step_out(b):
            self.step_mode = StepMode.STEP_OUT
            self.is_paused = False
            status_label.value = "状态: 步出"
        
        def on_step_over(b):
            self.step_mode = StepMode.STEP_OVER
            self.is_paused = False
            status_label.value = "状态: 步过"
        
        def on_analysis(b):
            with self.output_widget:
                print("\n🔍 正在分析当前状态...")
            self.analysis()
        
        def on_quit(b):
            self.continue_execution = False
            self.is_paused = False
            status_label.value = "状态: 已退出"
        
        # 绑定事件
        continue_btn.on_click(on_continue)
        step_btn.on_click(on_step)
        step_in_btn.on_click(on_step_in)
        step_out_btn.on_click(on_step_out)
        step_over_btn.on_click(on_step_over)
        analysis_btn.on_click(on_analysis)
        quit_btn.on_click(on_quit)
        
        # 布局
        button_box = widgets.HBox([
            continue_btn, step_btn, step_in_btn, step_out_btn, step_over_btn, 
            analysis_btn, quit_btn
        ])
        
        control_panel = widgets.VBox([
            status_label,
            button_box,
            self.output_widget
        ])
        
        self.control_panel = control_panel
        return control_panel
    
    def _handle_debug_command(self) -> bool:
        """Notebook 版本的命令处理 - 使用交互式 UI"""
        self.is_paused = True
        
        # 等待用户通过 UI 操作
        while self.is_paused and self.continue_execution:
            asyncio.sleep(0.1)
        
        return self.continue_execution
    
    def execute_task_async(self, task: str):
        """异步执行任务（适合 Jupyter Notebook）"""
        # 创建事件循环任务
        async def run():
            self.execute_task(task)
        
        # 在 notebook 中运行
        return asyncio.create_task(run())


def create_notebook_debugger(agent, gemini_api_key: Optional[str] = None) -> NotebookReactAgentDebugger:
    """创建 Notebook 调试器的便捷函数
    
    Args:
        agent: GenericReactAgent 实例
        gemini_api_key: Gemini API 密钥
        
    Returns:
        配置好的 NotebookReactAgentDebugger 实例
    """
    debugger = NotebookReactAgentDebugger(agent, gemini_api_key)
    
    # 添加一些默认断点
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            "error_detector",
            lambda ctx: "error" in str(ctx.get("last_message", "")).lower(),
            "检测到错误"
        )
    )
    
    return debugger