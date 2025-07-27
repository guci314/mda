#!/usr/bin/env python3
"""
Gemini CLI 会话管理器

使用文件系统和锁机制管理 Gemini CLI 会话
"""

import os
import subprocess
import json
import time
import fcntl
import signal
import sys
from pathlib import Path
from datetime import datetime
import hashlib

class GeminiSessionManager:
    """管理 Gemini CLI 会话"""
    
    def __init__(self, session_dir="/tmp/gemini_sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        
    def create_session(self, session_id=None):
        """创建新会话"""
        if not session_id:
            session_id = f"session_{int(time.time())}"
            
        session_path = self.session_dir / session_id
        session_path.mkdir(exist_ok=True)
        
        # 创建会话文件
        session_info = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'history': [],
            'context': {}
        }
        
        with open(session_path / 'session.json', 'w') as f:
            json.dump(session_info, f, indent=2)
            
        print(f"✅ 会话已创建: {session_id}")
        return session_id
        
    def send_message(self, session_id: str, message: str) -> str:
        """向会话发送消息"""
        session_path = self.session_dir / session_id
        if not session_path.exists():
            return "错误: 会话不存在"
            
        # 加载会话
        session_file = session_path / 'session.json'
        lock_file = session_path / '.lock'
        
        # 获取文件锁
        with open(lock_file, 'w') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            
            try:
                # 读取会话历史
                with open(session_file, 'r') as f:
                    session_info = json.load(f)
                    
                history = session_info.get('history', [])
                
                # 构建带上下文的提示
                prompt = self._build_prompt_with_history(message, history)
                
                # 调用 Gemini
                response = self._call_gemini(prompt)
                
                # 更新历史
                history.append({
                    'timestamp': datetime.now().isoformat(),
                    'user': message,
                    'assistant': response
                })
                
                # 只保留最近的10条对话
                if len(history) > 10:
                    history = history[-10:]
                    
                session_info['history'] = history
                session_info['last_activity'] = datetime.now().isoformat()
                
                # 保存会话
                with open(session_file, 'w') as f:
                    json.dump(session_info, f, indent=2)
                    
                return response
                
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                
    def _build_prompt_with_history(self, message: str, history: list) -> str:
        """构建包含历史的提示"""
        if not history:
            return message
            
        prompt_parts = ["基于以下对话历史：\n"]
        
        # 添加最近的5条对话
        recent_history = history[-5:]
        for item in recent_history:
            prompt_parts.append(f"用户: {item['user']}")
            # 限制历史响应的长度
            assistant_response = item['assistant']
            if len(assistant_response) > 200:
                assistant_response = assistant_response[:200] + "..."
            prompt_parts.append(f"助手: {assistant_response}\n")
            
        prompt_parts.append(f"当前问题: {message}")
        return "\n".join(prompt_parts)
        
    def _call_gemini(self, prompt: str) -> str:
        """调用 Gemini CLI"""
        try:
            result = subprocess.run(
                ['gemini', '-c', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except Exception as e:
            return f"错误: {str(e)}"
            
    def list_sessions(self):
        """列出所有会话"""
        sessions = []
        for session_dir in self.session_dir.iterdir():
            if session_dir.is_dir():
                session_file = session_dir / 'session.json'
                if session_file.exists():
                    with open(session_file, 'r') as f:
                        info = json.load(f)
                        sessions.append({
                            'id': info['id'],
                            'created_at': info['created_at'],
                            'last_activity': info.get('last_activity', 'N/A'),
                            'message_count': len(info.get('history', []))
                        })
        return sessions
        
    def get_session_history(self, session_id: str):
        """获取会话历史"""
        session_path = self.session_dir / session_id / 'session.json'
        if not session_path.exists():
            return None
            
        with open(session_path, 'r') as f:
            session_info = json.load(f)
            
        return session_info.get('history', [])
        
    def delete_session(self, session_id: str):
        """删除会话"""
        session_path = self.session_dir / session_id
        if session_path.exists():
            import shutil
            shutil.rmtree(session_path)
            print(f"✅ 会话已删除: {session_id}")
            

class GeminiDaemon:
    """Gemini CLI 守护进程"""
    
    def __init__(self):
        self.pid_file = Path("/tmp/gemini_daemon.pid")
        self.log_file = Path("/tmp/gemini_daemon.log")
        
    def start(self):
        """启动守护进程"""
        # 检查是否已经运行
        if self.is_running():
            print("⚠️  守护进程已经在运行")
            return
            
        # Fork 进程
        pid = os.fork()
        if pid > 0:
            # 父进程退出
            print(f"✅ Gemini 守护进程已启动 (PID: {pid})")
            sys.exit(0)
            
        # 子进程继续
        # 创建新会话
        os.setsid()
        
        # 再次 fork
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
            
        # 守护进程主体
        self._run_daemon()
        
    def _run_daemon(self):
        """运行守护进程"""
        # 保存 PID
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
        # 重定向标准输入输出
        with open(self.log_file, 'a') as log:
            sys.stdout = log
            sys.stderr = log
            
            print(f"\n[{datetime.now()}] 守护进程启动")
            
            # 主循环
            session_manager = GeminiSessionManager()
            
            while True:
                try:
                    # 清理超过1小时没有活动的会话
                    self._cleanup_old_sessions(session_manager)
                    
                    # 睡眠
                    time.sleep(60)  # 每分钟检查一次
                    
                except Exception as e:
                    print(f"[{datetime.now()}] 错误: {e}")
                    
    def _cleanup_old_sessions(self, session_manager):
        """清理旧会话"""
        current_time = datetime.now()
        for session in session_manager.list_sessions():
            last_activity = session.get('last_activity', session['created_at'])
            if last_activity != 'N/A':
                last_time = datetime.fromisoformat(last_activity)
                if (current_time - last_time).seconds > 3600:  # 1小时
                    session_manager.delete_session(session['id'])
                    print(f"[{current_time}] 清理会话: {session['id']}")
                    
    def stop(self):
        """停止守护进程"""
        if not self.is_running():
            print("⚠️  守护进程未运行")
            return
            
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())
            
        try:
            os.kill(pid, signal.SIGTERM)
            os.unlink(self.pid_file)
            print("✅ 守护进程已停止")
        except:
            print("❌ 无法停止守护进程")
            
    def is_running(self):
        """检查守护进程是否运行"""
        if not self.pid_file.exists():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return True
        except:
            return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Gemini CLI 会话管理器")
        print("")
        print("会话管理:")
        print("  python gemini_session_manager.py create [session_id]")
        print("  python gemini_session_manager.py send <session_id> '消息'")
        print("  python gemini_session_manager.py list")
        print("  python gemini_session_manager.py history <session_id>")
        print("  python gemini_session_manager.py delete <session_id>")
        print("")
        print("守护进程:")
        print("  python gemini_session_manager.py daemon start")
        print("  python gemini_session_manager.py daemon stop")
        print("")
        print("交互模式:")
        print("  python gemini_session_manager.py chat [session_id]")
        return
        
    command = sys.argv[1]
    manager = GeminiSessionManager()
    
    if command == "create":
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        manager.create_session(session_id)
        
    elif command == "send":
        if len(sys.argv) < 4:
            print("用法: send <session_id> '消息'")
            return
            
        session_id = sys.argv[2]
        message = sys.argv[3]
        
        print(f"发送: {message}")
        response = manager.send_message(session_id, message)
        print(f"响应: {response}")
        
    elif command == "list":
        sessions = manager.list_sessions()
        if not sessions:
            print("没有活动会话")
        else:
            print("活动会话:")
            for session in sessions:
                print(f"  - {session['id']}")
                print(f"    创建时间: {session['created_at']}")
                print(f"    最后活动: {session['last_activity']}")
                print(f"    消息数: {session['message_count']}")
                
    elif command == "history":
        if len(sys.argv) < 3:
            print("用法: history <session_id>")
            return
            
        session_id = sys.argv[2]
        history = manager.get_session_history(session_id)
        
        if not history:
            print("没有历史记录")
        else:
            print(f"会话 {session_id} 的历史:")
            for item in history:
                print(f"\n[{item['timestamp']}]")
                print(f"用户: {item['user']}")
                print(f"助手: {item['assistant'][:200]}...")
                
    elif command == "delete":
        if len(sys.argv) < 3:
            print("用法: delete <session_id>")
            return
            
        session_id = sys.argv[2]
        manager.delete_session(session_id)
        
    elif command == "daemon":
        if len(sys.argv) < 3:
            print("用法: daemon start|stop")
            return
            
        daemon = GeminiDaemon()
        if sys.argv[2] == "start":
            daemon.start()
        elif sys.argv[2] == "stop":
            daemon.stop()
            
    elif command == "chat":
        # 交互式聊天模式
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not session_id:
            session_id = manager.create_session()
            
        print(f"进入聊天模式 (会话: {session_id})")
        print("输入 'exit' 退出\n")
        
        while True:
            try:
                message = input("你: ")
                if message.lower() == 'exit':
                    break
                    
                response = manager.send_message(session_id, message)
                print(f"Gemini: {response}\n")
                
            except KeyboardInterrupt:
                break
                
        print("\n再见!")
        
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()