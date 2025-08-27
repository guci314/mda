#!/usr/bin/env python3
import unittest
import sys
from test_calculator import TestCalculator

# 创建测试套件
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestCalculator))

# 运行测试
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# 输出详细结果
print("\n" + "="*50)
print("测试结果汇总:")
print(f"运行测试数: {result.testsRun}")
print(f"失败数: {len(result.failures)}")
print(f"错误数: {len(result.errors)}")
print(f"跳过数: {len(result.skipped)}")

if result.wasSuccessful():
    print("✅ 所有测试通过!")
else:
    print("❌ 有测试失败或错误!")
    
    if result.failures:
        print("\n失败详情:")
        for failure in result.failures:
            print(f"{failure[0]}: {failure[1]}")
    
    if result.errors:
        print("\n错误详情:")
        for error in result.errors:
            print(f"{error[0]}: {error[1]}")

sys.exit(0 if result.wasSuccessful() else 1)