#!/usr/bin/env python3
"""
PIM Compiler Chatbot with Gradio UI

提供 Web 界面的智能编译助手
"""

import gradio as gr
import os
import sys
from pathlib import Path
from typing import List, Tuple
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from pim_compiler_chatbot.chatbot import create_pim_compiler_agent, PIMCompilerTools


class ChatbotUI:
    """聊天机器人 UI"""
    
    def __init__(self):
        self.agent = None
        self.tools = PIMCompilerTools()
        self.chat_history = []
        self.setup_agent()
        
    def setup_agent(self):
        """设置智能体"""
        # 尝试配置 LLM
        llm_config = None
        
        if not os.getenv("OPENAI_API_KEY"):
            deepseek_key = os.getenv("DEEPSEEK_API_KEY")
            if deepseek_key:
                llm_config = {
                    "api_key": deepseek_key,
                    "base_url": "https://api.deepseek.com/v1",
                    "model": "deepseek-chat",
                    "temperature": 0.3
                }
                self.llm_info = "使用 DeepSeek 模型: deepseek-chat"
            else:
                self.llm_info = "⚠️ 未配置 LLM（需要设置 DEEPSEEK_API_KEY），部分功能不可用"
        else:
            self.llm_info = "使用 OpenAI 模型"
            
        try:
            self.agent = create_pim_compiler_agent(llm_config)
        except Exception as e:
            self.llm_info = f"❌ 无法创建智能体: {str(e)}"
            
    def chat(self, message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
        """处理聊天消息"""
        if not message:
            return history, ""
            
        # 添加用户消息到历史
        history = history + [(message, None)]
        
        try:
            if self.agent:
                # 使用智能体处理
                result = self.agent.invoke({"input": message})
                response = result['output']
            else:
                # 直接使用工具（降级模式）
                response = self.handle_direct_command(message)
                
            # 更新历史
            history[-1] = (message, response)
            
        except Exception as e:
            response = f"❌ 出错了: {str(e)}"
            history[-1] = (message, response)
            
        return history, ""
    
    def handle_direct_command(self, message: str) -> str:
        """直接处理命令（无 LLM 模式）"""
        message_lower = message.lower()
        
        if "编译" in message:
            # 尝试提取文件名
            if "医院" in message or "hospital" in message:
                search_result = self.tools.search_pim_files("hospital")
                return f"搜索结果:\n{search_result}\n\n请使用完整路径编译，如: compile examples/smart_hospital_system.md"
            else:
                return "请指定要编译的系统名称或文件路径"
                
        elif "日志" in message or "log" in message_lower:
            return self.tools.check_log()
            
        elif "列出" in message or "list" in message_lower:
            return self.tools.list_compiled_projects()
            
        elif "搜索" in message or "search" in message_lower:
            # 提取搜索词
            words = message.split()
            if len(words) > 1:
                query = words[-1]
                return self.tools.search_pim_files(query)
            else:
                return "请提供搜索关键词"
                
        else:
            return "支持的命令: 搜索<关键词>、编译<系统>、查看日志、列出项目"
    
    def quick_search(self, query: str) -> str:
        """快速搜索"""
        if not query:
            return "请输入搜索关键词"
        return self.tools.search_pim_files(query)
    
    def quick_compile(self, file_path: str) -> str:
        """快速编译"""
        if not file_path:
            return "请输入文件路径"
        return self.tools.compile_pim(file_path)
    
    def view_log(self, system_name: str) -> str:
        """查看日志"""
        return self.tools.check_log(system_name if system_name else None)
    
    def list_projects(self) -> str:
        """列出项目"""
        return self.tools.list_compiled_projects()


def create_ui():
    """创建 Gradio UI"""
    ui = ChatbotUI()
    
    with gr.Blocks(title="PIM Compiler Chatbot", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🤖 PIM 编译器智能助手
        
        基于 LangChain ReAct Agent 的智能编译助手，帮助你管理 PIM 文件的编译过程。
        """)
        
        # 显示 LLM 信息
        gr.Markdown(f"**模型状态**: {ui.llm_info}")
        
        with gr.Tab("💬 智能对话"):
            chatbot = gr.Chatbot(
                value=[],
                height=400,
                show_label=False,
                elem_id="chatbot"
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="输入消息",
                    placeholder='试试: "编译医院系统" 或 "查看日志"',
                    lines=1,
                    scale=9
                )
                submit = gr.Button("发送", variant="primary", scale=1)
            
            # 快捷命令
            gr.Examples(
                examples=[
                    "列出所有可用的 PIM 文件",
                    "编译医院系统",
                    "查看日志",
                    "列出已编译的项目"
                ],
                inputs=msg
            )
            
            # 事件处理
            msg.submit(ui.chat, [msg, chatbot], [chatbot, msg])
            submit.click(ui.chat, [msg, chatbot], [chatbot, msg])
        
        with gr.Tab("🔧 快捷工具"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🔍 搜索 PIM 文件")
                    search_input = gr.Textbox(
                        label="搜索关键词",
                        placeholder="如: hospital, 医院, smart"
                    )
                    search_btn = gr.Button("搜索", variant="primary")
                    search_output = gr.Textbox(
                        label="搜索结果",
                        lines=10,
                        max_lines=20
                    )
                    search_btn.click(ui.quick_search, search_input, search_output)
                    
                with gr.Column():
                    gr.Markdown("### 🚀 编译 PIM 文件")
                    compile_input = gr.Textbox(
                        label="文件路径",
                        placeholder="如: examples/smart_hospital_system.md"
                    )
                    compile_btn = gr.Button("开始编译", variant="primary")
                    compile_output = gr.Textbox(
                        label="编译状态",
                        lines=10,
                        max_lines=20
                    )
                    compile_btn.click(ui.quick_compile, compile_input, compile_output)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📊 查看编译日志")
                    log_input = gr.Textbox(
                        label="系统名称（可选）",
                        placeholder="留空显示所有活动任务"
                    )
                    log_btn = gr.Button("查看日志", variant="primary")
                    log_output = gr.Textbox(
                        label="日志内容",
                        lines=15,
                        max_lines=30
                    )
                    log_btn.click(ui.view_log, log_input, log_output)
                    
                with gr.Column():
                    gr.Markdown("### 📁 项目管理")
                    list_btn = gr.Button("列出所有项目", variant="primary")
                    list_output = gr.Textbox(
                        label="项目列表",
                        lines=15,
                        max_lines=30
                    )
                    list_btn.click(ui.list_projects, [], list_output)
        
        with gr.Tab("📖 使用说明"):
            gr.Markdown("""
            ## 使用指南
            
            ### 智能对话模式
            
            在对话框中输入自然语言指令，助手会自动理解并执行：
            
            - **编译系统**: "编译医院系统" → 自动搜索相关文件并编译
            - **查看进度**: "查看日志" → 显示编译进度和日志
            - **项目管理**: "列出所有项目" → 显示已编译的项目
            
            ### 快捷工具模式
            
            直接使用各个工具完成特定任务：
            
            1. **搜索文件**: 输入关键词搜索 PIM 文件
            2. **编译文件**: 输入完整路径启动编译
            3. **查看日志**: 查看编译日志和进度
            4. **项目列表**: 管理已编译的项目
            
            ### 注意事项
            
            - 编译是后台进程，启动后可以继续其他操作
            - 日志会实时更新，可以多次查看了解进度
            - 编译输出保存在 `compiled_output` 目录
            """)
    
    return demo


def main():
    """主函数"""
    # 设置工作目录
    os.chdir(Path(__file__).parent.parent)
    
    # 创建并启动 UI
    demo = create_ui()
    
    print("🚀 启动 PIM Compiler Chatbot UI...")
    print("📍 访问地址: http://127.0.0.1:7860")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # 设为 True 可以生成公共链接
        inbrowser=True  # 自动打开浏览器
    )


if __name__ == "__main__":
    main()