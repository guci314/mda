#!/usr/bin/env python3
"""
gemini_stateful_cli.py - Python 封装实现有状态的 Gemini CLI 交互
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class GeminiStatefulCLI:
    """有状态的 Gemini CLI 封装"""
    
    def __init__(self, session_name: str = "default"):
        self.session_name = session_name
        self.history: List[Dict[str, Any]] = []
        
    def chat(self, message: str) -> str:
        """
        发送消息到 Gemini CLI 并获取响应
        使用 -c 参数保持会话状态
        """
        try:
            # 使用 subprocess 调用 gemini
            result = subprocess.run(
                ['gemini', '-c', '-p', message],
                capture_output=True,
                text=True,
                check=True
            )
            
            response = result.stdout.strip()
            
            # 记录到历史
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'user',
                'content': message
            })
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'assistant',
                'content': response
            })
            
            return response
            
        except subprocess.CalledProcessError as e:
            return f"错误: {e.stderr}"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def save_history(self, filename: Optional[str] = None):
        """保存对话历史"""
        if filename is None:
            filename = f"gemini_history_{self.session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'session_name': self.session_name,
                'history': self.history
            }, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def print_history(self):
        """打印对话历史"""
        for item in self.history:
            role = "You" if item['role'] == 'user' else "Gemini"
            print(f"\n[{role}]: {item['content']}")


def test_memory():
    """测试记忆功能"""
    print("=== Gemini CLI 记忆测试 ===\n")
    
    gemini = GeminiStatefulCLI("memory_test")
    
    # 第一次交互
    print("步骤1: 告诉 Gemini 电话号码")
    response1 = gemini.chat("我的电话号码是18674048895，请记住它。")
    print(f"Gemini: {response1}")
    
    # 第二次交互
    print("\n步骤2: 询问电话号码")
    response2 = gemini.chat("我刚才告诉你的电话号码是什么？")
    print(f"Gemini: {response2}")
    
    # 检查是否记住
    if "18674048895" in response2:
        print("\n✅ 成功！Gemini 记住了电话号码。")
    else:
        print("\n❌ 失败！Gemini 没有记住电话号码。")
    
    # 保存历史
    filename = gemini.save_history()
    print(f"\n对话历史已保存到: {filename}")


def interactive_demo():
    """交互式演示"""
    print("=== Gemini CLI 交互式会话 ===")
    print("输入 'exit' 退出，'history' 查看历史\n")
    
    gemini = GeminiStatefulCLI("interactive")
    
    while True:
        try:
            user_input = input("You: ")
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'history':
                gemini.print_history()
                continue
            
            response = gemini.chat(user_input)
            print(f"Gemini: {response}")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
    
    # 询问是否保存历史
    save = input("\n是否保存对话历史？(y/n): ")
    if save.lower() == 'y':
        filename = gemini.save_history()
        print(f"历史已保存到: {filename}")


def multi_step_workflow():
    """多步骤工作流示例"""
    print("=== 多步骤工作流演示 ===\n")
    
    gemini = GeminiStatefulCLI("workflow")
    
    steps = [
        ("设定角色", "你现在是一个 Python 专家。请记住这个角色。"),
        ("提出需求", "我需要一个函数来计算斐波那契数列的第 n 项。"),
        ("要求优化", "请优化上面的函数，使用动态规划来提高性能。"),
        ("添加文档", "为优化后的函数添加详细的 docstring 文档。"),
        ("生成测试", "为这个函数生成 pytest 测试用例。"),
        ("总结", "总结一下我们刚才完成的工作。")
    ]
    
    for step_name, prompt in steps:
        print(f"\n[{step_name}]")
        print(f"发送: {prompt}")
        response = gemini.chat(prompt)
        print(f"响应: {response[:200]}..." if len(response) > 200 else f"响应: {response}")
    
    # 保存工作流结果
    filename = gemini.save_history()
    print(f"\n\n工作流完成！结果已保存到: {filename}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "test":
            test_memory()
        elif mode == "interactive":
            interactive_demo()
        elif mode == "workflow":
            multi_step_workflow()
        else:
            print("未知模式。可用模式: test, interactive, workflow")
    else:
        # 默认运行测试
        print("可用模式:")
        print("1. test - 测试记忆功能")
        print("2. interactive - 交互式会话")
        print("3. workflow - 多步骤工作流")
        print("\n运行方式:")
        print("python3 gemini_stateful_cli.py test")
        print("python3 gemini_stateful_cli.py interactive")
        print("python3 gemini_stateful_cli.py workflow")
        print("\n默认运行记忆测试...\n")
        test_memory()