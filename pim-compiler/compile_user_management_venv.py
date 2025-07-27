#!/usr/bin/env python3
"""在虚拟环境中编译用户管理PIM"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 确保在项目根目录
os.chdir(Path(__file__).parent)

def compile_pim(generator_name: str):
    """使用指定生成器编译PIM"""
    print(f"\n{'='*60}")
    print(f"Compiling with {generator_name}")
    print('='*60)
    
    output_dir = f"output/venv_compile/{generator_name}_user_management"
    log_file = f"output/venv_compile/{generator_name}_compile.log"
    
    # 确保输出目录存在
    Path("output/venv_compile").mkdir(parents=True, exist_ok=True)
    
    # 构建命令
    cmd = [
        sys.executable,
        "compile_pim.py",
        "--pim", "examples/user_management.md",
        "--generator", generator_name,
        "--platform", "fastapi",
        "--output-dir", output_dir
    ]
    
    # 添加额外参数
    if generator_name == "react-agent":
        cmd.extend(["--max-iterations", "30"])
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Log file: {log_file}")
    
    # 执行编译
    start_time = time.time()
    with open(log_file, 'w') as log:
        try:
            # 后台运行
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                env={**os.environ, "PYTHONPATH": os.getcwd()}
            )
            
            print(f"✅ Started compilation process (PID: {process.pid})")
            print(f"Monitor progress: tail -f {log_file}")
            
            # 等待一会儿检查是否启动成功
            time.sleep(3)
            if process.poll() is not None:
                print(f"❌ Process exited early with code: {process.returncode}")
                with open(log_file, 'r') as f:
                    print(f.read()[-500:])  # 打印最后500个字符
            else:
                print(f"✅ Process is running...")
                
        except Exception as e:
            print(f"❌ Failed to start: {str(e)}")

def main():
    """主函数"""
    print("=== Compiling User Management PIM in Virtual Environment ===")
    print(f"Python: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # 检查虚拟环境
    if "venv_test" not in sys.executable:
        print("⚠️  Warning: Not running in venv_test virtual environment")
        print("Run: source venv_test/bin/activate")
        return
    
    # 选择生成器
    print("\nAvailable generators:")
    print("1. gemini-cli - Gemini CLI Generator")
    print("2. react-agent - React Agent with Testing Tools")
    print("3. autogen - Microsoft Autogen Multi-Agent")
    
    choice = input("\nSelect generator (1-3) or name: ").strip()
    
    generator_map = {
        "1": "gemini-cli",
        "2": "react-agent", 
        "3": "autogen",
        "gemini-cli": "gemini-cli",
        "react-agent": "react-agent",
        "autogen": "autogen"
    }
    
    generator = generator_map.get(choice)
    if not generator:
        print("❌ Invalid choice")
        return
    
    compile_pim(generator)

if __name__ == "__main__":
    main()