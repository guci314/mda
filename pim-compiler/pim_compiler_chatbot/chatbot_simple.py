#!/usr/bin/env python3
"""
PIM Compiler Chatbot - 简化版（无需 LLM）

直接使用工具的命令行界面
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from pim_compiler_chatbot.chatbot import PIMCompilerTools


class SimpleChatbot:
    """简化版聊天机器人"""
    
    def __init__(self):
        self.tools = PIMCompilerTools()
        self.commands = {
            "搜索": self.search_command,
            "search": self.search_command,
            "编译": self.compile_command,
            "compile": self.compile_command,
            "日志": self.log_command,
            "log": self.log_command,
            "列出": self.list_command,
            "list": self.list_command,
            "清理": self.clean_command,
            "clean": self.clean_command,
            "帮助": self.help_command,
            "help": self.help_command,
        }
        
    def search_command(self, args):
        """搜索命令"""
        if not args:
            return "请提供搜索关键词，例如: 搜索 医院"
        query = " ".join(args)
        return self.tools.search_pim_files(query)
    
    def compile_command(self, args):
        """编译命令"""
        if not args:
            # 如果没有参数，尝试智能推测
            return self.smart_compile(None)
        
        # 检查是否是系统名称（如"医院系统"）
        system_name = " ".join(args)
        if any(keyword in system_name for keyword in ["医院", "hospital", "图书", "library", "订单", "order"]):
            return self.smart_compile(system_name)
        
        # 否则当作文件路径
        file_path = args[0]
        return self.tools.compile_pim(file_path)
    
    def smart_compile(self, system_name):
        """智能编译 - 自动搜索并编译"""
        if not system_name:
            return "请指定要编译的系统，例如: 编译 医院系统"
        
        # 提取关键词
        keywords = []
        if "医院" in system_name or "hospital" in system_name.lower():
            keywords = ["hospital", "医院"]
        elif "图书" in system_name or "library" in system_name.lower():
            keywords = ["library", "图书"]
        elif "订单" in system_name or "order" in system_name.lower():
            keywords = ["order", "订单"]
        else:
            keywords = [system_name.split()[0]]
        
        # 搜索文件
        print(f"正在搜索 {system_name} 相关文件...")
        for keyword in keywords:
            search_result = self.tools.search_pim_files(keyword)
            if "找到" in search_result and "examples/" in search_result:
                # 提取文件路径
                lines = search_result.split('\n')
                for line in lines:
                    if "examples/" in line and ".md" in line:
                        # 提取路径
                        parts = line.strip().split()
                        for part in parts:
                            if "examples/" in part and part.endswith(".md"):
                                file_path = part.strip("- ")
                                print(f"找到文件: {file_path}")
                                print("开始编译...")
                                return self.tools.compile_pim(file_path)
        
        return f"未找到 {system_name} 相关的 PIM 文件"
    
    def log_command(self, args):
        """日志命令"""
        system_name = " ".join(args) if args else None
        return self.tools.check_log(system_name)
    
    def list_command(self, args):
        """列出命令"""
        return self.tools.list_compiled_projects()
    
    def clean_command(self, args):
        """清理命令"""
        if not args:
            return "请指定要清理的项目名称"
        project_name = args[0]
        return self.tools.clean_output(project_name)
    
    def help_command(self, args):
        """帮助命令"""
        return """
PIM 编译器命令帮助：

基本命令：
  搜索 <关键词>     - 搜索 PIM 文件
  编译 <系统名称>   - 智能编译（如: 编译 医院系统）
  编译 <文件路径>   - 编译指定文件（如: 编译 examples/library.md）
  日志 [系统名称]   - 查看编译日志
  列出             - 列出所有已编译项目
  清理 <项目名称>   - 清理编译输出
  帮助             - 显示此帮助信息

快捷用法：
  "编译医院系统" - 自动搜索并编译医院相关系统
  "日志" - 查看所有活动的编译任务
  "列出" - 显示所有已编译的项目

退出：
  输入 'exit' 或 'quit' 或按 Ctrl+C
"""
    
    def process_input(self, user_input):
        """处理用户输入"""
        # 分词
        parts = user_input.strip().split()
        if not parts:
            return ""
        
        # 提取命令和参数
        command = parts[0]
        args = parts[1:]
        
        # 特殊处理"编译XX系统"格式
        if command == "编译" and len(parts) >= 2:
            # 检查是否是"编译医院系统"这种格式
            if any(keyword in user_input for keyword in ["系统", "system"]):
                return self.smart_compile(user_input.replace("编译", "").strip())
        
        # 查找命令
        handler = self.commands.get(command)
        if handler:
            return handler(args)
        else:
            # 尝试将整个输入作为智能命令处理
            if "编译" in user_input:
                system_name = user_input.replace("编译", "").strip()
                return self.smart_compile(system_name)
            elif "日志" in user_input or "查看" in user_input:
                return self.log_command([])
            elif "列出" in user_input or "项目" in user_input:
                return self.list_command([])
            else:
                return f"未知命令: {command}\n输入 '帮助' 查看可用命令"
    
    def run(self):
        """运行聊天机器人"""
        print("🤖 PIM 编译器助手（简化版）")
        print("=" * 60)
        print("这是无需 LLM 的版本，直接使用命令控制")
        print("输入 '帮助' 查看可用命令")
        print("输入 'exit' 退出\n")
        
        while True:
            try:
                user_input = input("你: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                # 处理输入
                result = self.process_input(user_input)
                print(f"\n助手: {result}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 出错了: {str(e)}\n")


def main():
    """主函数"""
    # 设置工作目录
    os.chdir(Path(__file__).parent.parent)
    
    # 运行聊天机器人
    bot = SimpleChatbot()
    bot.run()


if __name__ == "__main__":
    main()