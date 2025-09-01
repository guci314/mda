#!/usr/bin/env python3
"""
调试测试问题的脚本
"""
import time
import subprocess
import sys

def run_with_timeout(cmd, timeout=3):
    """运行命令并设置超时"""
    try:
        start = time.time()
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start
        print(f"命令 '{cmd}' 执行时间: {elapsed:.2f}s")
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"标准错误:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ 命令 '{cmd}' 超时 ({timeout}s)")
        return False
    except Exception as e:
        print(f"❌ 命令 '{cmd}' 出错: {e}")
        return False

print("=== 测试诊断 ===")

# 测试1: 直接运行Python导入
test1 = run_with_timeout("python -c 'from main import app; print(\"✅ 直接导入成功\")'", 5)

# 测试2: 运行简单的pytest
test2 = run_with_timeout("python -m pytest tests/test_main.py::TestMain::test_health_check -v --tb=short", 10)

# 测试3: 检查数据库连接
test3 = run_with_timeout("python -c 'from database import engine; conn = engine.connect(); conn.close(); print(\"✅ 数据库连接正常\")'", 5)

print(f"\n=== 诊断结果 ===")
print(f"直接导入: {'✅ 成功' if test1 else '❌ 失败'}")
print(f"pytest测试: {'✅ 成功' if test2 else '❌ 失败或超时'}")
print(f"数据库连接: {'✅ 成功' if test3 else '❌ 失败'}")

if not test2:
    print("\n=== 进一步诊断pytest问题 ===")
    # 检查pytest配置
    run_with_timeout("python -m pytest --version", 3)
    run_with_timeout("python -c 'import pytest; print(f\"pytest版本: {pytest.__version__}\")'", 3)