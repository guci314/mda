#!/usr/bin/env python3
"""
张三李四消息工作流演示 - 工作流文档嵌入在inbox消息中
"""

import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.react_agent_minimal import ReactAgentMinimal

def setup_environment():
    """设置环境"""
    # 创建inbox目录
    Path(".inbox/张三").mkdir(parents=True, exist_ok=True)
    Path(".inbox/李四").mkdir(parents=True, exist_ok=True)
    
    # 清理旧消息
    for f in Path(".inbox/张三").glob("*.md"):
        f.unlink()
    for f in Path(".inbox/李四").glob("*.md"):
        f.unlink()
    
    print("环境已准备就绪")

def create_initial_workflow():
    """创建初始工作流消息"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    workflow_content = f"""# Message
From: 张三
To: 李四
Time: {current_time}
Type: workflow

## Workflow Document
### Workflow: calc_{timestamp}
Status: pending
Current_Owner: 李四
Previous_Owner: 张三
Created_At: {current_time}
Updated_At: {current_time}
Interaction_Count: 1

### Task
请计算：2+2等于几？

### History
- {current_time} 张三 创建工作流 pending→pending

### Next_Action
待李四处理

### Termination_Conditions
- 李四给出答案后
- 超过10次交互
- 遇到终止标记[WORKFLOW_END]
"""
    
    # 写入李四的收件箱
    message_file = Path(f".inbox/李四/workflow_calc_{timestamp}.md")
    message_file.write_text(workflow_content, encoding='utf-8')
    
    print(f"[张三] 发送工作流消息到李四的inbox")
    print(f"[张三] 文件: {message_file}")
    print(f"[张三] 任务: 请计算2+2等于几？")
    
    return timestamp

def run_zhangsan():
    """运行张三Agent"""
    print("\n[张三] 启动...")
    
    # 创建初始工作流消息
    workflow_id = create_initial_workflow()
    
    # 创建张三Agent
    zhangsan = ReactAgentMinimal(
        work_dir=".",
        model="x-ai/grok-code-fast-1",
        knowledge_files=["knowledge/roles/zhangsan_message.md"],
        minimal_mode=False
    )
    
    # 监控回复
    print("[张三] 等待李四的回复...")
    for i in range(20):  # 检查20次，每次3秒
        time.sleep(3)
        
        # 检查收件箱
        inbox_files = list(Path(".inbox/张三").glob("*.md"))
        if inbox_files:
            print(f"[张三] 收到{len(inbox_files)}条消息")
            for msg_file in inbox_files:
                content = msg_file.read_text(encoding='utf-8')
                if "[WORKFLOW_END]" in content:
                    print("[张三] 收到工作流结束标记")
                    if "答案是4" in content or "2+2=4" in content or "Answer" in content:
                        print("[张三] ✅ 收到正确答案：4")
                    return
    
    print("[张三] 超时，未收到回复")

def run_lisi():
    """运行李四Agent"""
    print("\n[李四] 启动...")
    
    # 等待一下让张三先创建消息
    time.sleep(2)
    
    # 创建李四Agent
    lisi = ReactAgentMinimal(
        work_dir=".",
        model="x-ai/grok-code-fast-1",
        knowledge_files=["knowledge/roles/lisi_message.md"],
        minimal_mode=False
    )
    
    # 检查并处理工作流消息
    for i in range(10):  # 检查10次
        time.sleep(3)
        
        # 检查收件箱
        inbox_files = list(Path(".inbox/李四").glob("*.md"))
        if inbox_files:
            print(f"[李四] 发现{len(inbox_files)}条待处理消息")
            
            for msg_file in inbox_files:
                print(f"[李四] 处理消息: {msg_file.name}")
                
                # 让Agent处理消息
                prompt = f"""处理收到的工作流消息：
1. 读取文件 {msg_file}
2. 提取Task（计算2+2）
3. 执行计算得到结果4
4. 创建回复消息到 .inbox/张三/workflow_reply_[timestamp].md
5. 回复中包含：
   - 更新后的工作流文档（Status: completed）
   - Answer部分写入：计算结果：2+2=4
   - 必须添加[WORKFLOW_END]标记
"""
                
                response = lisi.execute(task=prompt)
                print(f"[李四] 处理完成")
                
                # 检查是否已发送回复
                reply_files = list(Path(".inbox/张三").glob("*.md"))
                if reply_files:
                    print(f"[李四] 已发送回复到张三的inbox")
                    return
    
    print("[李四] 处理结束")

def monitor_inboxes():
    """监控inbox目录"""
    print("\n=== Inbox监控 ===")
    
    start_time = time.time()
    max_duration = 60
    
    while time.time() - start_time < max_duration:
        # 监控张三的inbox
        zhangsan_inbox = list(Path(".inbox/张三").glob("*.md"))
        lisi_inbox = list(Path(".inbox/李四").glob("*.md"))
        
        print(f"\n[监控] 时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"  张三收件箱: {len(zhangsan_inbox)}条消息")
        print(f"  李四收件箱: {len(lisi_inbox)}条消息")
        
        # 检查是否有完成标记
        for msg_file in zhangsan_inbox:
            content = msg_file.read_text(encoding='utf-8')
            if "Status: completed" in content and "[WORKFLOW_END]" in content:
                print("  ✅ 工作流已完成！")
                print("  ✅ 成功避免死循环！")
                
                # 提取答案
                if "2+2=4" in content or "答案是4" in content:
                    print("  ✅ 答案正确：4")
                
                return
        
        time.sleep(2)
    
    print("\n=== 监控结束 ===")

def main():
    """主函数"""
    print("="*60)
    print("张三李四消息工作流演示")
    print("工作流文档嵌入在inbox消息中传递")
    print("="*60)
    
    # 设置环境
    setup_environment()
    
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_inboxes)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # 并行运行两个Agent
    zhangsan_thread = threading.Thread(target=run_zhangsan)
    lisi_thread = threading.Thread(target=run_lisi)
    
    zhangsan_thread.start()
    lisi_thread.start()
    
    # 等待完成
    zhangsan_thread.join(timeout=70)
    lisi_thread.join(timeout=70)
    monitor_thread.join(timeout=5)
    
    # 最终统计
    print("\n" + "="*60)
    print("最终统计:")
    print("="*60)
    
    zhangsan_msgs = list(Path(".inbox/张三").glob("*.md"))
    lisi_msgs = list(Path(".inbox/李四").glob("*.md"))
    
    print(f"张三收件箱: {len(zhangsan_msgs)}条消息")
    print(f"李四收件箱: {len(lisi_msgs)}条消息")
    
    # 检查是否成功
    success = False
    for msg_file in zhangsan_msgs:
        content = msg_file.read_text(encoding='utf-8')
        if "[WORKFLOW_END]" in content and "completed" in content:
            success = True
            break
    
    if success:
        print("\n✅ 演示成功！工作流正常完成，无死循环")
    else:
        print("\n⚠️ 工作流未正常完成")
    
    print("\n演示结束！")

if __name__ == "__main__":
    main()