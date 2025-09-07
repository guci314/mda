#!/usr/bin/env python3
"""
经济版异步Agent演示：使用shell脚本监听，减少API调用
"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from core.react_agent_minimal import ReactAgentMinimal

def run_lisi():
    """李四监听服务 - 经济版"""
    print("李四Agent启动（经济模式）...")
    
    lisi = ReactAgentMinimal(
        work_dir=".",
        model="x-ai/grok-code-fast-1",
        knowledge_files=["knowledge/roles/lisi.md"],
        minimal_mode=True
    )
    
    # 创建一个持续监听的shell脚本，只在有消息时调用Agent
    task = '''
作为李四，我需要创建一个高效的监听服务。

步骤：
1. 用write_file创建监听脚本 monitor_lisi.sh：
```bash
#!/bin/bash
echo "李四监听服务启动..."
mkdir -p .inbox/李四 .inbox/张三

while true; do
  # 检查消息
  messages=$(ls .inbox/李四/msg_*.md 2>/dev/null)
  
  if [ -n "$messages" ]; then
    for msg in $messages; do
      echo "发现消息: $msg"
      
      # 读取消息
      content=$(cat "$msg")
      sender=$(echo "$content" | grep "From:" | cut -d: -f2 | tr -d ' ')
      question=$(echo "$content" | grep -E "Content:|Question:" | cut -d: -f2-)
      
      # 计算答案
      if echo "$question" | grep -q "2+2"; then
        answer="4"
      elif echo "$question" | grep -q "3+5"; then
        answer="8"
      elif echo "$question" | grep -q "10-3"; then
        answer="7"
      else
        # 尝试用bc计算
        answer=$(echo "$question" | bc 2>/dev/null || echo "无法计算")
      fi
      
      # 创建回复
      timestamp=$(date +%s)
      mkdir -p ".inbox/$sender"
      cat > ".inbox/$sender/reply_$timestamp.md" << EOF
From: 李四
To: $sender
Time: $(date)
Answer: $answer
EOF
      
      echo "已回复给 $sender: $answer"
      
      # 删除已处理消息
      rm "$msg"
    done
  fi
  
  sleep 1
done
```

2. 用execute_command运行: chmod +x monitor_lisi.sh && ./monitor_lisi.sh

这样只需要2次API调用就能启动永久监听服务。
'''
    
    result = lisi.execute(task=task)
    print(f"李四监听脚本已启动: {result[:100]}...")

def run_zhangsan():
    """张三发送消息 - 保持不变"""
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
作为张三，发送消息并等待回复。

1. 用write_file创建 .inbox/李四/msg_{timestamp}.md：
   From: 张三
   To: 李四
   Content: 2+2等于几？
   
2. 用execute_command运行等待脚本：
```bash
for i in {{1..15}}; do
  if ls .inbox/张三/reply_*.md 2>/dev/null; then
    cat .inbox/张三/reply_*.md
    rm .inbox/张三/reply_*.md
    exit 0
  fi
  sleep 1
done
echo "超时：没有收到回复"
```
'''
    
    result = zhangsan.execute(task=task)
    print(f"张三结果: {result[:200]}...")

def stop_lisi():
    """停止李四监听服务"""
    import subprocess
    subprocess.run(["pkill", "-f", "monitor_lisi.sh"], capture_output=True)
    print("李四监听服务已停止")

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python demo_zhangsan_lisi_economic.py lisi    # 启动李四监听")
        print("  python demo_zhangsan_lisi_economic.py zhangsan # 张三发送消息")
        print("  python demo_zhangsan_lisi_economic.py stop     # 停止李四服务")
        print("  python demo_zhangsan_lisi_economic.py clean    # 清理")
        return
    
    mode = sys.argv[1]
    
    if mode == "lisi":
        print("="*60)
        print("李四Agent监听服务（经济模式）")
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
        if Path("monitor_lisi.sh").exists():
            Path("monitor_lisi.sh").unlink()
        print("清理完成！")
    else:
        print(f"未知模式: {mode}")

if __name__ == "__main__":
    main()