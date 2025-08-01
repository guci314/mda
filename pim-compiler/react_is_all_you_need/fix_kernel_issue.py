#!/usr/bin/env python3
"""
诊断和修复Jupyter内核问题
"""

import os
import sys
import subprocess
import json
import time

def check_kernel_spec():
    """检查内核规格"""
    print("=== 检查内核规格 ===")
    try:
        result = subprocess.run(['jupyter', 'kernelspec', 'list'], 
                              capture_output=True, text=True)
        print(result.stdout)
        return 'react_agent_env' in result.stdout
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_kernel_launch():
    """测试内核启动"""
    print("\n=== 测试内核启动 ===")
    try:
        # 创建一个简单的测试连接文件
        test_conn_file = "/tmp/test_kernel.json"
        conn_data = {
            "shell_port": 12345,
            "iopub_port": 12346,
            "stdin_port": 12347,
            "hb_port": 12348,
            "ip": "127.0.0.1",
            "key": "test_key"
        }
        
        with open(test_conn_file, 'w') as f:
            json.dump(conn_data, f)
        
        # 尝试启动内核
        cmd = [
            sys.executable, "-m", "ipykernel_launcher",
            "-f", test_conn_file
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        # 设置超时
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待5秒
        try:
            stdout, stderr = process.communicate(timeout=5)
            print("内核启动成功")
            return True
        except subprocess.TimeoutExpired:
            process.kill()
            print("内核启动超时")
            return False
            
    except Exception as e:
        print(f"内核启动测试失败: {e}")
        return False

def check_environment():
    """检查环境"""
    print("\n=== 检查环境 ===")
    print(f"Python路径: {sys.executable}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查关键包
    try:
        import ipykernel
        print("✅ ipykernel 可用")
    except ImportError as e:
        print(f"❌ ipykernel 不可用: {e}")
        return False
    
    try:
        import jupyter_client
        print("✅ jupyter_client 可用")
    except ImportError as e:
        print(f"❌ jupyter_client 不可用: {e}")
        return False
    
    return True

def fix_kernel_issue():
    """修复内核问题"""
    print("\n=== 尝试修复内核问题 ===")
    
    # 重新安装内核
    try:
        cmd = [
            sys.executable, "-m", "ipykernel", "install",
            "--user", "--name=react_agent_env",
            "--display-name=React Agent Environment"
        ]
        
        print(f"重新安装内核: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 内核重新安装成功")
            return True
        else:
            print(f"❌ 内核重新安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 重新安装内核时出错: {e}")
        return False

def create_simple_notebook():
    """创建一个简单的测试notebook"""
    print("\n=== 创建测试notebook ===")
    
    test_notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import sys\n",
                    "print('Python路径:', sys.executable)\n",
                    "print('测试成功！')"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "React Agent Environment",
                "language": "python",
                "name": "react_agent_env"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open('test_notebook.ipynb', 'w') as f:
        json.dump(test_notebook, f, indent=2)
    
    print("✅ 测试notebook已创建: test_notebook.ipynb")

def main():
    """主函数"""
    print("Jupyter内核问题诊断和修复工具")
    print("=" * 50)
    
    # 检查环境
    env_ok = check_environment()
    if not env_ok:
        print("❌ 环境检查失败")
        return False
    
    # 检查内核规格
    spec_ok = check_kernel_spec()
    if not spec_ok:
        print("❌ 内核规格检查失败")
        return False
    
    # 测试内核启动
    launch_ok = test_kernel_launch()
    if not launch_ok:
        print("❌ 内核启动测试失败")
        print("尝试修复...")
        fix_ok = fix_kernel_issue()
        if fix_ok:
            print("重新测试内核启动...")
            launch_ok = test_kernel_launch()
    
    # 创建测试notebook
    create_simple_notebook()
    
    print("\n" + "=" * 50)
    print("诊断结果:")
    
    if env_ok and spec_ok and launch_ok:
        print("🎉 所有检查都通过！")
        print("\n建议:")
        print("1. 使用 test_notebook.ipynb 进行测试")
        print("2. 如果测试notebook工作正常，再尝试 agent_research.ipynb")
        print("3. 如果仍有问题，可能需要重启Jupyter服务器")
        return True
    else:
        print("❌ 存在问题，请检查上述错误信息")
        return False

if __name__ == "__main__":
    main() 