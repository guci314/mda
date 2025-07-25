#!/usr/bin/env python3
"""
监控博客系统代码生成进度
"""

import os
import time
import subprocess
import re
from datetime import datetime


def check_process_status(pid):
    """检查进程是否在运行"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def parse_log_for_progress(log_file):
    """解析日志获取进度信息"""
    if not os.path.exists(log_file):
        return None
        
    stats = {
        "steps_completed": 0,
        "total_steps": 0,
        "current_step": "",
        "actions_count": 0,
        "files_created": [],
        "errors": [],
        "last_action": "",
        "compression_events": 0
    }
    
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
            
        for line in lines:
            # 统计步骤
            if "Created plan with" in line and "steps:" in line:
                match = re.search(r"(\d+) steps", line)
                if match:
                    stats["total_steps"] = int(match.group(1))
                    
            # 当前步骤
            if "Executing step:" in line:
                stats["current_step"] = line.split("Executing step:")[-1].strip()
                
            # 步骤完成
            if "✓ Step completed:" in line:
                stats["steps_completed"] += 1
                
            # 动作统计
            if re.search(r"Action \d+:", line):
                stats["actions_count"] += 1
                stats["last_action"] = line.strip()
                
            # 文件创建
            if "write_file" in line and "✓ Action completed" in line:
                stats["files_created"].append(line)
                
            # 错误
            if "ERROR" in line or "✗" in line:
                stats["errors"].append(line.strip())
                
            # 压缩事件
            if "Context size exceeded limit, compressing" in line:
                stats["compression_events"] += 1
                
            # 任务完成
            if "✅ Task completed successfully" in line:
                stats["task_completed"] = True
            elif "❌ Task failed" in line:
                stats["task_failed"] = True
                
    except Exception as e:
        print(f"解析日志时出错: {e}")
        
    return stats


def monitor_generation():
    """监控代码生成过程"""
    log_file = "blog_generation.log"
    pid_file = "blog_generation.pid"
    output_dir = "blog_management_output"
    
    print("=== 博客系统代码生成监控 ===\n")
    
    # 读取 PID
    if not os.path.exists(pid_file):
        print("❌ 未找到 PID 文件，请先启动生成任务")
        print("   运行: python generate_blog_system.py --background")
        return
        
    with open(pid_file, "r") as f:
        pid = int(f.read().strip())
        
    print(f"监控进程 PID: {pid}")
    print(f"日志文件: {log_file}")
    print(f"输出目录: {output_dir}\n")
    
    start_time = time.time()
    last_line_count = 0
    
    try:
        while True:
            # 检查进程状态
            is_running = check_process_status(pid)
            
            # 解析日志
            stats = parse_log_for_progress(log_file)
            
            # 清屏（可选）
            # os.system('clear' if os.name == 'posix' else 'cls')
            
            # 显示状态
            elapsed = int(time.time() - start_time)
            print(f"\n{'='*60}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 已运行: {elapsed}秒")
            print(f"{'='*60}")
            
            print(f"进程状态: {'🟢 运行中' if is_running else '🔴 已停止'}")
            
            if stats:
                # 进度信息
                if stats["total_steps"] > 0:
                    progress = stats["steps_completed"] / stats["total_steps"] * 100
                    print(f"\n📊 进度: {stats['steps_completed']}/{stats['total_steps']} 步骤 ({progress:.1f}%)")
                    print(f"   当前步骤: {stats['current_step']}")
                
                # 动作统计
                print(f"\n🔧 动作统计:")
                print(f"   总动作数: {stats['actions_count']}")
                print(f"   最近动作: {stats['last_action']}")
                
                # 压缩统计
                if stats["compression_events"] > 0:
                    print(f"\n💾 上下文压缩: {stats['compression_events']} 次")
                
                # 文件统计
                if os.path.exists(output_dir):
                    file_count = sum(1 for root, dirs, files in os.walk(output_dir) 
                                   for f in files)
                    print(f"\n📁 已生成文件: {file_count} 个")
                    
                    # 显示最近创建的文件
                    recent_files = subprocess.run(
                        ["find", output_dir, "-type", "f", "-mmin", "-1"],
                        capture_output=True, text=True
                    )
                    if recent_files.stdout:
                        print("   最近创建:")
                        for f in recent_files.stdout.strip().split("\n")[:5]:
                            print(f"   - {f.replace(output_dir + '/', '')}")
                
                # 错误信息
                if stats["errors"]:
                    print(f"\n⚠️  错误 ({len(stats['errors'])} 个):")
                    for err in stats["errors"][-3:]:  # 显示最近3个错误
                        print(f"   {err}")
                
                # 检查完成状态
                if stats.get("task_completed"):
                    print(f"\n✅ 任务已完成！")
                    break
                elif stats.get("task_failed"):
                    print(f"\n❌ 任务失败！")
                    break
            
            # 显示日志尾部
            if os.path.exists(log_file):
                print(f"\n📋 最新日志:")
                print("-" * 60)
                tail = subprocess.run(
                    ["tail", "-20", log_file],
                    capture_output=True, text=True
                )
                # 只显示有意义的行
                for line in tail.stdout.split("\n"):
                    if any(keyword in line for keyword in 
                          ["Step", "Action", "✓", "✗", "ERROR", "生成", "创建"]):
                        print(f"   {line.strip()}")
            
            # 检查是否完成
            if not is_running:
                print(f"\n进程已结束")
                
                # 检查输出
                if os.path.exists(output_dir):
                    print(f"\n📂 生成的项目结构:")
                    tree_result = subprocess.run(
                        ["tree", output_dir, "-L", "2"],
                        capture_output=True, text=True
                    )
                    print(tree_result.stdout)
                    
                break
            
            # 等待下次检查
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n监控已停止")
        
    # 清理 PID 文件
    if not check_process_status(pid) and os.path.exists(pid_file):
        os.remove(pid_file)
        print(f"\n已清理 PID 文件")


def show_final_summary():
    """显示最终摘要"""
    output_dir = "blog_management_output"
    
    if os.path.exists(output_dir):
        print(f"\n{'='*60}")
        print("📊 生成摘要")
        print(f"{'='*60}")
        
        # 统计文件
        file_stats = {}
        total_size = 0
        
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                ext = os.path.splitext(f)[1]
                if ext not in file_stats:
                    file_stats[ext] = 0
                file_stats[ext] += 1
                
                file_path = os.path.join(root, f)
                total_size += os.path.getsize(file_path)
        
        print(f"\n文件类型统计:")
        for ext, count in sorted(file_stats.items()):
            print(f"  {ext or '(no ext)'}: {count} 个文件")
            
        print(f"\n总大小: {total_size / 1024:.1f} KB")
        
        # 检查关键文件
        key_files = [
            "app/main.py",
            "app/config.py", 
            "app/database.py",
            "requirements.txt",
            "README.md",
            ".env.example"
        ]
        
        print(f"\n关键文件检查:")
        for f in key_files:
            path = os.path.join(output_dir, f)
            status = "✅" if os.path.exists(path) else "❌"
            print(f"  {status} {f}")


if __name__ == "__main__":
    try:
        monitor_generation()
        show_final_summary()
    except Exception as e:
        print(f"\n❌ 监控出错: {e}")
        import traceback
        traceback.print_exc()