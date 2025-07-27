#!/usr/bin/env python3
"""
Agent CLI 测试框架演示

演示如何使用测试框架测试智能体
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_cli.core.agent_registry import AgentRegistry
from agent_cli.core.test_runner import TestRunner, TestCase, TestSuite
from agent_cli.agents.code_generator import CodeGeneratorAgent
from agent_cli.utils.report_viewer import ReportViewer


def create_simple_test_suite():
    """创建一个简单的测试套件"""
    test_cases = [
        TestCase(
            name="test_hello_world",
            description="测试生成 Hello World 函数",
            input={
                "task": "generate",
                "language": "python",
                "description": "生成一个打印 'Hello, World!' 的函数"
            },
            expected_output={
                "status": "success",
                "language": "python"
            },
            expected_actions=[
                "analyze_requirements",
                "generate_code*"
            ],
            timeout=30,
            tags=["basic"]
        ),
        TestCase(
            name="test_add_function",
            description="测试生成加法函数",
            input={
                "task": "generate",
                "language": "python",
                "description": "生成一个两数相加的函数，函数名为 add，接收参数 a 和 b"
            },
            expected_output={
                "status": "success",
                "language": "python"
            },
            expected_actions=[
                "analyze_requirements",
                "generate_code*",
                "validate_syntax"
            ],
            timeout=30,
            tags=["basic", "math"]
        )
    ]
    
    suite = TestSuite(
        name="code_generator_demo_suite",
        description="代码生成智能体演示测试套件",
        agent_name="code_generator",
        test_cases=test_cases,
        tags=["demo"]
    )
    
    return suite


def main():
    """主函数"""
    print("Agent CLI 测试框架演示")
    print("=" * 60)
    
    # 1. 注册智能体
    print("\n1. 注册智能体...")
    registry = AgentRegistry()
    code_agent = CodeGeneratorAgent()
    registry.register(code_agent)
    print(f"   ✓ 已注册: {code_agent.metadata.name}")
    
    # 2. 创建测试套件
    print("\n2. 创建测试套件...")
    suite = create_simple_test_suite()
    print(f"   ✓ 测试用例数: {len(suite.test_cases)}")
    
    # 3. 运行测试
    print("\n3. 运行测试...")
    runner = TestRunner(registry)
    report = runner.run_test_suite(suite)
    
    # 4. 保存报告
    print("\n4. 保存测试报告...")
    
    # JSON 格式
    json_path = Path("demo_test_report.json")
    runner.save_report(report, json_path, "json")
    print(f"   ✓ JSON 报告: {json_path}")
    
    # HTML 格式
    html_path = Path("demo_test_report.html")
    runner.save_report(report, html_path, "html")
    print(f"   ✓ HTML 报告: {html_path}")
    
    # Markdown 格式
    md_path = Path("demo_test_report.md")
    runner.save_report(report, md_path, "markdown")
    print(f"   ✓ Markdown 报告: {md_path}")
    
    # 5. 生成可视化报告
    print("\n5. 生成可视化报告...")
    viewer = ReportViewer()
    
    # 生成详细HTML报告
    detailed_html = viewer.generate_detailed_report(
        {
            'suite': {
                'name': suite.name,
                'description': suite.description,
                'agent_name': suite.agent_name,
                'tags': suite.tags
            },
            'summary': {
                'total_tests': report.total_tests,
                'passed_tests': report.passed_tests,
                'failed_tests': report.failed_tests,
                'success_rate': report.success_rate,
                'duration': report.duration,
                'start_time': report.start_time.isoformat(),
                'end_time': report.end_time.isoformat()
            },
            'results': [
                {
                    'name': r.test_case.name,
                    'status': r.status.value,
                    'duration': r.duration,
                    'actual_output': r.actual_output,
                    'actual_actions': r.actual_actions,
                    'error_message': r.error_message,
                    'logs': r.logs
                }
                for r in report.results
            ]
        },
        "demo_detailed_report.html"
    )
    print(f"   ✓ 详细报告: {detailed_html}")
    
    # 6. 测试命令行工具
    print("\n6. 测试命令行工具示例:")
    print("   # 生成测试模板")
    print("   ./agent-cli test generate code_generator")
    print("")
    print("   # 运行测试")
    print("   ./agent-cli test run code_generator_test.json")
    print("")
    print("   # 查看报告")
    print("   ./agent-cli test show test_report_code_generator_*.json")
    print("")
    print("   # 统计结果")
    print("   ./agent-cli test stats --days 7")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    
    # 返回状态
    return 0 if report.failed_tests == 0 else 1


if __name__ == '__main__':
    sys.exit(main())