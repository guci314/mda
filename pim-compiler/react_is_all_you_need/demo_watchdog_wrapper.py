#!/usr/bin/env python3
"""
WatchdogWrapper演示
展示如何使用WatchdogWrapper创建事件驱动的Agent服务
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core.watchdog_wrapper import WatchdogWrapper, MultiAgentWatchdog


def demo_single_agent():
    """单个Agent演示"""
    print("="*60)
    print("单个Agent演示（李四）")
    print("="*60)
    
    # 创建李四Agent服务（使用存在的知识文件）
    lisi = WatchdogWrapper(
        agent_name="李四",
        model="x-ai/grok-code-fast-1",
        knowledge_files=[]  # 不依赖特定知识文件
    )
    
    try:
        # 模拟发送消息
        time.sleep(2)
        print("\n模拟张三发送消息...")
        # 注意：这里应该是从张三发给李四
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = Path(".inbox/李四") / f"msg_{timestamp}.md"
        msg_file.parent.mkdir(parents=True, exist_ok=True)
        msg_file.write_text("""From: 张三
To: 李四
Content: 2+2等于几？""")
        print(f"📤 消息已发送到李四")
        
        # 等待处理
        time.sleep(5)
        
        # 再发一条
        print("\n模拟王五发送消息...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = Path(".inbox/李四") / f"msg_{timestamp}_2.md"
        msg_file.write_text("""From: 王五
To: 李四
Content: 10-3等于几？""")
        print(f"📤 消息已发送到李四")
        
        # 等待
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        lisi.stop()


def demo_multi_agent():
    """多Agent演示"""
    print("="*60)
    print("多Agent协作演示")
    print("="*60)
    
    # 使用上下文管理器自动管理生命周期
    with MultiAgentWatchdog() as manager:
        # 添加多个Agent（不依赖特定知识文件）
        print("\n添加Agent...")
        manager.add_agent("秘书", knowledge_files=[])
        manager.add_agent("程序员", knowledge_files=[])
        manager.add_agent("测试员", knowledge_files=[])
        print(f"已添加 {len(manager.agents)} 个Agent")
        
        # 手动启动所有Agent
        manager.start_all()
        
        # 模拟消息交互
        time.sleep(2)
        
        print("\n📝 老板发送任务给秘书...")
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = Path(".inbox/秘书") / f"msg_{timestamp}.md"
        msg_file.parent.mkdir(parents=True, exist_ok=True)
        msg_file.write_text("""From: 老板
To: 秘书
Content: 请帮我安排一个计算器程序的开发任务""")
        
        # 等待秘书处理
        time.sleep(8)
        
        print("\n📝 秘书分配任务给程序员...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = Path(".inbox/程序员") / f"msg_{timestamp}.md"
        msg_file.write_text("""From: 秘书
To: 程序员
Content: 请实现一个简单的add(a, b)函数""")
        
        # 等待程序员处理
        time.sleep(8)
        
        print("\n📝 程序员提交代码给测试员...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = Path(".inbox/测试员") / f"msg_{timestamp}.md"
        msg_file.write_text("""From: 程序员
To: 测试员
Content: 已完成add函数，请测试：def add(a, b): return a + b""")
        
        # 等待测试员处理
        time.sleep(8)
        
    # 退出with块时自动停止所有Agent并打印统计


def demo_custom_handler():
    """自定义消息处理器演示"""
    print("="*60)
    print("自定义消息处理器演示")
    print("="*60)
    
    # 定义自定义处理器（不调用LLM）
    def math_calculator(msg_path: str):
        """简单的数学计算器（不调用LLM）"""
        content = Path(msg_path).read_text()
        
        # 简单解析
        if "2+2" in content:
            answer = "4"
        elif "10-3" in content:
            answer = "7"
        elif "3*5" in content:
            answer = "15"
        else:
            answer = "不知道"
        
        # 提取发送者
        sender = "unknown"
        for line in content.split('\n'):
            if line.startswith("From:"):
                sender = line.replace("From:", "").strip()
                break
        
        # 创建回复
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reply_path = Path(".inbox") / sender / f"reply_{timestamp}.md"
        reply_path.parent.mkdir(parents=True, exist_ok=True)
        reply_path.write_text(f"""From: 计算器
To: {sender}
Answer: {answer}
Note: 这是自定义处理器，没有调用LLM
""")
        
        # 删除原消息
        Path(msg_path).unlink()
        
        print(f"   📊 计算完成: {answer} (0 API调用)")
        return answer
    
    # 创建Agent并设置自定义处理器
    calculator = WatchdogWrapper(
        agent_name="计算器",
        model="x-ai/grok-code-fast-1"  # 实际不会用到
    )
    calculator.set_message_handler(math_calculator)
    
    try:
        # 发送测试消息
        time.sleep(1)
        print("\n发送计算请求...")
        from datetime import datetime
        
        # 发送2+2
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = Path(".inbox/计算器") / f"msg_{timestamp}_1.md"
        msg_file.parent.mkdir(parents=True, exist_ok=True)
        msg_file.write_text("""From: 用户
To: 计算器
Content: 2+2是多少？""")
        print("📤 发送: 2+2是多少？")
        
        time.sleep(2)
        
        # 发送3*5
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = Path(".inbox/计算器") / f"msg_{timestamp}_2.md"
        msg_file.write_text("""From: 用户
To: 计算器
Content: 3*5是多少？""")
        print("📤 发送: 3*5是多少？")
        
        time.sleep(2)
        
    finally:
        calculator.stop()


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python demo_watchdog_wrapper.py single   # 单Agent演示")
        print("  python demo_watchdog_wrapper.py multi    # 多Agent演示")
        print("  python demo_watchdog_wrapper.py custom   # 自定义处理器演示")
        print("  python demo_watchdog_wrapper.py clean    # 清理")
        return
    
    mode = sys.argv[1]
    
    try:
        if mode == "single":
            demo_single_agent()
        elif mode == "multi":
            demo_multi_agent()
        elif mode == "custom":
            demo_custom_handler()
        elif mode == "clean":
            print("清理inbox目录...")
            import shutil
            if Path(".inbox").exists():
                shutil.rmtree(".inbox")
            print("清理完成！")
        else:
            print(f"未知模式: {mode}")
    except ImportError as e:
        print(f"错误: 缺少依赖 - {e}")
        print("请安装: pip install watchdog")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()