#!/usr/bin/env python3
"""
WatchdogWrapper: 事件驱动的Agent包装器
让Agent只在有消息时被唤醒，实现0成本空闲
"""

import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from .react_agent_minimal import ReactAgentMinimal


class WatchdogWrapper(FileSystemEventHandler):
    """
    使用Watchdog包装Agent，实现事件驱动的异步消息处理
    
    特点：
    1. 空闲时0 API调用
    2. 即时响应（<100ms）
    3. 支持多Agent并发
    4. 自动消息路由
    """
    
    def __init__(
        self,
        agent_name: str,
        model: str = "x-ai/grok-code-fast-1",
        knowledge_files: list = None,
        inbox_dir: str = ".inbox",
        auto_start: bool = True
    ):
        """
        初始化WatchdogWrapper
        
        Args:
            agent_name: Agent名称（也是inbox子目录名）
            model: LLM模型
            knowledge_files: 知识文件列表
            inbox_dir: inbox根目录
            auto_start: 是否自动启动监听
        """
        super().__init__()
        self.agent_name = agent_name
        self.model = model
        self.knowledge_files = knowledge_files or []
        self.inbox_path = Path(inbox_dir) / agent_name
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        
        # 监听器
        self.observer = Observer()
        self.is_running = False
        
        # 消息处理回调（可自定义）
        self.message_handler: Optional[Callable] = None
        
        # 统计信息
        self.stats = {
            "messages_received": 0,
            "messages_processed": 0,
            "total_api_calls": 0,
            "start_time": None
        }
        
        if auto_start:
            self.start()
    
    def on_created(self, event):
        """文件创建事件处理"""
        if event.is_directory:
            return
            
        if event.src_path.endswith('.md'):
            self.stats["messages_received"] += 1
            print(f"\n📨 [{self.agent_name}] 收到新消息: {Path(event.src_path).name}")
            
            # 在新线程中处理，避免阻塞监听
            thread = threading.Thread(
                target=self._process_message,
                args=(event.src_path,)
            )
            thread.start()
    
    def _process_message(self, msg_path: str):
        """处理单个消息"""
        try:
            # 如果有自定义处理器，使用它
            if self.message_handler:
                result = self.message_handler(msg_path)
            else:
                result = self._default_handler(msg_path)
            
            self.stats["messages_processed"] += 1
            try:
                print(f"✅ [{self.agent_name}] 消息处理完成")
            except:
                pass  # 忽略打印错误
            return result
            
        except Exception as e:
            try:
                print(f"❌ [{self.agent_name}] 处理失败: {e}")
            except:
                pass  # 忽略打印错误
            return None
    
    def _default_handler(self, msg_path: str):
        """默认消息处理器"""
        print(f"   唤醒 {self.agent_name} Agent...")
        
        # 创建Agent实例
        agent = ReactAgentMinimal(
            work_dir=".",
            model=self.model,
            knowledge_files=self.knowledge_files,
            minimal_mode=True
        )
        
        # 统计API调用
        self.stats["total_api_calls"] += 1
        
        # 构建任务
        task = f"""
        处理消息文件：{msg_path}
        
        步骤：
        1. 用read_file读取消息内容
        2. 提取发送者（From字段）和内容
        3. 根据内容生成回复
        4. 用write_file将回复写入发送者的inbox
        5. 用execute_command删除已处理的消息
        
        回复格式：
        From: {self.agent_name}
        To: [发送者]
        Time: [当前时间]
        Answer: [你的回复]
        """
        
        result = agent.execute(task=task)
        return result
    
    def set_message_handler(self, handler: Callable):
        """设置自定义消息处理器"""
        self.message_handler = handler
        return self
    
    def start(self):
        """启动监听服务"""
        if self.is_running:
            print(f"⚠️ [{self.agent_name}] 已在运行")
            return
        
        self.observer.schedule(self, str(self.inbox_path), recursive=False)
        self.observer.start()
        self.is_running = True
        self.stats["start_time"] = datetime.now()
        
        print(f"🚀 [{self.agent_name}] 监听服务启动")
        print(f"   📂 监听目录: {self.inbox_path}")
        print(f"   🤖 模型: {self.model}")
        print(f"   ✨ 等待消息中...")
    
    def stop(self):
        """停止监听服务"""
        if not self.is_running:
            return
        
        self.observer.stop()
        self.observer.join()
        self.is_running = False
        
        print(f"🛑 [{self.agent_name}] 监听服务停止")
        self.print_stats()
    
    def wait(self):
        """阻塞等待（保持服务运行）"""
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def send_message(self, to_agent: str, content: str):
        """发送消息给其他Agent"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        to_inbox = Path(".inbox") / to_agent
        to_inbox.mkdir(parents=True, exist_ok=True)
        
        msg_file = to_inbox / f"msg_{timestamp}.md"
        msg_file.write_text(f"""From: {self.agent_name}
To: {to_agent}
Time: {datetime.now()}

Content:
{content}
""")
        print(f"📤 [{self.agent_name}] → [{to_agent}]: {content[:50]}...")
        return msg_file
    
    def print_stats(self):
        """打印统计信息"""
        if self.stats["start_time"]:
            runtime = datetime.now() - self.stats["start_time"]
            print(f"\n📊 [{self.agent_name}] 统计信息:")
            print(f"   运行时间: {runtime}")
            print(f"   收到消息: {self.stats['messages_received']}")
            print(f"   处理消息: {self.stats['messages_processed']}")
            print(f"   API调用: {self.stats['total_api_calls']}")
            
            # 计算节省
            if runtime.total_seconds() > 0:
                # 假设轮询方式每秒1次API调用
                potential_calls = int(runtime.total_seconds())
                saved_calls = potential_calls - self.stats['total_api_calls']
                if saved_calls > 0:
                    print(f"   💰 节省API调用: {saved_calls} ({saved_calls/potential_calls*100:.1f}%)")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


class MultiAgentWatchdog:
    """管理多个WatchdogWrapper Agent"""
    
    def __init__(self):
        self.agents: Dict[str, WatchdogWrapper] = {}
    
    def add_agent(
        self,
        agent_name: str,
        model: str = "x-ai/grok-code-fast-1",
        knowledge_files: list = None,
        handler: Optional[Callable] = None
    ) -> WatchdogWrapper:
        """添加Agent"""
        if agent_name in self.agents:
            print(f"⚠️ Agent {agent_name} 已存在")
            return self.agents[agent_name]
        
        wrapper = WatchdogWrapper(
            agent_name=agent_name,
            model=model,
            knowledge_files=knowledge_files,
            auto_start=False
        )
        
        if handler:
            wrapper.set_message_handler(handler)
        
        self.agents[agent_name] = wrapper
        return wrapper
    
    def start_all(self):
        """启动所有Agent"""
        print("🚀 启动所有Agent...")
        for agent in self.agents.values():
            agent.start()
    
    def stop_all(self):
        """停止所有Agent"""
        print("🛑 停止所有Agent...")
        for agent in self.agents.values():
            agent.stop()
    
    def wait(self):
        """等待所有Agent"""
        try:
            while any(a.is_running for a in self.agents.values()):
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all()
    
    def print_all_stats(self):
        """打印所有Agent统计"""
        print("\n" + "="*60)
        print("📊 所有Agent统计")
        print("="*60)
        for agent in self.agents.values():
            agent.print_stats()
    
    def __enter__(self):
        """上下文管理器"""
        # 不在这里启动，让用户添加完Agent后手动启动或在exit时启动
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器"""
        self.stop_all()
        self.print_all_stats()


# 便捷函数
def create_agent_service(
    agent_name: str,
    model: str = "x-ai/grok-code-fast-1",
    knowledge_files: list = None
) -> WatchdogWrapper:
    """创建并启动Agent服务"""
    return WatchdogWrapper(
        agent_name=agent_name,
        model=model,
        knowledge_files=knowledge_files,
        auto_start=True
    )