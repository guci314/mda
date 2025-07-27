#!/usr/bin/env python3
"""
gemini_pid_interaction.py - 通过进程 PID 与 Gemini CLI 交互
演示如何连接到已运行的 Gemini CLI 进程并进行交互
"""

import subprocess
import os
import time
import signal
import threading
import queue
from pathlib import Path
from typing import Optional, Tuple


class GeminiProcessManager:
    """管理 Gemini CLI 进程的类"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.output_queue = queue.Queue()
        self.reader_thread: Optional[threading.Thread] = None
        
    def start_gemini(self) -> int:
        """启动 Gemini CLI 进程并返回 PID"""
        # 启动 Gemini CLI - 使用 -p 参数直接传递消息
        # 注意：这里我们不使用交互模式，而是每次调用新的 gemini 进程
        self.pid = os.getpid()  # 使用当前进程 PID 作为标识
        
        print(f"✅ Gemini CLI 管理器已启动，PID: {self.pid}")
        return self.pid
    
    def _call_gemini(self, message: str) -> str:
        """调用 gemini CLI 并返回响应"""
        try:
            # 使用 -c -p 参数调用 gemini
            result = subprocess.run(
                ['gemini', '-c', '-p', message],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"错误: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "错误: 命令超时"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def send_command(self, command: str) -> str:
        """发送命令并获取响应"""
        # 使用新的 gemini 进程处理每个命令
        return self._call_gemini(command)
    
    def stop(self):
        """停止管理器"""
        print(f"✅ Gemini 管理器 (PID: {self.pid}) 已停止")


class GeminiPIDConnector:
    """连接到已存在的 Gemini CLI 进程"""
    
    def __init__(self, pid: int):
        self.pid = pid
        self.pipe_dir = Path(f"/tmp/gemini_pipes_{pid}")
        self.pipe_in = self.pipe_dir / "input"
        self.pipe_out = self.pipe_dir / "output"
        
    def connect(self) -> bool:
        """尝试连接到进程"""
        # 检查进程是否存在
        try:
            os.kill(self.pid, 0)
        except ProcessLookupError:
            print(f"❌ 进程 {self.pid} 不存在")
            return False
        
        # 检查管道是否存在
        if not self.pipe_in.exists() or not self.pipe_out.exists():
            print(f"❌ 进程 {self.pid} 的通信管道不存在")
            return False
        
        print(f"✅ 已连接到 Gemini 进程 (PID: {self.pid})")
        return True
    
    def send_command(self, command: str) -> str:
        """通过管道发送命令"""
        # 发送命令
        with open(self.pipe_in, 'w') as f:
            f.write(command + '\n')
            f.flush()
        
        # 读取响应
        response_lines = []
        with open(self.pipe_out, 'r') as f:
            while True:
                line = f.readline()
                if not line or line.strip() == '>':
                    break
                response_lines.append(line.strip())
        
        return '\n'.join(response_lines)


def demo_process_management():
    """演示：进程管理和交互"""
    print("=== Gemini CLI 进程管理演示 ===\n")
    
    manager = GeminiProcessManager()
    
    try:
        # 启动 Gemini
        pid = manager.start_gemini()
        
        # 保存 PID 到文件
        with open('gemini.pid', 'w') as f:
            f.write(str(pid))
        print(f"PID 已保存到 gemini.pid 文件\n")
        
        # 测试交互
        print("测试1: 发送问候")
        response1 = manager.send_command("你好，我是一个 Python 程序")
        print(f"响应: {response1}\n")
        
        print("测试2: 设置信息")
        response2 = manager.send_command("请记住：项目代号是 ALPHA-2025")
        print(f"响应: {response2}\n")
        
        print("测试3: 验证记忆")
        response3 = manager.send_command("我刚才说的项目代号是什么？")
        print(f"响应: {response3}\n")
        
        if "ALPHA-2025" in response3:
            print("✅ Gemini 成功记住了信息！")
        
    finally:
        manager.stop()


def demo_pid_connection():
    """演示：连接到已存在的进程"""
    print("=== 连接到已存在的 Gemini 进程 ===\n")
    
    # 读取 PID 文件
    if not os.path.exists('gemini.pid'):
        print("❌ 未找到 gemini.pid 文件")
        print("请先运行 demo_process_management() 或手动创建 PID 文件")
        return
    
    with open('gemini.pid', 'r') as f:
        pid = int(f.read().strip())
    
    print(f"尝试连接到 PID: {pid}")
    
    # 检查进程是否存在
    try:
        os.kill(pid, 0)
        print(f"✅ 进程 {pid} 正在运行")
    except ProcessLookupError:
        print(f"❌ 进程 {pid} 不存在")
        return
    
    # 这里我们模拟通过其他方式与进程交互
    # 实际上，如果进程不是我们启动的，我们需要其他 IPC 机制
    print("\n注意：直接连接到非子进程需要特殊的 IPC 机制")
    print("常用方法：")
    print("1. 命名管道 (FIFO)")
    print("2. Unix 域套接字")
    print("3. 共享内存")
    print("4. 文件系统监控")


def demo_fifo_communication():
    """演示：使用命名管道进行进程间通信"""
    print("=== 使用 FIFO 进行进程间通信 ===\n")
    
    fifo_in = "/tmp/gemini_fifo_in"
    fifo_out = "/tmp/gemini_fifo_out"
    
    # 创建命名管道
    try:
        os.mkfifo(fifo_in)
        os.mkfifo(fifo_out)
    except FileExistsError:
        pass
    
    print(f"创建命名管道:")
    print(f"  输入: {fifo_in}")
    print(f"  输出: {fifo_out}")
    
    # 启动 Gemini CLI 并重定向到管道
    print("\n启动 Gemini CLI...")
    process = subprocess.Popen(
        f"gemini -c < {fifo_in} > {fifo_out} 2>&1",
        shell=True
    )
    
    print(f"Gemini CLI PID: {process.pid}")
    
    # 在另一个线程中读取输出
    def read_output():
        with open(fifo_out, 'r') as f:
            while True:
                line = f.readline()
                if line:
                    print(f"[Gemini]: {line.strip()}")
    
    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    
    # 发送命令
    time.sleep(2)
    
    print("\n发送命令到 Gemini...")
    with open(fifo_in, 'w') as f:
        f.write("计算 123 + 456\n")
        f.flush()
    
    time.sleep(2)
    
    with open(fifo_in, 'w') as f:
        f.write("生成一个 Python 函数来反转字符串\n")
        f.flush()
    
    time.sleep(3)
    
    # 清理
    process.terminate()
    os.unlink(fifo_in)
    os.unlink(fifo_out)
    print("\n清理完成")


def interactive_demo():
    """交互式演示"""
    print("=== Gemini CLI 进程交互演示 ===")
    print("\n选择演示:")
    print("1. 进程管理和交互")
    print("2. 连接到已存在的进程")
    print("3. FIFO 进程间通信")
    print("4. 完整工作流示例")
    
    choice = input("\n选择 (1-4): ")
    
    if choice == "1":
        demo_process_management()
    elif choice == "2":
        demo_pid_connection()
    elif choice == "3":
        demo_fifo_communication()
    elif choice == "4":
        print("\n运行完整工作流...")
        demo_process_management()
        print("\n" + "="*50 + "\n")
        demo_pid_connection()
    else:
        print("无效选择")


class GeminiSessionManager:
    """高级会话管理器 - 支持多个 Gemini 实例"""
    
    def __init__(self):
        self.sessions: Dict[str, GeminiProcessManager] = {}
        
    def create_session(self, name: str) -> int:
        """创建新会话"""
        if name in self.sessions:
            raise ValueError(f"会话 {name} 已存在")
        
        manager = GeminiProcessManager()
        pid = manager.start_gemini()
        self.sessions[name] = manager
        
        # 保存会话信息
        session_info = {
            'name': name,
            'pid': pid,
            'created_at': time.time()
        }
        
        with open(f'.gemini_session_{name}.json', 'w') as f:
            import json
            json.dump(session_info, f)
        
        return pid
    
    def get_session(self, name: str) -> GeminiProcessManager:
        """获取会话"""
        return self.sessions.get(name)
    
    def list_sessions(self):
        """列出所有会话"""
        return list(self.sessions.keys())
    
    def close_session(self, name: str):
        """关闭会话"""
        if name in self.sessions:
            self.sessions[name].stop()
            del self.sessions[name]
            
            # 删除会话文件
            session_file = f'.gemini_session_{name}.json'
            if os.path.exists(session_file):
                os.unlink(session_file)


def demo_multi_session():
    """演示：多会话管理"""
    print("=== 多会话 Gemini CLI 管理 ===\n")
    
    manager = GeminiSessionManager()
    
    try:
        # 创建多个会话
        print("创建会话 'dev'...")
        dev_pid = manager.create_session('dev')
        print(f"Dev 会话 PID: {dev_pid}")
        
        print("\n创建会话 'test'...")
        test_pid = manager.create_session('test')
        print(f"Test 会话 PID: {test_pid}")
        
        # 在不同会话中设置不同的上下文
        print("\n设置 dev 会话上下文...")
        dev_session = manager.get_session('dev')
        dev_session.send_command("我是开发环境，数据库是 PostgreSQL")
        
        print("\n设置 test 会话上下文...")
        test_session = manager.get_session('test')
        test_session.send_command("我是测试环境，数据库是 SQLite")
        
        # 验证上下文隔离
        print("\n验证上下文隔离...")
        
        dev_response = dev_session.send_command("我使用什么数据库？")
        print(f"Dev 环境: {dev_response}")
        
        test_response = test_session.send_command("我使用什么数据库？")
        print(f"Test 环境: {test_response}")
        
    finally:
        # 清理所有会话
        for session_name in manager.list_sessions():
            manager.close_session(session_name)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "manage":
            demo_process_management()
        elif sys.argv[1] == "connect":
            demo_pid_connection()
        elif sys.argv[1] == "fifo":
            demo_fifo_communication()
        elif sys.argv[1] == "multi":
            demo_multi_session()
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("可用参数: manage, connect, fifo, multi")
    else:
        interactive_demo()