"""MDA Test Suite - 运行所有测试"""

import unittest
import sys
import os
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 导入所有测试模块
try:
    from test_mda_orchestrator import TestMDAOrchestrator, TestMDAOrchestratorIntegration
    from test_mda_e2e import TestMDAEndToEnd, TestMDAPerformance
    from converters.test_converters_structure import TestConvertersStructure
    from converters.test_pim_to_psm_gemini import TestPIMtoPSMGeminiConverter
    from converters.test_psm_to_code_gemini import TestPSMtoCodeGeminiGenerator
except ImportError:
    # 尝试使用完整路径导入
    import sys
    from pathlib import Path
    tests_dir = Path(__file__).parent
    sys.path.insert(0, str(tests_dir))
    sys.path.insert(0, str(tests_dir / "converters"))
    
    import test_mda_orchestrator
    import test_mda_e2e
    import converters.test_converters_structure as test_converters_structure
    import converters.test_pim_to_psm_gemini as test_pim_to_psm_gemini
    import converters.test_psm_to_code_gemini as test_psm_to_code_gemini
    
    TestMDAOrchestrator = test_mda_orchestrator.TestMDAOrchestrator
    TestMDAOrchestratorIntegration = test_mda_orchestrator.TestMDAOrchestratorIntegration
    TestMDAEndToEnd = test_mda_e2e.TestMDAEndToEnd
    TestMDAPerformance = test_mda_e2e.TestMDAPerformance
    TestConvertersStructure = test_converters_structure.TestConvertersStructure
    TestPIMtoPSMGeminiConverter = test_pim_to_psm_gemini.TestPIMtoPSMGeminiConverter
    TestPSMtoCodeGeminiGenerator = test_psm_to_code_gemini.TestPSMtoCodeGeminiGenerator


def create_test_suite(include_integration=True):
    """创建测试套件"""
    suite = unittest.TestSuite()
    
    # 单元测试（不需要 API key）
    print("添加单元测试...")
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConvertersStructure))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMDAOrchestrator))
    
    if include_integration and os.getenv("GEMINI_API_KEY"):
        # 集成测试（需要 API key）
        print("添加集成测试（需要 API key）...")
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPIMtoPSMGeminiConverter))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPSMtoCodeGeminiGenerator))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMDAOrchestratorIntegration))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMDAEndToEnd))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMDAPerformance))
    else:
        print("跳过集成测试（未设置 GEMINI_API_KEY）")
    
    return suite


def run_tests(verbosity=2, include_integration=True):
    """运行测试套件"""
    print("=" * 70)
    print("MDA 测试套件")
    print("=" * 70)
    
    # 检查环境
    if os.getenv("GEMINI_API_KEY"):
        print("✓ GEMINI_API_KEY 已设置")
    else:
        print("✗ GEMINI_API_KEY 未设置 - 将跳过集成测试")
    
    print()
    
    # 创建和运行测试套件
    suite = create_test_suite(include_integration)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # 打印统计
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.skipped:
        print(f"跳过: {len(result.skipped)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # 解析命令行参数
    import argparse
    
    parser = argparse.ArgumentParser(description='运行 MDA 测试套件')
    parser.add_argument('--no-integration', action='store_true',
                       help='跳过集成测试（不需要 API key）')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    parser.add_argument('--quiet', action='store_true',
                       help='简洁输出')
    
    args = parser.parse_args()
    
    # 设置详细程度
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 3
    else:
        verbosity = 2
    
    # 运行测试
    success = run_tests(
        verbosity=verbosity,
        include_integration=not args.no_integration
    )
    
    # 退出码
    sys.exit(0 if success else 1)