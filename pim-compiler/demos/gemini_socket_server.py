#!/usr/bin/env python3
"""
使用 Unix 域套接字的 Gemini CLI 服务器

提供更可靠的进程间通信
"""

import os
import socket
import subprocess
import threading
import json
import time
import signal
import sys
from pathlib import Path
import queue
import uuid

class GeminiSocketServer:
    """基于 Unix 套接字的 Gemini 服务器"""
    
    def __init__(self, socket_path="/tmp/gemini_server.sock"):
        self.socket_path = socket_path
        self.server_socket = None
        self.gemini_process = None
        self.clients = {}
        self.running = False
        self.response_queue = queue.Queue()
        
    def start(self):
        """启动服务器"""
        # 确保删除旧的套接字文件
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
            
        # 创建 Unix 域套接字
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(5)
        
        print(f"✅ Gemini 套接字服务器已启动")
        print(f"   套接字: {self.socket_path}")
        
        self.running = True
        
        # 启动接受连接的线程
        accept_thread = threading.Thread(target=self._accept_connections)
        accept_thread.start()
        
        try:
            accept_thread.join()
        except KeyboardInterrupt:
            self.stop()
            
    def _accept_connections(self):
        """接受客户端连接"""
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, _ = self.server_socket.accept()
                
                # 为每个客户端创建处理线程
                client_id = str(uuid.uuid4())
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_id)
                )
                client_thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"接受连接错误: {e}")
                    
    def _handle_client(self, client_socket, client_id):
        """处理客户端请求"""
        try:
            while self.running:
                # 接收请求
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                request = json.loads(data.decode('utf-8'))
                message = request.get('message', '')
                
                print(f"[{client_id[:8]}] 收到: {message}")
                
                # 调用 Gemini CLI
                response = self._call_gemini(message)
                
                # 发送响应
                response_data = {
                    'status': 'success',
                    'response': response,
                    'timestamp': time.time()
                }
                
                client_socket.send(json.dumps(response_data).encode('utf-8'))
                
        except Exception as e:
            print(f"处理客户端错误: {e}")
        finally:
            client_socket.close()
            
    def _call_gemini(self, message: str) -> str:
        """调用 Gemini CLI"""
        try:
            result = subprocess.run(
                ['gemini', '-c', '-p', message],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "错误: 请求超时"
        except Exception as e:
            return f"错误: {str(e)}"
            
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        print("✅ 服务器已停止")


class GeminiSocketClient:
    """Gemini 套接字客户端"""
    
    def __init__(self, socket_path="/tmp/gemini_server.sock"):
        self.socket_path = socket_path
        
    def send_message(self, message: str) -> str:
        """发送消息到服务器"""
        try:
            # 连接到服务器
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_socket.connect(self.socket_path)
            
            # 发送请求
            request = {
                'message': message,
                'timestamp': time.time()
            }
            client_socket.send(json.dumps(request).encode('utf-8'))
            
            # 接收响应
            response_data = client_socket.recv(8192)
            response = json.loads(response_data.decode('utf-8'))
            
            client_socket.close()
            
            return response.get('response', '无响应')
            
        except FileNotFoundError:
            return "错误: 服务器未运行"
        except Exception as e:
            return f"错误: {str(e)}"


# 使用 Screen 或 tmux 的版本
class GeminiScreenServer:
    """使用 GNU Screen 管理 Gemini CLI"""
    
    def __init__(self, session_name="gemini_session"):
        self.session_name = session_name
        
    def start(self):
        """在 screen 会话中启动 Gemini"""
        # 检查 screen 是否安装
        check = subprocess.run(['which', 'screen'], capture_output=True)
        if check.returncode != 0:
            print("❌ 请先安装 screen: sudo apt-get install screen")
            return False
            
        # 创建新的 screen 会话并运行 gemini
        cmd = f"screen -dmS {self.session_name} gemini -c"
        subprocess.run(cmd, shell=True)
        
        time.sleep(1)
        
        # 检查会话是否创建成功
        if self.is_running():
            print(f"✅ Gemini 已在 screen 会话 '{self.session_name}' 中启动")
            print(f"   查看会话: screen -r {self.session_name}")
            print(f"   分离会话: Ctrl+A, D")
            return True
        else:
            print("❌ 启动失败")
            return False
            
    def send_command(self, command: str):
        """向 screen 会话发送命令"""
        # 发送命令到 screen 会话
        cmd = f"screen -S {self.session_name} -X stuff '{command}\\n'"
        subprocess.run(cmd, shell=True)
        
    def is_running(self):
        """检查会话是否存在"""
        result = subprocess.run(
            f"screen -ls | grep {self.session_name}",
            shell=True,
            capture_output=True
        )
        return result.returncode == 0
        
    def stop(self):
        """停止 screen 会话"""
        subprocess.run(f"screen -S {self.session_name} -X quit", shell=True)
        print(f"✅ Screen 会话 '{self.session_name}' 已停止")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  套接字服务器:")
        print("    python gemini_socket_server.py socket-server")
        print("    python gemini_socket_server.py socket-client '消息'")
        print("")
        print("  Screen 服务器:")
        print("    python gemini_socket_server.py screen-start")
        print("    python gemini_socket_server.py screen-send '命令'")
        print("    python gemini_socket_server.py screen-stop")
        return
        
    command = sys.argv[1]
    
    if command == "socket-server":
        server = GeminiSocketServer()
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
            
    elif command == "socket-client":
        if len(sys.argv) < 3:
            print("请提供消息")
            return
            
        client = GeminiSocketClient()
        message = sys.argv[2]
        print(f"发送: {message}")
        response = client.send_message(message)
        print(f"响应: {response}")
        
    elif command == "screen-start":
        server = GeminiScreenServer()
        server.start()
        
    elif command == "screen-send":
        if len(sys.argv) < 3:
            print("请提供命令")
            return
            
        server = GeminiScreenServer()
        if not server.is_running():
            print("❌ Screen 会话未运行")
            return
            
        command = sys.argv[2]
        server.send_command(command)
        print(f"✅ 已发送: {command}")
        
    elif command == "screen-stop":
        server = GeminiScreenServer()
        server.stop()
        
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()