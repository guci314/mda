#!/usr/bin/env python3
"""
增强版 PIM Compiler Chatbot - 带命令历史和自动补全
"""

import os
import sys
from pathlib import Path
from typing import List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from pim_compiler_chatbot.chatbot import create_pim_compiler_agent, PIMCompilerTools


class CommandCompleter:
    """命令自动补全器"""
    
    def __init__(self, tools: PIMCompilerTools):
        self.tools = tools
        
        # 常用命令模板
        self.commands = [
            "编译",
            "编译医院系统",
            "编译博客系统", 
            "编译用户管理系统",
            "编译图书管理系统",
            "查看日志",
            "查看博客系统日志",
            "查看医院系统日志",
            "列出所有项目",
            "列出项目",
            "搜索",
            "搜索医院",
            "搜索博客",
            "搜索用户",
            "清理",
            "清理博客系统",
            "清理医院系统",
            "帮助",
            "exit",
            "quit"
        ]
        
        # 动态添加已知的 PIM 文件
        self.update_file_list()
    
    def update_file_list(self):
        """更新可用的 PIM 文件列表"""
        try:
            examples_dir = self.tools.examples_dir
            if examples_dir.exists():
                for file in examples_dir.glob("*.md"):
                    name = file.stem.replace('_', ' ')
                    self.commands.append(f"编译{name}")
                    self.commands.append(f"搜索{name}")
        except:
            pass
    
    def complete(self, text, state):
        """readline 补全函数"""
        # 获取匹配的命令
        matches = [cmd for cmd in self.commands if cmd.startswith(text)]
        
        # 如果输入包含路径分隔符，尝试文件补全
        if '/' in text:
            # 文件路径补全
            dir_path = os.path.dirname(text)
            base_name = os.path.basename(text)
            
            try:
                if not dir_path:
                    dir_path = '.'
                
                for item in os.listdir(dir_path):
                    if item.startswith(base_name):
                        full_path = os.path.join(dir_path, item)
                        if os.path.isdir(full_path):
                            matches.append(full_path + '/')
                        else:
                            matches.append(full_path)
            except:
                pass
        
        # 返回第 state 个匹配项
        if state < len(matches):
            return matches[state]
        return None


def setup_readline(tools: PIMCompilerTools):
    """设置 readline 以支持历史和自动补全"""
    try:
        import readline
        
        # 设置历史文件
        history_file = Path.home() / ".pim_compiler_chatbot_history"
        
        # 加载历史记录
        if history_file.exists():
            readline.read_history_file(str(history_file))
        
        # 设置历史记录大小
        readline.set_history_length(1000)
        
        # 设置自动补全
        completer = CommandCompleter(tools)
        readline.set_completer(completer.complete)
        readline.parse_and_bind("tab: complete")
        
        # 设置分隔符（用于路径补全）
        readline.set_completer_delims(' \t\n;')
        
        print("✅ 已启用命令历史和自动补全（按 Tab 键）")
        
        return readline, history_file
        
    except ImportError:
        print("⚠️  readline 模块不可用，命令历史和自动补全功能已禁用")
        return None, None


def print_help():
    """打印帮助信息"""
    help_text = """
📚 PIM 编译器助手使用指南

基本命令：
  编译<系统名>      - 编译指定的系统（如：编译博客系统）
  查看日志         - 查看最近的编译日志
  查看<系统名>日志  - 查看特定系统的编译日志
  列出所有项目     - 显示所有已编译的项目
  搜索<关键词>     - 搜索 PIM 文件
  清理<项目名>     - 清理编译输出
  帮助            - 显示此帮助信息
  exit/quit       - 退出程序

快捷键：
  ↑/↓            - 浏览命令历史
  Tab            - 自动补全命令
  Ctrl+C         - 取消当前输入
  Ctrl+D         - 退出程序

示例：
  编译博客系统
  查看日志
  搜索医院
  清理blog

提示：
  - 输入命令的前几个字符后按 Tab 键可以自动补全
  - 系统会记住您的命令历史，下次启动时可以继续使用
"""
    print(help_text)


def main():
    """主函数"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # 确保在正确的目录下运行
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # 初始化工具
    tools = PIMCompilerTools()
    
    # 设置 readline
    readline_module, history_file = setup_readline(tools)
    
    print("🤖 PIM 编译器助手（增强版）")
    print("=" * 60)
    print("输入 '帮助' 查看使用指南，'exit' 退出")
    print()
    
    # 检查 API key
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        llm_config = {
            "api_key": deepseek_key,
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "temperature": 0.3
        }
        print("✅ 使用 DeepSeek 模型")
    else:
        print("⚠️  未设置 DEEPSEEK_API_KEY，使用简化模式")
        llm_config = None
    
    # 创建 agent
    agent = create_pim_compiler_agent(llm_config) if llm_config else None
    
    # 交互循环
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye', '退出']:
                print("\n👋 再见！")
                break
            
            if user_input.lower() in ['help', '帮助', '?']:
                print_help()
                continue
            
            if not user_input:
                continue
            
            # 处理命令
            if agent:
                result = agent.invoke({"input": user_input})
                print(f"\n助手: {result['output']}")
            else:
                # 简化模式 - 直接调用工具
                print("\n助手: 正在处理您的请求...")
                if "编译" in user_input:
                    print("请设置 DEEPSEEK_API_KEY 以使用完整功能")
                elif "查看日志" in user_input:
                    print(tools.check_log())
                elif "列出" in user_input:
                    print(tools.list_compiled_projects())
                else:
                    print("简化模式下功能有限，请设置 DEEPSEEK_API_KEY")
            
        except KeyboardInterrupt:
            print("\n（使用 'exit' 退出）")
            continue
        except EOFError:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 出错了: {str(e)}")
    
    # 保存历史记录
    if readline_module and history_file:
        try:
            readline_module.write_history_file(str(history_file))
            print(f"✅ 命令历史已保存到 {history_file}")
        except:
            pass


if __name__ == "__main__":
    main()