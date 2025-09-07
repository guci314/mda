#!/usr/bin/env python3
"""
最简单的WatchdogWrapper使用示例
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core.watchdog_wrapper import WatchdogWrapper


def main():
    print("="*60)
    print("WatchdogWrapper 最简单演示")
    print("="*60)
    
    # 一行代码创建Agent服务
    with WatchdogWrapper("李四", model="x-ai/grok-code-fast-1") as lisi:
        
        # 发送测试消息
        print("\n发送消息测试...")
        lisi.send_message("李四", "2+2等于几？")
        
        # 等待处理
        print("等待处理...")
        time.sleep(5)
        
        # 查看统计
        lisi.print_stats()
    
    # 自动清理
    print("\n清理...")
    import shutil
    if Path(".inbox").exists():
        shutil.rmtree(".inbox")
    print("完成！")


if __name__ == "__main__":
    main()