#!/usr/bin/env python3
"""
图书借阅系统测试脚本
"""
import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_tests():
    """运行测试"""
    print("🧪 开始运行测试...")
    
    # 设置测试环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    try:
        # 运行pytest
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd=project_root,
            env=env,
            capture_output=False
        )
        
        if result.returncode == 0:
            print("✅ 所有测试通过")
        else:
            print("❌ 部分测试失败")
            
        return result.returncode == 0
        
    except FileNotFoundError:
        print("❌ pytest未安装，请运行: pip install pytest")
        return False
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False


def run_specific_test(test_file):
    """运行特定测试文件"""
    print(f"🧪 运行测试文件: {test_file}")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", f"tests/{test_file}", "-v"],
            cwd=project_root,
            env=env,
            capture_output=False
        )
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 运行特定测试文件
        test_file = sys.argv[1]
        if not test_file.startswith("test_"):
            test_file = f"test_{test_file}"
        if not test_file.endswith(".py"):
            test_file = f"{test_file}.py"
        
        success = run_specific_test(test_file)
    else:
        # 运行所有测试
        success = run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()