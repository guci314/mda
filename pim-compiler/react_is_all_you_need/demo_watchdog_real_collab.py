#!/usr/bin/env python3
"""
真正的Agent协作演示
Agent们会主动协作，而不是被动响应
"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from core.watchdog_wrapper import WatchdogWrapper, MultiAgentWatchdog


def demo_real_collaboration():
    """真正的Agent协作"""
    print("="*60)
    print("真正的Agent协作演示")
    print("="*60)
    
    with MultiAgentWatchdog() as manager:
        # 添加Agent
        print("\n添加协作Agent...")
        
        # 秘书Agent - 知道要分配任务
        secretary = manager.add_agent("秘书", knowledge_files=[])
        
        # 程序员Agent - 知道要提交代码
        coder = manager.add_agent("程序员", knowledge_files=[])
        
        # 测试员Agent - 知道要测试代码
        tester = manager.add_agent("测试员", knowledge_files=[])
        
        print(f"已添加 {len(manager.agents)} 个Agent")
        
        # 启动所有Agent
        manager.start_all()
        
        # 给秘书一个包含协作指令的任务
        print("\n📝 老板发送协作任务给秘书...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = Path(".inbox/秘书") / f"msg_{timestamp}.md"
        msg_file.parent.mkdir(parents=True, exist_ok=True)
        msg_file.write_text(f"""From: 老板
To: 秘书
Time: {datetime.now()}

Content: 
请帮我安排一个计算器程序的开发任务。
具体要求：
1. 让程序员实现一个add(a,b)函数
2. 让测试员测试这个函数
3. 协调他们的工作

注意：你需要主动发消息给程序员（.inbox/程序员/），让他们知道任务。
""")
        
        # 等待协作完成
        print("\n等待Agent们自主协作...")
        for i in range(30):
            time.sleep(1)
            print(".", end="", flush=True)
            
            # 检查是否有结果
            if Path(".inbox/老板").exists():
                results = list(Path(".inbox/老板").glob("*.md"))
                if len(results) >= 2:  # 期待至少2个回复
                    print("\n✅ 协作完成！")
                    for result in results:
                        print(f"\n收到: {result.name}")
                        print(result.read_text()[:200])
                    break
        
        print("\n" + "="*40)


def demo_with_knowledge():
    """使用知识文件指导协作"""
    print("="*60)
    print("知识驱动的Agent协作")
    print("="*60)
    
    # 先创建协作知识文件
    print("\n创建协作知识文件...")
    
    # 秘书知识
    secretary_knowledge = Path("knowledge/collab/secretary_collab.md")
    secretary_knowledge.parent.mkdir(parents=True, exist_ok=True)
    secretary_knowledge.write_text("""# 秘书协作知识

## 角色定位
我是秘书，负责任务分配和协调。

## 重要：处理消息时的步骤
1. 读取消息内容
2. 回复发送者确认收到
3. **主动分配任务给其他Agent**（这是关键！）
4. 删除已处理的消息

## 具体操作
当收到关于"计算器程序"或"add函数"的任务时：
1. 用write_file创建 .inbox/老板/reply_[时间].md 回复老板
2. **用write_file创建 .inbox/程序员/msg_[时间].md 分配任务给程序员**
   内容示例：
   From: 秘书
   To: 程序员
   Content: 请实现一个add(a, b)函数
3. 删除原消息

记住：你必须主动发消息给程序员，不要只回复老板！
""")
    
    # 程序员知识
    coder_knowledge = Path("knowledge/collab/coder_collab.md")
    coder_knowledge.write_text("""# 程序员协作知识

## 角色定位
我是程序员，负责代码实现。

## 重要：处理消息时的步骤
1. 读取任务消息
2. 实现代码
3. **主动发送代码给测试员**（关键！）
4. 回复秘书完成状态
5. 删除已处理的消息

## 具体操作
当收到"add函数"任务时：
1. 实现代码：def add(a, b): return a + b
2. **用write_file创建 .inbox/测试员/msg_[时间].md 发送给测试员**
   内容示例：
   From: 程序员
   To: 测试员
   Content: 已完成add函数，请测试：def add(a, b): return a + b
3. 用write_file创建 .inbox/秘书/reply_[时间].md 回复秘书
4. 删除原消息

记住：你必须主动发代码给测试员！
""")
    
    # 测试员知识
    tester_knowledge = Path("knowledge/collab/tester_collab.md")
    tester_knowledge.write_text("""# 测试员协作知识

## 角色定位
我是测试员，负责代码测试。

## 协作规则
1. 收到代码时，执行测试
2. 将测试结果反馈给程序员和秘书

## 测试反馈模板
测试完成后：
- 发送给程序员：.inbox/程序员/msg_[时间].md
  内容：测试结果：[通过/失败]
- 发送给秘书：.inbox/秘书/msg_[时间].md
  内容：[功能]测试[通过/失败]
""")
    
    # 使用知识文件创建Agent
    with MultiAgentWatchdog() as manager:
        print("\n添加知识驱动的Agent...")
        
        manager.add_agent(
            "秘书",
            knowledge_files=["collab/secretary_collab.md"]  # 不要knowledge/前缀
        )
        manager.add_agent(
            "程序员", 
            knowledge_files=["collab/coder_collab.md"]
        )
        manager.add_agent(
            "测试员",
            knowledge_files=["collab/tester_collab.md"]
        )
        
        print(f"已添加 {len(manager.agents)} 个Agent（带协作知识）")
        
        # 启动
        manager.start_all()
        
        # 发送初始任务
        print("\n📝 发送任务给秘书...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = Path(".inbox/秘书") / f"msg_{timestamp}.md"
        msg_file.parent.mkdir(parents=True, exist_ok=True)
        msg_file.write_text(f"""From: 老板
To: 秘书
Time: {datetime.now()}
Content: 请安排开发一个计算器程序，需要add函数
""")
        
        # 永远运行，直到Ctrl+C
        print("\n等待知识驱动的自主协作...")
        print("按 Ctrl+C 停止服务\n")
        
        try:
            while True:
                time.sleep(1)
                # 可以在这里添加状态检查
        except KeyboardInterrupt:
            print("\n\n用户中断，正在停止...")


def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python demo_watchdog_real_collab.py real    # 真正的协作")
        print("  python demo_watchdog_real_collab.py know    # 知识驱动协作")
        print("  python demo_watchdog_real_collab.py clean   # 清理")
        return
    
    mode = sys.argv[1]
    
    try:
        if mode == "real":
            demo_real_collaboration()
        elif mode == "know":
            demo_with_knowledge()
        elif mode == "clean":
            print("清理...")
            import shutil
            if Path(".inbox").exists():
                shutil.rmtree(".inbox")
            if Path("knowledge/collab").exists():
                shutil.rmtree("knowledge/collab")
            print("清理完成！")
        else:
            print(f"未知模式: {mode}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()