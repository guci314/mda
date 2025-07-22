#!/usr/bin/env python3
"""异步测试运行器 - 支持长时间运行的测试"""

import subprocess
import time
import os
import sys
from pathlib import Path
from datetime import datetime
import threading
import json

class AsyncTestRunner:
    def __init__(self, output_dir="test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.processes = {}
        
    def run_test(self, name, command, env_vars=None):
        """在后台运行测试"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{name}_{timestamp}.log"
        status_file = self.output_dir / f"{name}_status.json"
        
        # 准备环境变量
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
            
        # 加载 .env 文件中的 API keys
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if 'API' in key or 'KEY' in key:
                            env[key] = value
        
        # 启动进程
        with open(output_file, 'w') as f:
            f.write(f"=== 测试开始: {datetime.now()} ===\n")
            f.write(f"命令: {command}\n")
            f.write("=" * 50 + "\n\n")
            
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=open(output_file, 'a'),
            stderr=subprocess.STDOUT,
            env=env
        )
        
        # 保存进程信息
        self.processes[name] = {
            'process': process,
            'command': command,
            'output_file': str(output_file),
            'start_time': datetime.now().isoformat(),
            'pid': process.pid
        }
        
        # 保存状态
        self._save_status(name, 'running', status_file)
        
        # 在后台线程中监控进程
        monitor_thread = threading.Thread(
            target=self._monitor_process,
            args=(name, process, output_file, status_file)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print(f"✓ 启动测试: {name}")
        print(f"  PID: {process.pid}")
        print(f"  输出: {output_file}")
        
        return process.pid
        
    def _monitor_process(self, name, process, output_file, status_file):
        """监控进程状态"""
        process.wait()
        
        # 记录结束时间和状态
        with open(output_file, 'a') as f:
            f.write(f"\n{'=' * 50}\n")
            f.write(f"=== 测试结束: {datetime.now()} ===\n")
            f.write(f"退出码: {process.returncode}\n")
            
        status = 'success' if process.returncode == 0 else 'failed'
        self._save_status(name, status, status_file, process.returncode)
        
    def _save_status(self, name, status, status_file, return_code=None):
        """保存测试状态"""
        data = {
            'name': name,
            'status': status,
            'update_time': datetime.now().isoformat(),
            'return_code': return_code
        }
        
        if name in self.processes:
            data.update({
                'command': self.processes[name]['command'],
                'output_file': self.processes[name]['output_file'],
                'start_time': self.processes[name]['start_time'],
                'pid': self.processes[name]['pid']
            })
            
        with open(status_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def check_status(self):
        """检查所有测试状态"""
        print("\n=== 测试状态 ===")
        
        status_files = list(self.output_dir.glob("*_status.json"))
        if not status_files:
            print("没有正在运行的测试")
            return
            
        for status_file in status_files:
            with open(status_file) as f:
                data = json.load(f)
                
            name = data['name']
            status = data['status']
            
            print(f"\n[{name}]")
            print(f"  状态: {status}")
            print(f"  命令: {data.get('command', 'N/A')}")
            
            if status == 'running':
                pid = data.get('pid')
                if pid and self._is_process_running(pid):
                    print(f"  PID: {pid} (运行中)")
                else:
                    print(f"  PID: {pid} (可能已结束)")
                    
            elif status in ['success', 'failed']:
                print(f"  退出码: {data.get('return_code', 'N/A')}")
                print(f"  开始时间: {data.get('start_time', 'N/A')}")
                print(f"  结束时间: {data.get('update_time', 'N/A')}")
                
            # 显示最后几行输出
            output_file = data.get('output_file')
            if output_file and Path(output_file).exists():
                print(f"  最后几行输出:")
                lines = Path(output_file).read_text().splitlines()
                for line in lines[-5:]:
                    print(f"    {line}")
                    
    def _is_process_running(self, pid):
        """检查进程是否在运行"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
            
    def tail_output(self, name, lines=20):
        """查看测试输出的最后几行"""
        status_file = self.output_dir / f"{name}_status.json"
        if not status_file.exists():
            print(f"找不到测试: {name}")
            return
            
        with open(status_file) as f:
            data = json.load(f)
            
        output_file = data.get('output_file')
        if output_file and Path(output_file).exists():
            print(f"\n=== {name} 输出 (最后 {lines} 行) ===")
            output_lines = Path(output_file).read_text().splitlines()
            for line in output_lines[-lines:]:
                print(line)
        else:
            print(f"找不到输出文件: {output_file}")

def main():
    """主函数"""
    runner = AsyncTestRunner()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python test_runner.py run <test_name> <command>")
        print("  python test_runner.py status")
        print("  python test_runner.py tail <test_name> [lines]")
        print("")
        print("示例:")
        print("  python test_runner.py run deepseek 'python -m pytest tests/converters/test_pim_to_psm_deepseek.py -v'")
        print("  python test_runner.py status")
        print("  python test_runner.py tail deepseek 50")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == "run":
        if len(sys.argv) < 4:
            print("错误: 需要提供测试名称和命令")
            sys.exit(1)
        name = sys.argv[2]
        command = ' '.join(sys.argv[3:])
        runner.run_test(name, command)
        
    elif action == "status":
        runner.check_status()
        
    elif action == "tail":
        if len(sys.argv) < 3:
            print("错误: 需要提供测试名称")
            sys.exit(1)
        name = sys.argv[2]
        lines = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        runner.tail_output(name, lines)
        
    else:
        print(f"未知操作: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()