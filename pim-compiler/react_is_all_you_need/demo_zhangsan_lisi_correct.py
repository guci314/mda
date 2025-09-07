#!/usr/bin/env python3
"""
正确的经济版：Shell只负责监听，发现消息时调用李四Agent处理
"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from core.react_agent_minimal import ReactAgentMinimal

def run_lisi():
    """李四监听服务 - 正确的经济版"""
    print("李四Agent启动（正确经济模式）...")
    
    lisi = ReactAgentMinimal(
        work_dir=".",
        model="x-ai/grok-code-fast-1",
        knowledge_files=["knowledge/roles/lisi.md"],
        minimal_mode=True
    )
    
    # Shell只负责监听，发现消息时调用Python处理
    task = '''
作为李四，创建一个监听服务，当有消息时真正调用我来处理。

用write_file创建 monitor_lisi.py：
```python
#!/usr/bin/env python3
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from core.react_agent_minimal import ReactAgentMinimal

print("李四监听服务启动...")
Path(".inbox/李四").mkdir(parents=True, exist_ok=True)

while True:
    inbox = Path(".inbox/李四")
    messages = list(inbox.glob("msg_*.md"))
    
    if messages:
        print(f"发现{len(messages)}条消息，唤醒李四Agent处理...")
        
        # 创建李四Agent
        lisi = ReactAgentMinimal(
            work_dir=".",
            model="x-ai/grok-code-fast-1",
            knowledge_files=["knowledge/roles/lisi.md"],
            minimal_mode=True
        )
        
        # 让李四处理所有消息
        task = f"""
        检查.inbox/李四/目录下的所有消息文件。
        对每个消息：
        1. 用read_file读取内容
        2. 提取发送者和问题
        3. 计算答案（如2+2=4）
        4. 用write_file回复到发送者的inbox
        5. 用execute_command删除已处理的消息
        
        当前有{len(messages)}条消息需要处理。
        """
        
        result = lisi.execute(task=task)
        print(f"李四处理完成: {result[:50]}...")
    
    time.sleep(1)  # Shell层的等待，不消耗API
```

然后用execute_command运行: python monitor_lisi.py
'''
    
    result = lisi.execute(task=task)
    print(f"监听服务创建完成: {result[:100]}...")

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
作为张三，我需要：
1. 用write_file创建消息 .inbox/李四/msg_{timestamp}.md：
   From: 张三
   To: 李四
   Content: 2+2等于几？

2. 等待回复（最多15秒）
   循环用execute_command检查: ls .inbox/张三/reply_*.md
   如果有回复，用read_file读取并显示
'''
    
    result = zhangsan.execute(task=task)
    print(f"张三结果: {result[:200]}...")

def stop_lisi():
    """停止李四监听服务"""
    import subprocess
    subprocess.run(["pkill", "-f", "monitor_lisi.py"], capture_output=True)
    print("李四监听服务已停止")

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python demo_zhangsan_lisi_correct.py lisi    # 启动李四监听")
        print("  python demo_zhangsan_lisi_correct.py zhangsan # 张三发送消息")
        print("  python demo_zhangsan_lisi_correct.py stop     # 停止服务")
        print("  python demo_zhangsan_lisi_correct.py clean    # 清理")
        return
    
    mode = sys.argv[1]
    
    if mode == "lisi":
        print("="*60)
        print("李四Agent监听服务（正确经济模式）")
        print("="*60)
        run_lisi()
    elif mode == "zhangsan":
        print("="*60)
        print("张三Agent发送消息")
        print("="*60)
        run_zhangsan()
    elif mode == "stop":
        stop_lisi()
    elif mode == "clean":
        print("清理...")
        import shutil
        if Path(".inbox").exists():
            shutil.rmtree(".inbox")
        if Path("monitor_lisi.py").exists():
            Path("monitor_lisi.py").unlink()
        print("清理完成！")

if __name__ == "__main__":
    main()