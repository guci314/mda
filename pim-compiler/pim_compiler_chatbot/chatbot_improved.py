#!/usr/bin/env python3
"""
改进版 PIM Compiler Chatbot - 带进程状态检查
"""

import os
import subprocess
import psutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class ImprovedPIMCompilerTools:
    """改进的 PIM 编译器工具集"""
    
    def __init__(self, pim_compiler_path: str = "."):
        self.pim_compiler_path = Path(pim_compiler_path).resolve()
        self.examples_dir = self.pim_compiler_path / "examples"
        self.compiled_output_dir = self.pim_compiler_path / "compiled_output"
        self.active_processes = {}  # 跟踪活动的编译进程
        
    def is_process_running(self, pid: int) -> bool:
        """检查进程是否仍在运行"""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def update_active_processes(self):
        """更新活动进程列表，移除已完成的进程"""
        completed = []
        for name, info in self.active_processes.items():
            if not self.is_process_running(info['pid']):
                completed.append(name)
        
        for name in completed:
            del self.active_processes[name]
    
    def get_compilation_status(self, log_file: Path) -> str:
        """分析日志文件获取编译状态"""
        if not log_file.exists():
            return "未找到日志文件"
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键状态标记
            if "Compilation completed successfully" in content:
                return "✅ 编译成功完成"
            elif "❌ Compilation failed" in content:
                return "❌ 编译失败"
            elif "❌ Compilation completed but REST tests pass rate" in content:
                return "⚠️ 编译完成但测试未完全通过"
            elif "Step 5: Testing REST endpoints" in content:
                return "🧪 正在测试 REST 端点..."
            elif "Step 4: Starting application" in content:
                return "🚀 正在启动应用..."
            elif "Step 3: Running tests" in content:
                return "🧪 正在运行测试..."
            elif "Step 2: Generating code" in content:
                return "💻 正在生成代码..."
            elif "Step 1: Generating PSM" in content:
                return "📝 正在生成 PSM..."
            else:
                return "🔄 编译进行中..."
        except Exception as e:
            return f"读取状态时出错: {str(e)}"
    
    def check_log_improved(self, system_name: Optional[str] = None) -> str:
        """改进的查看日志方法"""
        # 首先更新活动进程列表
        self.update_active_processes()
        
        if not system_name:
            # 显示所有编译任务状态
            result = "📊 编译任务状态:\n\n"
            
            # 1. 检查活动进程
            if self.active_processes:
                result += "🟢 活动的编译任务:\n"
                for name, info in self.active_processes.items():
                    duration = (datetime.now() - info['start_time']).seconds
                    log_file = Path(info['log_file'])
                    status = self.get_compilation_status(log_file)
                    result += f"\n- {name}:\n"
                    result += f"  状态: {status}\n"
                    result += f"  运行时间: {duration}秒\n"
                    result += f"  进程 PID: {info['pid']}\n"
                    result += f"  日志文件: {info['log_file']}\n"
            
            # 2. 检查最近的日志文件
            log_files = list(self.pim_compiler_path.glob("*.log"))
            if log_files:
                # 按修改时间排序，获取最近的5个
                recent_logs = sorted(log_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]
                result += "\n🟡 最近的编译日志:\n"
                for log_file in recent_logs:
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    status = self.get_compilation_status(log_file)
                    result += f"\n- {log_file.stem}:\n"
                    result += f"  状态: {status}\n"
                    result += f"  最后更新: {mtime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            return result
        else:
            # 查看特定系统的日志
            log_file = self.pim_compiler_path / f"{system_name}.log"
            if not log_file.exists():
                return f"未找到 {system_name} 的日志文件"
            
            # 检查是否为活动进程
            is_active = system_name in self.active_processes and \
                       self.is_process_running(self.active_processes[system_name]['pid'])
            
            status = self.get_compilation_status(log_file)
            
            result = f"📋 {system_name} 编译日志分析\n"
            result += f"状态: {status}\n"
            result += f"活动进程: {'是' if is_active else '否'}\n"
            result += f"日志文件: {log_file}\n"
            result += f"文件大小: {log_file.stat().st_size / 1024:.1f} KB\n"
            result += f"最后更新: {datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # 读取最后50行日志
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = ''.join(lines[-50:])
                result += f"\n最新日志:\n{'-'*60}\n{last_lines}\n{'-'*60}"
            
            return result


# 测试改进的功能
if __name__ == "__main__":
    tools = ImprovedPIMCompilerTools()
    
    print("测试改进的日志查看功能:")
    print("=" * 80)
    
    # 查看所有编译任务状态
    print(tools.check_log_improved())
    
    print("\n" + "=" * 80 + "\n")
    
    # 查看特定系统的日志
    print(tools.check_log_improved("blog"))