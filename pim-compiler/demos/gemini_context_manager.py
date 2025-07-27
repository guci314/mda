#!/usr/bin/env python3
"""
gemini_context_manager.py - 显式管理上下文的 Gemini CLI 封装
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class GeminiContextManager:
    """带上下文管理的 Gemini CLI 封装"""
    
    def __init__(self, session_name: str = "default", max_context_messages: int = 10):
        self.session_name = session_name
        self.max_context_messages = max_context_messages
        self.history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        
    def _build_prompt_with_context(self, message: str) -> str:
        """构建带上下文的提示词"""
        if not self.history:
            return message
        
        # 获取最近的对话历史
        recent_history = self.history[-self.max_context_messages:]
        
        # 构建上下文
        context_parts = ["基于以下对话历史：\n"]
        for item in recent_history:
            role = "用户" if item['role'] == 'user' else "助手"
            context_parts.append(f"{role}: {item['content']}\n")
        
        context_parts.append(f"\n当前请求: {message}")
        context_parts.append("\n请基于上述对话历史回答。")
        
        return "".join(context_parts)
    
    def chat(self, message: str, include_context: bool = True) -> str:
        """发送消息到 Gemini CLI"""
        try:
            # 构建提示
            if include_context and self.history:
                prompt = self._build_prompt_with_context(message)
            else:
                prompt = message
            
            # 调用 Gemini
            result = subprocess.run(
                ['gemini', '-c', '-p', prompt],
                capture_output=True,
                text=True,
                check=True
            )
            
            response = result.stdout.strip()
            
            # 记录到历史（只记录原始消息，不记录上下文）
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
    
    def set_context(self, key: str, value: Any):
        """设置上下文变量"""
        self.context[key] = value
    
    def get_context(self, key: str) -> Any:
        """获取上下文变量"""
        return self.context.get(key)
    
    def save_session(self, filename: Optional[str] = None):
        """保存会话"""
        if filename is None:
            filename = f"gemini_session_{self.session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'session_name': self.session_name,
                'history': self.history,
                'context': self.context
            }, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def load_session(self, filename: str):
        """加载会话"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.session_name = data.get('session_name', self.session_name)
            self.history = data.get('history', [])
            self.context = data.get('context', {})


def test_context_workflow():
    """测试带上下文的工作流"""
    print("=== 带上下文管理的工作流演示 ===\n")
    
    gemini = GeminiContextManager("context_workflow", max_context_messages=6)
    
    # 步骤1：设定角色
    print("[步骤1] 设定角色")
    response1 = gemini.chat("你现在是一个 Python 专家。请记住这个角色。")
    print(f"响应: {response1}\n")
    
    # 步骤2：创建函数
    print("[步骤2] 创建函数")
    response2 = gemini.chat("创建一个递归实现的斐波那契函数，函数名为 fibonacci_recursive。")
    print(f"响应: {response2[:200]}...\n" if len(response2) > 200 else f"响应: {response2}\n")
    
    # 保存函数代码到上下文
    gemini.set_context("fibonacci_code", response2)
    
    # 步骤3：优化函数
    print("[步骤3] 优化函数")
    response3 = gemini.chat("请优化上面的 fibonacci_recursive 函数，使用动态规划方法，函数名改为 fibonacci_dp。")
    print(f"响应: {response3[:200]}...\n" if len(response3) > 200 else f"响应: {response3}\n")
    
    # 步骤4：添加文档
    print("[步骤4] 添加文档")
    response4 = gemini.chat("为刚才的 fibonacci_dp 函数添加详细的 docstring 文档，包括参数说明和示例。")
    print(f"响应: {response4[:200]}...\n" if len(response4) > 200 else f"响应: {response4}\n")
    
    # 步骤5：生成测试
    print("[步骤5] 生成测试")
    response5 = gemini.chat("为 fibonacci_dp 函数生成完整的 pytest 测试用例，测试正常情况和边界情况。")
    print(f"响应: {response5[:200]}...\n" if len(response5) > 200 else f"响应: {response5}\n")
    
    # 步骤6：总结
    print("[步骤6] 总结")
    response6 = gemini.chat("总结我们刚才完成的工作，列出创建的所有函数和测试。")
    print(f"响应: {response6}\n")
    
    # 保存会话
    filename = gemini.save_session()
    print(f"\n会话已保存到: {filename}")
    
    # 测试是否真的记住了上下文
    if "fibonacci" in response6.lower():
        print("✅ 成功！Gemini 通过上下文管理记住了整个工作流。")
    else:
        print("⚠️  Gemini 可能没有完全理解上下文。")


def interactive_context_demo():
    """交互式上下文演示"""
    print("=== 交互式上下文管理演示 ===")
    print("命令: exit(退出), history(历史), context(上下文), save(保存)")
    print("特殊前缀: @no-context 表示不包含历史上下文\n")
    
    gemini = GeminiContextManager("interactive_context")
    
    while True:
        try:
            user_input = input("You: ")
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'history':
                for i, item in enumerate(gemini.history):
                    if item['role'] == 'user':
                        print(f"\n[{i//2 + 1}] {item['content']}")
                continue
            elif user_input.lower() == 'context':
                print(f"上下文变量: {gemini.context}")
                continue
            elif user_input.lower() == 'save':
                filename = gemini.save_session()
                print(f"会话已保存到: {filename}")
                continue
            
            # 检查是否不包含上下文
            include_context = True
            if user_input.startswith("@no-context "):
                include_context = False
                user_input = user_input[12:]
            
            response = gemini.chat(user_input, include_context=include_context)
            print(f"Gemini: {response}")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_context_demo()
    else:
        # 默认运行工作流测试
        test_context_workflow()