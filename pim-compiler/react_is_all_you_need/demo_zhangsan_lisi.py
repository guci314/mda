#!/usr/bin/env python3
"""
简单异步Agent演示：张三问李四
分两步运行：先启动李四监听，再运行张三发送
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from core.react_agent_minimal import ReactAgentMinimal

def run_lisi():
    """运行李四Agent监听服务"""
    print("李四Agent启动...")
    
    # 创建李四Agent
    lisi = ReactAgentMinimal(
        work_dir=".",
        model="x-ai/grok-code-fast-1",
        knowledge_files=["knowledge/roles/lisi.md"],
        minimal_mode=True
    )
    
    # 李四的任务：监听并回复（永不退出）
    task = '''
作为李四，我需要持续监听inbox并回答数学问题，永不退出。

具体步骤：
1. 无限循环监听（while true）
2. 每秒用execute_command执行: ls .inbox/李四/ 2>/dev/null
3. 如果发现msg_*.md文件：
   - 用read_file读取每个消息
   - 提取发送者和问题内容
   - 根据问题计算答案：
     * 如果包含"2+2"，答案是4
     * 如果包含其他数学运算，尝试计算
   - 用write_file创建回复文件 .inbox/[发送者]/reply_[时间戳].md
   - 内容格式：
     From: 李四
     To: [发送者]
     Answer: [答案]
   - 用execute_command删除已处理的消息: rm .inbox/李四/msg_*.md
   - 继续监听下一个消息（不退出循环）
4. 如果没有消息，等待1秒后继续监听
5. 永远不退出，持续服务

开始持续监听服务...
'''
    
    result = lisi.execute(task=task)
    print(f"李四Agent结束: {result[:100]}...")

def run_zhangsan():
    """运行张三Agent发送消息"""
    print("张三Agent启动...")
    
    # 创建目录
    Path(".inbox/李四").mkdir(parents=True, exist_ok=True)
    Path(".inbox/张三").mkdir(parents=True, exist_ok=True)
    
    # 创建张三Agent
    zhangsan = ReactAgentMinimal(
        work_dir=".",
        model="x-ai/grok-code-fast-1",
        knowledge_files=["knowledge/roles/zhangsan.md"],
        minimal_mode=True
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 张三的任务：发送消息并等待回复
    task = f'''
作为张三，我需要发送问题并等待回复。

具体步骤：
1. 用write_file创建消息文件 .inbox/李四/msg_{timestamp}.md
   内容：
   From: 张三
   To: 李四
   Content: 2+2等于几？
   
2. 等待回复，循环15次，每次间隔2秒：
   - 用execute_command执行: ls .inbox/张三/ 2>/dev/null
   - 如果发现reply_*.md文件：
     - 用read_file读取回复
     - 显示答案
     - 退出循环

开始执行...
'''
    
    result = zhangsan.execute(task=task)
    print(f"张三Agent结束: {result[:200]}...")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python demo_zhangsan_lisi.py lisi    # 启动李四监听")
        print("  python demo_zhangsan_lisi.py zhangsan # 张三发送消息")
        print("  python demo_zhangsan_lisi.py clean    # 清理inbox")
        return
    
    mode = sys.argv[1]
    
    if mode == "lisi":
        print("="*60)
        print("李四Agent监听服务")
        print("="*60)
        run_lisi()
    elif mode == "zhangsan":
        print("="*60)
        print("张三Agent发送消息")
        print("="*60)
        run_zhangsan()
    elif mode == "clean":
        print("清理inbox目录...")
        import shutil
        if Path(".inbox").exists():
            shutil.rmtree(".inbox")
        print("清理完成！")
    else:
        print(f"未知模式: {mode}")

if __name__ == "__main__":
    main()