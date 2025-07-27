#!/usr/bin/env python3
"""在虚拟环境中编译用户管理PIM"""

import os
import sys
import subprocess
from pathlib import Path
import json
import time

# 设置项目根目录
project_root = Path(__file__).parent
os.chdir(project_root)

# 添加项目到Python路径
sys.path.insert(0, str(project_root))

def compile_with_generator(generator_name: str, pim_file: str):
    """使用指定的生成器编译PIM"""
    print(f"\n{'='*60}")
    print(f"Compiling with {generator_name} generator")
    print('='*60)
    
    output_dir = f"output/venv_compile/{generator_name}"
    
    # 构建编译命令
    cmd = [
        sys.executable,  # 使用当前Python解释器
        "compile_pim.py",
        "--pim", pim_file,
        "--generator", generator_name,
        "--platform", "fastapi",
        "--output-dir", output_dir
    ]
    
    # 添加额外参数
    if generator_name == "react-agent":
        cmd.extend(["--max-iterations", "20"])
    
    print(f"Command: {' '.join(cmd)}")
    
    # 执行编译
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(project_root)}
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Compilation successful in {elapsed_time:.2f}s")
            print(f"Output directory: {output_dir}")
            
            # 检查生成的文件
            output_path = Path(output_dir)
            if output_path.exists():
                files = list(output_path.rglob("*.py"))
                print(f"Generated {len(files)} Python files")
        else:
            print(f"❌ Compilation failed after {elapsed_time:.2f}s")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """主函数"""
    print("=== Compiling User Management PIM in Virtual Environment ===")
    print(f"Python: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # 检查PIM文件
    pim_file = "examples/user_management.md"
    if not Path(pim_file).exists():
        print(f"❌ PIM file not found: {pim_file}")
        
        # 尝试其他位置
        alt_locations = [
            "models/domain/用户管理_pim.md",
            "../models/domain/用户管理_pim.md",
            "../../models/domain/用户管理_pim.md"
        ]
        
        for alt in alt_locations:
            if Path(alt).exists():
                pim_file = alt
                print(f"✅ Found PIM file at: {pim_file}")
                break
        else:
            print("❌ Could not find user management PIM file")
            return
    
    # 测试不同的生成器
    generators = [
        "gemini-cli",      # Gemini CLI生成器
        "react-agent",     # React Agent生成器（带测试工具）
        "autogen",         # Autogen多智能体生成器
    ]
    
    for generator in generators:
        try:
            compile_with_generator(generator, pim_file)
        except Exception as e:
            print(f"❌ Failed to compile with {generator}: {str(e)}")

if __name__ == "__main__":
    main()