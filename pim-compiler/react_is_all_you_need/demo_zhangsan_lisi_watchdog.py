#!/usr/bin/env python3
"""
终极经济版：使用watchdog监听文件系统事件
只在有消息时唤醒Agent，真正的0成本空闲
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sys.path.insert(0, str(Path(__file__).parent))
from core.react_agent_minimal import ReactAgentMinimal

class LisiInboxHandler(FileSystemEventHandler):
    """李四的inbox监听器"""
    
    def on_created(self, event):
        """当有新文件创建时"""
        if event.is_directory:
            return
            
        if event.src_path.endswith('.md'):
            print(f"\n📨 收到新消息: {event.src_path}")
            self.process_message(event.src_path)
    
    def process_message(self, msg_path):
        """处理消息 - 只在这时调用LLM"""
        print("唤醒李四Agent处理消息...")
        
        # 创建李四Agent
        lisi = ReactAgentMinimal(
            work_dir=".",
            model="x-ai/grok-code-fast-1",
            knowledge_files=["knowledge/roles/lisi.md"],
            minimal_mode=True
        )
        
        # 让李四处理这条消息
        task = f"""
        处理消息文件：{msg_path}
        1. 用read_file读取消息内容
        2. 提取发送者（From字段）和问题
        3. 计算答案（如2+2=4）
        4. 用write_file创建回复文件到发送者的inbox
        5. 用execute_command删除已处理的消息
        """
        
        result = lisi.execute(task=task)
        print(f"处理完成: {result[:100]}...")

def run_lisi_service():
    """运行李四监听服务"""
    print("李四监听服务启动（Watchdog模式）...")
    print("优势：")
    print("  ✅ 空闲时0 API调用")
    print("  ✅ 即时响应（事件驱动）")
    print("  ✅ 最小资源占用")
    print("\n等待消息中...\n")
    
    # 创建inbox目录
    inbox_path = Path(".inbox/李四")
    inbox_path.mkdir(parents=True, exist_ok=True)
    
    # 设置文件系统监听
    event_handler = LisiInboxHandler()
    observer = Observer()
    observer.schedule(event_handler, str(inbox_path), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)  # 主线程保持运行，但不消耗API
    except KeyboardInterrupt:
        observer.stop()
        print("\n服务停止")
    observer.join()

def run_zhangsan():
    """张三发送消息"""
    print("张三Agent启动...")
    
    Path(".inbox/李四").mkdir(parents=True, exist_ok=True)
    Path(".inbox/张三").mkdir(parents=True, exist_ok=True)
    
    zhangsan = ReactAgentMinimal(
        work_dir=".",
        model="x-ai/grok-code-fast-1",
        knowledge_files=["knowledge/roles/zhangsan.md"],
        minimal_mode=True
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    task = f'''
    发送消息给李四：
    1. 用write_file创建 .inbox/李四/msg_{timestamp}.md
       内容：
       From: 张三
       To: 李四
       Content: 2+2等于几？
    
    2. 等待回复（最多10秒）
       循环检查.inbox/张三/目录
       如果有reply_*.md文件，读取并显示
    '''
    
    result = zhangsan.execute(task=task)
    print(f"张三结果: {result[:200]}...")

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python demo_zhangsan_lisi_watchdog.py lisi    # 启动李四监听")
        print("  python demo_zhangsan_lisi_watchdog.py zhangsan # 张三发送消息")
        print("  python demo_zhangsan_lisi_watchdog.py clean    # 清理")
        print("\n需要安装: pip install watchdog")
        return
    
    mode = sys.argv[1]
    
    if mode == "lisi":
        print("="*60)
        print("李四Agent监听服务（Watchdog事件驱动）")
        print("="*60)
        run_lisi_service()
    elif mode == "zhangsan":
        print("="*60)
        print("张三Agent发送消息")
        print("="*60)
        run_zhangsan()
    elif mode == "clean":
        print("清理...")
        import shutil
        if Path(".inbox").exists():
            shutil.rmtree(".inbox")
        print("清理完成！")

if __name__ == "__main__":
    main()