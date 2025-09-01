#!/usr/bin/env python
"""运行所有unittest测试"""
import unittest
import sys

def run_tests():
    """运行tests目录下的所有测试"""
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 发现tests目录下的所有测试
    suite = loader.discover('tests', pattern='test_*.py')
    
    # 创建测试运行器
    runner = unittest.TextTestRunner(verbosity=2)
    
    # 运行测试
    result = runner.run(suite)
    
    # 返回退出码
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())