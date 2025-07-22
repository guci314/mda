#!/usr/bin/env python3
"""运行所有测试"""

import unittest
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试模块
    test_modules = [
        'tests.converters.test_pim_to_psm_gemini',
        'tests.converters.test_psm_to_code_gemini'
    ]
    
    for module in test_modules:
        try:
            suite.addTests(loader.loadTestsFromName(module))
            print(f"✓ 加载测试模块: {module}")
        except Exception as e:
            print(f"✗ 无法加载测试模块 {module}: {e}")
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回是否成功
    return result.wasSuccessful()


if __name__ == '__main__':
    print("运行 MDA 转换器单元测试...")
    print("=" * 70)
    
    success = run_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)