#!/usr/bin/env python3
"""
后台运行 Gemini CLI 服务器

通过命名管道（FIFO）与后台 Gemini CLI 进程交互
"""

import os
import subprocess
import time
import threading
import json
import signal
import sys
from pathlib import Path
import fcntl
import select

class GeminiBackgroundServer:
    """Gemini CLI 后台服务器"""
    
    def __init__(self, server_name="gemini_server"):
        self.server_name = server_name
        self.work_dir = Path(f"/tmp/{server_name}")
        self.pid_file = self.work_dir / "gemini.pid"
        self.input_fifo = self.work_dir / "input.fifo"
        self.output_fifo = self.work_dir / "output.fifo"
        self.log_file = self.work_dir / "server.log"
        self.process = None
        
    def setup_environment(self):
        """设置工作环境"""
        # 创建工作目录
        self.work_dir.mkdir(exist_ok=True)
        
        # 删除旧的 FIFO
        for fifo in [self.input_fifo, self.output_fifo]:
            if fifo.exists():
                os.unlink(fifo)
        
        # 创建命名管道
        os.mkfifo(self.input_fifo)
        os.mkfifo(self.output_fifo)
        
        print(f"✅ 工作环境已设置: {self.work_dir}")
        
    def start_server(self):
        """启动后台 Gemini CLI 服务器"""
        self.setup_environment()
        
        # 启动 Gemini CLI 进程
        with open(self.log_file, 'w') as log:
            # 使用 shell 命令重定向
            cmd = f"exec gemini -c < {self.input_fifo} > {self.output_fifo} 2>&1"
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid  # 创建新的进程组
            )
        
        # 保存 PID
        with open(self.pid_file, 'w') as f:
            f.write(str(self.process.pid))
        
        print(f"✅ Gemini CLI 服务器已启动")
        print(f"   PID: {self.process.pid}")
        print(f"   输入管道: {self.input_fifo}")
        print(f"   输出管道: {self.output_fifo}")
        print(f"   日志文件: {self.log_file}")
        
        # 启动输出读取线程
        self.output_thread = threading.Thread(target=self._output_reader, daemon=True)
        self.output_thread.start()
        
    def _output_reader(self):
        """持续读取输出管道"""
        try:
            # 以非阻塞方式打开输出管道
            output_fd = os.open(str(self.output_fifo), os.O_RDONLY | os.O_NONBLOCK)
            
            while self.process and self.process.poll() is None:
                # 使用 select 等待数据
                ready, _, _ = select.select([output_fd], [], [], 0.1)
                if ready:
                    try:
                        data = os.read(output_fd, 4096)
                        if data:
                            # 这里可以处理输出，比如保存到缓冲区
                            pass
                    except:
                        pass
                        
            os.close(output_fd)
        except Exception as e:
            print(f"输出读取器错误: {e}")
            
    def stop_server(self):
        """停止服务器"""
        if self.process:
            # 终止整个进程组
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait()
            print(f"✅ Gemini CLI 服务器已停止")
            
        # 清理环境
        for fifo in [self.input_fifo, self.output_fifo]:
            if fifo.exists():
                os.unlink(fifo)
                
    def is_running(self):
        """检查服务器是否运行"""
        if not self.pid_file.exists():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # 检查进程是否存在
            return True
        except:
            return False


class GeminiClient:
    """Gemini CLI 客户端"""
    
    def __init__(self, server_name="gemini_server"):
        self.server_name = server_name
        self.work_dir = Path(f"/tmp/{server_name}")
        self.input_fifo = self.work_dir / "input.fifo"
        self.output_fifo = self.work_dir / "output.fifo"
        
    def send_message(self, message: str, timeout: float = 5.0) -> str:
        """发送消息并获取响应"""
        if not self.input_fifo.exists() or not self.output_fifo.exists():
            return "错误: 服务器未运行"
            
        try:
            # 先打开输出管道（非阻塞）
            output_fd = os.open(str(self.output_fifo), os.O_RDONLY | os.O_NONBLOCK)
            
            # 清空之前的输出
            self._drain_output(output_fd)
            
            # 发送消息
            with open(self.input_fifo, 'w') as f:
                f.write(message + '\n')
                f.flush()
            
            # 读取响应
            response = self._read_response(output_fd, timeout)
            os.close(output_fd)
            
            return response
            
        except Exception as e:
            return f"错误: {str(e)}"
            
    def _drain_output(self, fd):
        """清空输出缓冲区"""
        while True:
            ready, _, _ = select.select([fd], [], [], 0)
            if not ready:
                break
            try:
                os.read(fd, 4096)
            except:
                break
                
    def _read_response(self, fd, timeout: float) -> str:
        """读取响应"""
        response_lines = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ready, _, _ = select.select([fd], [], [], 0.1)
            if ready:
                try:
                    data = os.read(fd, 4096)
                    if data:
                        lines = data.decode('utf-8', errors='ignore').split('\n')
                        response_lines.extend(lines)
                except:
                    break
                    
            # 如果已经有响应，等待一下看是否还有更多
            if response_lines:
                time.sleep(0.5)
                if not select.select([fd], [], [], 0.1)[0]:
                    break
                    
        # 清理响应
        response = '\n'.join(line.strip() for line in response_lines if line.strip())
        return response


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  启动服务器: python gemini_background_server.py start")
        print("  停止服务器: python gemini_background_server.py stop")
        print("  发送消息: python gemini_background_server.py send '你的消息'")
        print("  交互模式: python gemini_background_server.py interactive")
        return
        
    command = sys.argv[1]
    
    if command == "start":
        server = GeminiBackgroundServer()
        if server.is_running():
            print("⚠️  服务器已经在运行")
            return
            
        server.start_server()
        print("\n现在可以使用客户端发送消息:")
        print(f"  python {sys.argv[0]} send '你的消息'")
        
        # 保持服务器运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止服务器...")
            server.stop_server()
            
    elif command == "stop":
        server = GeminiBackgroundServer()
        if not server.is_running():
            print("⚠️  服务器未运行")
            return
            
        # 读取 PID 并停止进程
        pid_file = Path(f"/tmp/gemini_server/gemini.pid")
        if pid_file.exists():
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                print("✅ 服务器已停止")
            except:
                print("❌ 无法停止服务器")
                
        # 清理文件
        work_dir = Path("/tmp/gemini_server")
        if work_dir.exists():
            import shutil
            shutil.rmtree(work_dir)
            
    elif command == "send":
        if len(sys.argv) < 3:
            print("请提供消息内容")
            return
            
        message = sys.argv[2]
        client = GeminiClient()
        
        print(f"发送: {message}")
        response = client.send_message(message)
        print(f"响应: {response}")
        
    elif command == "interactive":
        client = GeminiClient()
        print("进入交互模式 (输入 'exit' 退出)")
        
        while True:
            try:
                message = input("\n你: ")
                if message.lower() == 'exit':
                    break
                    
                response = client.send_message(message)
                print(f"Gemini: {response}")
                
            except KeyboardInterrupt:
                break
                
        print("\n再见!")
        
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()