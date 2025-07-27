#!/usr/bin/env python3
"""
使用 PTY（伪终端）与 Gemini CLI 交互
"""

import os
import pty
import subprocess
import select
import time
import sys

class GeminiPTYManager:
    """使用 PTY 管理 Gemini CLI"""
    
    def __init__(self):
        self.master_fd = None
        self.slave_fd = None
        self.process = None
        
    def start(self):
        """启动 Gemini CLI with PTY"""
        print("使用 PTY 启动 Gemini CLI...")
        
        # 创建伪终端
        self.master_fd, self.slave_fd = pty.openpty()
        
        # 启动进程
        self.process = subprocess.Popen(
            ['gemini', '-c'],
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            close_fds=True
        )
        
        # 关闭子进程中的从端
        os.close(self.slave_fd)
        
        print(f"✅ Gemini CLI 已启动 (PTY)，PID: {self.process.pid}")
        
        # 读取初始输出
        time.sleep(1)
        self._read_available()
        
    def send_and_receive(self, message: str, timeout: float = 5.0) -> str:
        """发送消息并接收响应"""
        if not self.master_fd:
            return "错误: Gemini 未启动"
        
        print(f"\n发送: {message}")
        
        # 发送消息
        try:
            os.write(self.master_fd, (message + '\n').encode())
        except Exception as e:
            return f"发送错误: {str(e)}"
        
        # 读取响应
        response = self._read_response(timeout)
        return response
    
    def _read_response(self, timeout: float) -> str:
        """读取响应"""
        response_data = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查是否有数据可读
            ready, _, _ = select.select([self.master_fd], [], [], 0.1)
            
            if ready:
                try:
                    data = os.read(self.master_fd, 1024)
                    if data:
                        response_data.append(data.decode('utf-8', errors='ignore'))
                except:
                    break
            
            # 如果已经有响应，等待看是否还有更多
            if response_data:
                time.sleep(0.5)
                if not select.select([self.master_fd], [], [], 0.1)[0]:
                    break
        
        response = ''.join(response_data)
        # 清理 ANSI 转义序列和控制字符
        response = self._clean_output(response)
        return response
    
    def _read_available(self):
        """读取所有可用数据"""
        try:
            while True:
                ready, _, _ = select.select([self.master_fd], [], [], 0)
                if not ready:
                    break
                data = os.read(self.master_fd, 1024)
                if not data:
                    break
        except:
            pass
    
    def _clean_output(self, text: str) -> str:
        """清理输出文本"""
        import re
        # 移除 ANSI 转义序列
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)
        # 移除控制字符
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        # 移除多余的空行
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        return '\n'.join(lines)
    
    def stop(self):
        """停止 Gemini CLI"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print(f"✅ Gemini CLI (PID: {self.process.pid}) 已停止")
        
        if self.master_fd:
            os.close(self.master_fd)


def test_pty_interaction():
    """测试 PTY 交互"""
    print("=== Gemini CLI PTY 交互测试 ===\n")
    
    manager = GeminiPTYManager()
    
    try:
        # 启动
        manager.start()
        time.sleep(2)
        
        # 测试对话
        conversations = [
            ("你好，我是通过 PTY 连接的 Python 程序", "问候"),
            ("请记住这个数字：42", "设置信息"),
            ("我刚才告诉你的数字是什么？", "验证记忆")
        ]
        
        for message, description in conversations:
            print(f"\n测试: {description}")
            response = manager.send_and_receive(message)
            print(f"响应: {response[:200]}..." if len(response) > 200 else f"响应: {response}")
            
            if description == "验证记忆" and "42" in response:
                print("\n✅ 成功！Gemini 记住了信息。")
        
    finally:
        manager.stop()


def test_context_accumulation():
    """测试上下文累积"""
    print("=== 测试上下文累积 ===\n")
    
    # 创建一个包含历史的提示
    history = []
    
    conversations = [
        "我叫张三",
        "我是一名 Python 开发者",
        "我在研究 Gemini CLI",
        "请总结一下你了解到的关于我的信息"
    ]
    
    for i, message in enumerate(conversations, 1):
        print(f"\n第 {i} 轮对话:")
        
        # 构建包含历史的提示
        if history:
            prompt = "基于以下对话历史：\n"
            for h in history:
                prompt += f"用户: {h['user']}\n"
                prompt += f"助手: {h['assistant'][:100]}...\n" if len(h['assistant']) > 100 else f"助手: {h['assistant']}\n"
            prompt += f"\n当前问题: {message}"
        else:
            prompt = message
        
        print(f"发送: {message}")
        
        try:
            result = subprocess.run(
                ['gemini', '-c', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=10
            )
            response = result.stdout.strip()
            print(f"响应: {response[:200]}..." if len(response) > 200 else f"响应: {response}")
            
            # 添加到历史
            history.append({
                'user': message,
                'assistant': response
            })
            
            # 检查最后的总结
            if i == len(conversations):
                if all(keyword in response for keyword in ["张三", "Python", "Gemini"]):
                    print("\n✅ 成功！Gemini 基于上下文历史正确总结了信息。")
                else:
                    print("\n⚠️  总结可能不完整。")
                    
        except Exception as e:
            print(f"错误: {str(e)}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'context':
            test_context_accumulation()
        else:
            print("未知参数。可用: context")
    else:
        test_pty_interaction()