#!/usr/bin/env python3
"""
测试报告查看器

提供测试报告的可视化和分析功能
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


class ReportViewer:
    """测试报告查看器"""
    
    def __init__(self):
        self.reports = []
    
    def load_report(self, file_path: Path) -> Dict[str, Any]:
        """加载测试报告"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_multiple_reports(self, pattern: str = "test_report_*.json") -> List[Dict[str, Any]]:
        """加载多个测试报告"""
        report_files = Path.cwd().glob(pattern)
        reports = []
        
        for file_path in report_files:
            try:
                report = self.load_report(file_path)
                reports.append({
                    'file': file_path.name,
                    'data': report
                })
            except:
                continue
        
        return reports
    
    def generate_summary_chart(self, reports: List[Dict[str, Any]], output_path: str = "test_summary.png"):
        """生成测试摘要图表"""
        # 提取数据
        agents = []
        success_rates = []
        total_tests = []
        
        for report in reports:
            data = report['data']
            agents.append(data['suite']['agent_name'])
            success_rates.append(data['summary']['success_rate'])
            total_tests.append(data['summary']['total_tests'])
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 成功率柱状图
        ax1.bar(agents, success_rates, color=['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in success_rates])
        ax1.set_xlabel('智能体')
        ax1.set_ylabel('成功率 (%)')
        ax1.set_title('各智能体测试成功率')
        ax1.set_ylim(0, 100)
        
        # 测试数量饼图
        ax2.pie(total_tests, labels=agents, autopct='%1.1f%%')
        ax2.set_title('测试用例分布')
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def generate_trend_chart(self, agent_name: str, days: int = 30, output_path: str = "test_trend.png"):
        """生成测试趋势图"""
        # 加载指定智能体的历史报告
        reports = self.load_multiple_reports(f"test_report_{agent_name}_*.json")
        
        # 按时间排序
        data_points = []
        for report in reports:
            summary = report['data']['summary']
            timestamp = datetime.fromisoformat(summary['start_time'])
            success_rate = summary['success_rate']
            data_points.append((timestamp, success_rate))
        
        data_points.sort(key=lambda x: x[0])
        
        # 创建趋势图
        dates = [point[0] for point in data_points]
        rates = [point[1] for point in data_points]
        
        plt.figure(figsize=(10, 6))
        plt.plot(dates, rates, marker='o', linestyle='-', linewidth=2, markersize=8)
        plt.axhline(y=80, color='green', linestyle='--', alpha=0.5, label='目标线 (80%)')
        
        plt.xlabel('日期')
        plt.ylabel('成功率 (%)')
        plt.title(f'{agent_name} 测试成功率趋势')
        plt.xticks(rotation=45)
        plt.ylim(0, 100)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def generate_detailed_report(self, report_data: Dict[str, Any], output_path: str = "detailed_report.html"):
        """生成详细的HTML报告"""
        suite = report_data['suite']
        summary = report_data['summary']
        results = report_data['results']
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{suite['name']} - 详细测试报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #2196F3;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            margin: -20px -20px 20px -20px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #2196F3;
        }}
        .test-case {{
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        .test-case-header {{
            padding: 15px;
            background-color: #f8f9fa;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .test-case-header:hover {{
            background-color: #e9ecef;
        }}
        .test-case.passed .test-case-header {{
            border-left: 4px solid #4CAF50;
        }}
        .test-case.failed .test-case-header {{
            border-left: 4px solid #f44336;
        }}
        .test-case-body {{
            padding: 15px;
            display: none;
            background-color: #fafafa;
        }}
        .test-case.expanded .test-case-body {{
            display: block;
        }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .status-badge.passed {{
            background-color: #4CAF50;
            color: white;
        }}
        .status-badge.failed {{
            background-color: #f44336;
            color: white;
        }}
        .logs {{
            background-color: #263238;
            color: #aed581;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            margin-top: 10px;
        }}
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background-color: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background-color: #4CAF50;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
    </style>
    <script>
        function toggleTestCase(id) {{
            const testCase = document.getElementById(id);
            testCase.classList.toggle('expanded');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{suite['name']}</h1>
            <p>{suite['description']}</p>
            <p>智能体: <strong>{suite['agent_name']}</strong></p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="value">{summary['total_tests']}</div>
            </div>
            <div class="summary-card">
                <h3>通过</h3>
                <div class="value" style="color: #4CAF50;">{summary['passed_tests']}</div>
            </div>
            <div class="summary-card">
                <h3>失败</h3>
                <div class="value" style="color: #f44336;">{summary['failed_tests']}</div>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="value">{summary['success_rate']:.1f}%</div>
            </div>
            <div class="summary-card">
                <h3>总耗时</h3>
                <div class="value">{summary['duration']:.1f}s</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {summary['success_rate']}%">
                {summary['success_rate']:.1f}%
            </div>
        </div>
        
        <h2>测试用例详情</h2>
"""
        
        # 添加每个测试用例
        for i, result in enumerate(results):
            status_class = "passed" if result['status'] == "passed" else "failed"
            status_text = "通过" if result['status'] == "passed" else "失败"
            
            html_content += f"""
        <div id="test-{i}" class="test-case {status_class}">
            <div class="test-case-header" onclick="toggleTestCase('test-{i}')">
                <div>
                    <strong>{result['name']}</strong>
                    <span style="margin-left: 10px; color: #666;">({result['duration']:.2f}秒)</span>
                </div>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
            <div class="test-case-body">
"""
            
            if result.get('error_message'):
                html_content += f"""
                <p><strong>错误信息:</strong> {result['error_message']}</p>
"""
            
            if result.get('actual_output'):
                html_content += f"""
                <p><strong>实际输出:</strong></p>
                <pre>{json.dumps(result['actual_output'], ensure_ascii=False, indent=2)}</pre>
"""
            
            if result.get('actual_actions'):
                html_content += f"""
                <p><strong>执行的动作:</strong></p>
                <ul>
"""
                for action in result['actual_actions']:
                    html_content += f"                    <li>{action}</li>\n"
                html_content += "                </ul>\n"
            
            if result.get('logs'):
                html_content += f"""
                <p><strong>日志:</strong></p>
                <div class="logs">
"""
                for log in result['logs']:
                    html_content += f"{log}\n"
                html_content += """                </div>
"""
            
            html_content += """            </div>
        </div>
"""
        
        # 添加页脚
        html_content += f"""
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; text-align: center; color: #666;">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Agent CLI Test Framework v1.0</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def analyze_failure_patterns(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析失败模式"""
        failure_patterns = {}
        total_failures = 0
        
        for report in reports:
            for result in report['data']['results']:
                if result['status'] != 'passed':
                    total_failures += 1
                    error = result.get('error_message', 'Unknown error')
                    
                    # 提取错误类型
                    if 'timeout' in error.lower():
                        error_type = 'Timeout'
                    elif 'syntax' in error.lower():
                        error_type = 'Syntax Error'
                    elif 'import' in error.lower():
                        error_type = 'Import Error'
                    elif 'assert' in error.lower():
                        error_type = 'Assertion Failed'
                    else:
                        error_type = 'Other'
                    
                    if error_type not in failure_patterns:
                        failure_patterns[error_type] = {
                            'count': 0,
                            'examples': []
                        }
                    
                    failure_patterns[error_type]['count'] += 1
                    if len(failure_patterns[error_type]['examples']) < 3:
                        failure_patterns[error_type]['examples'].append({
                            'test': result['name'],
                            'error': error
                        })
        
        return {
            'total_failures': total_failures,
            'patterns': failure_patterns
        }


if __name__ == '__main__':
    # 示例用法
    viewer = ReportViewer()
    
    # 加载所有报告
    reports = viewer.load_multiple_reports()
    
    if reports:
        # 生成摘要图表
        viewer.generate_summary_chart(reports, "test_summary.png")
        print("已生成测试摘要图表: test_summary.png")
        
        # 分析失败模式
        failure_analysis = viewer.analyze_failure_patterns(reports)
        print(f"\n失败分析:")
        print(f"总失败数: {failure_analysis['total_failures']}")
        for error_type, data in failure_analysis['patterns'].items():
            print(f"  {error_type}: {data['count']} 次")