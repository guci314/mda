#!/usr/bin/env python3
"""
使用管道与 Gemini CLI 交互的演示
"""

import subprocess
import os
import time
import select
import fcntl

class GeminiPipeManager:
    """使用管道管理 Gemini CLI"""
    
    def __init__(self):
        self.process = None
        
    def start(self):
        """启动 Gemini CLI 进程"""
        print("启动 Gemini CLI...")
        
        # 创建管道
        self.process = subprocess.Popen(
            ['gemini', '-c'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # 行缓冲
        )
        
        # 设置非阻塞模式
        fd = self.process.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        
        print(f"✅ Gemini CLI 已启动，PID: {self.process.pid}")
        
        # 读取初始输出
        time.sleep(1)
        self._read_available()
        
    def send_and_receive(self, message: str, timeout: float = 5.0) -> str:
        """发送消息并接收响应"""
        if not self.process:
            return "错误: Gemini 未启动"
        
        print(f"\n发送: {message}")
        
        # 发送消息
        try:
            self.process.stdin.write(message + '\n')
            self.process.stdin.flush()
        except Exception as e:
            return f"发送错误: {str(e)}"
        
        # 等待并读取响应
        response = self._read_response(timeout)
        return response
    
    def _read_response(self, timeout: float) -> str:
        """读取响应，带超时"""
        if not self.process:
            return ""
        
        response_lines = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 使用 select 检查是否有数据可读
            ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
            
            if ready:
                try:
                    # 读取所有可用数据
                    while True:
                        line = self.process.stdout.readline()
                        if not line:
                            break
                        line = line.strip()
                        if line and line != '>':  # 忽略提示符
                            response_lines.append(line)
                except:
                    break
            
            # 如果已经有响应，等待一小段时间看是否还有更多
            if response_lines:
                time.sleep(0.5)
                if not select.select([self.process.stdout], [], [], 0.1)[0]:
                    break
        
        return '\n'.join(response_lines)
    
    def _read_available(self):
        """读取所有可用输出"""
        try:
            while True:
                ready, _, _ = select.select([self.process.stdout], [], [], 0)
                if not ready:
                    break
                line = self.process.stdout.readline()
                if not line:
                    break
        except:
            pass
    
    def stop(self):
        """停止 Gemini CLI"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print(f"✅ Gemini CLI (PID: {self.process.pid}) 已停止")


def test_pipe_interaction():
    """测试管道交互"""
    print("=== Gemini CLI 管道交互测试 ===\n")
    
    manager = GeminiPipeManager()
    
    try:
        # 启动
        manager.start()
        time.sleep(2)
        
        # 测试1: 问候
        print("\n测试1: 发送问候")
        response = manager.send_and_receive("你好，我是一个 Python 程序")
        print(f"响应: {response[:200]}..." if len(response) > 200 else f"响应: {response}")
        
        # 测试2: 设置信息
        print("\n测试2: 设置信息")
        response = manager.send_and_receive("请记住：项目代号是 ALPHA-2025")
        print(f"响应: {response[:200]}..." if len(response) > 200 else f"响应: {response}")
        
        # 测试3: 验证记忆
        print("\n测试3: 验证记忆")
        response = manager.send_and_receive("我刚才说的项目代号是什么？")
        print(f"响应: {response}")
        
        if "ALPHA-2025" in response:
            print("\n✅ 成功！Gemini 记住了信息。")
        else:
            print("\n⚠️  Gemini 可能没有记住信息。")
        
    finally:
        # 停止
        manager.stop()


def test_multiple_processes():
    """测试多个独立的 gemini 进程"""
    print("=== 多进程测试 ===\n")
    
    # 使用多个独立的 gemini 调用
    messages = [
        "我的电话号码是18674048895",
        "我刚才告诉你的电话号码是什么？"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n调用 {i}: {msg}")
        try:
            result = subprocess.run(
                ['gemini', '-c', '-p', msg],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"响应: {result.stdout}")
        except Exception as e:
            print(f"错误: {str(e)}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'multi':
        test_multiple_processes()
    else:
        test_pipe_interaction()