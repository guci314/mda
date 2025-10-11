#!/usr/bin/env python3
"""
UI自动验证Agent
自动验证前端界面的正确性，无需人工介入
"""

import asyncio
import subprocess
import time
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

try:
    from pyppeteer import launch
except ImportError:
    print("请安装: pip install pyppeteer")

try:
    import httpx
except ImportError:
    print("请安装: pip install httpx")


@dataclass
class ValidationResult:
    """验证结果"""
    url: str
    success: bool
    errors: List[str] = None
    warnings: List[str] = None
    screenshot: str = None  # base64编码的截图
    console_errors: List[str] = None
    network_errors: List[str] = None
    visual_check: Dict[str, Any] = None
    performance: Dict[str, float] = None


class UIValidatorAgent:
    """
    UI验证Agent
    自动验证前端界面的正确性
    """

    def __init__(self, gemini_api_key: str = None, use_visual_ai: bool = True):
        self.gemini_api_key = gemini_api_key
        self.use_visual_ai = use_visual_ai
        self.browser = None
        self.page = None

        # 验证规则（条件反射层）
        self.validation_rules = {
            # 常见错误的快速检测
            'blank_page': lambda html: len(html.strip()) < 100,
            'react_error': lambda html: 'Error: ' in html or 'Cannot read' in html,
            'vue_error': lambda html: 'Vue warn' in html or 'Vue error' in html,
            'network_error': lambda html: '404' in html or '500' in html or 'Failed to fetch' in html,
            'missing_element': lambda html, selector: selector not in html,
        }

    async def start_browser(self):
        """启动浏览器"""
        self.browser = await launch(
            headless=True,  # 无头模式
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.page = await self.browser.newPage()

        # 监听console错误
        self.console_errors = []
        self.page.on('console', lambda msg:
            self.console_errors.append(msg.text) if msg.type in ['error', 'warning'] else None
        )

        # 监听网络错误
        self.network_errors = []
        self.page.on('requestfailed', lambda req:
            self.network_errors.append(f"{req.url}: {req.failure}")
        )

    async def validate_url(self, url: str, expected_elements: List[str] = None) -> ValidationResult:
        """
        验证指定URL的UI

        Args:
            url: 要验证的URL
            expected_elements: 期望存在的元素选择器列表
        """
        if not self.browser:
            await self.start_browser()

        result = ValidationResult(url=url, success=True)
        errors = []
        warnings = []

        # 重置错误收集器
        self.console_errors = []
        self.network_errors = []

        try:
            # 1. 导航到页面
            start_time = time.time()
            response = await self.page.goto(url, waitUntil='networkidle2', timeout=30000)
            load_time = time.time() - start_time

            # 2. 检查HTTP状态码
            if response.status >= 400:
                errors.append(f"HTTP错误: {response.status}")
                result.success = False

            # 3. 获取页面内容
            html = await self.page.content()

            # 4. 快速条件反射检查
            for rule_name, rule_func in self.validation_rules.items():
                if rule_name == 'missing_element':
                    continue  # 特殊处理
                if rule_func(html):
                    errors.append(f"规则失败: {rule_name}")
                    result.success = False

            # 5. 检查期望的元素
            if expected_elements:
                for selector in expected_elements:
                    element = await self.page.querySelector(selector)
                    if not element:
                        errors.append(f"缺少元素: {selector}")
                        result.success = False
                    else:
                        # 检查元素是否可见
                        is_visible = await self.page.evaluate(
                            '(element) => element.offsetParent !== null',
                            element
                        )
                        if not is_visible:
                            warnings.append(f"元素不可见: {selector}")

            # 6. 截图
            screenshot_bytes = await self.page.screenshot(fullPage=True)
            result.screenshot = base64.b64encode(screenshot_bytes).decode()

            # 7. 视觉AI验证（如果启用）
            if self.use_visual_ai and self.gemini_api_key:
                visual_result = await self.visual_validate(screenshot_bytes)
                result.visual_check = visual_result
                if not visual_result.get('success', True):
                    errors.extend(visual_result.get('errors', []))
                    result.success = False

            # 8. 收集console和网络错误
            if self.console_errors:
                result.console_errors = self.console_errors
                errors.extend([f"Console: {err}" for err in self.console_errors])
                result.success = False

            if self.network_errors:
                result.network_errors = self.network_errors
                errors.extend([f"Network: {err}" for err in self.network_errors])
                result.success = False

            # 9. 性能指标
            perf_data = await self.page.evaluate('''() => {
                const perf = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
                    loadComplete: perf.loadEventEnd - perf.loadEventStart,
                    totalTime: perf.loadEventEnd - perf.fetchStart
                };
            }''')

            result.performance = {
                'load_time': load_time,
                'dom_content_loaded': perf_data['domContentLoaded'],
                'load_complete': perf_data['loadComplete'],
                'total_time': perf_data['totalTime']
            }

            if load_time > 5:
                warnings.append(f"页面加载缓慢: {load_time:.2f}秒")

        except Exception as e:
            errors.append(f"验证异常: {str(e)}")
            result.success = False

        result.errors = errors if errors else None
        result.warnings = warnings if warnings else None

        return result

    async def visual_validate(self, screenshot_bytes: bytes) -> Dict[str, Any]:
        """
        使用Gemini进行视觉验证
        """
        if not self.gemini_api_key:
            return {'success': True, 'message': '未配置视觉AI'}

        try:
            import httpx

            # 准备请求
            client = httpx.AsyncClient(
                timeout=30,
                proxies='socks5://127.0.0.1:7890'  # 中国网络环境
            )

            # 调用Gemini Vision API
            prompt = """
            请分析这个网页截图，检查以下问题：
            1. 是否有明显的布局错误（元素重叠、错位）
            2. 是否有空白区域或内容缺失
            3. 是否有错误提示或异常信息
            4. 整体UI是否正常

            返回JSON格式：
            {
                "success": true/false,
                "errors": ["错误列表"],
                "suggestions": ["改进建议"]
            }
            """

            # 这里简化处理，实际需要调用Gemini Vision API
            # response = await client.post(...)

            return {
                'success': True,
                'message': '视觉验证通过（示例）'
            }

        except Exception as e:
            return {
                'success': False,
                'errors': [f'视觉验证失败: {str(e)}']
            }

    async def validate_interaction(self, url: str, interactions: List[Dict]) -> ValidationResult:
        """
        验证用户交互

        Args:
            url: 页面URL
            interactions: 交互步骤列表
                [
                    {'action': 'click', 'selector': '#button'},
                    {'action': 'type', 'selector': '#input', 'text': 'test'},
                    {'action': 'wait', 'selector': '#result'},
                    {'action': 'assert', 'selector': '#result', 'text': 'Success'}
                ]
        """
        if not self.browser:
            await self.start_browser()

        result = ValidationResult(url=url, success=True)
        errors = []

        try:
            # 导航到页面
            await self.page.goto(url, waitUntil='networkidle2')

            # 执行交互步骤
            for step in interactions:
                action = step['action']
                selector = step.get('selector')

                try:
                    if action == 'click':
                        await self.page.click(selector)
                        await self.page.waitFor(500)  # 等待响应

                    elif action == 'type':
                        await self.page.type(selector, step['text'])

                    elif action == 'wait':
                        await self.page.waitForSelector(selector, timeout=5000)

                    elif action == 'assert':
                        element = await self.page.querySelector(selector)
                        if element:
                            text = await self.page.evaluate('(el) => el.textContent', element)
                            if step.get('text') and step['text'] not in text:
                                errors.append(f"断言失败: {selector} 不包含 '{step['text']}'")
                                result.success = False
                        else:
                            errors.append(f"断言失败: 找不到元素 {selector}")
                            result.success = False

                    elif action == 'screenshot':
                        screenshot_bytes = await self.page.screenshot()
                        result.screenshot = base64.b64encode(screenshot_bytes).decode()

                except Exception as e:
                    errors.append(f"交互步骤失败 [{action}]: {str(e)}")
                    result.success = False
                    break

        except Exception as e:
            errors.append(f"交互验证失败: {str(e)}")
            result.success = False

        result.errors = errors if errors else None
        return result

    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None


class UITestRunner:
    """
    UI测试运行器
    管理和执行UI测试套件
    """

    def __init__(self):
        self.validator = None
        self.results = []

    async def run_test_suite(self, base_url: str, test_suite: Dict) -> Dict[str, Any]:
        """
        运行测试套件

        Args:
            base_url: 基础URL
            test_suite: 测试套件配置
        """
        self.validator = UIValidatorAgent()

        total_tests = len(test_suite['tests'])
        passed = 0
        failed = 0

        print(f"\n{'='*60}")
        print(f"🧪 运行UI测试套件: {test_suite['name']}")
        print(f"{'='*60}")

        for test in test_suite['tests']:
            print(f"\n测试: {test['name']}")

            url = f"{base_url}{test['path']}"

            # 基础验证
            if 'elements' in test:
                result = await self.validator.validate_url(url, test['elements'])
            # 交互验证
            elif 'interactions' in test:
                result = await self.validator.validate_interaction(url, test['interactions'])
            else:
                result = await self.validator.validate_url(url)

            self.results.append({
                'test': test['name'],
                'result': result
            })

            if result.success:
                print(f"✅ 通过")
                passed += 1
            else:
                print(f"❌ 失败")
                if result.errors:
                    for error in result.errors:
                        print(f"   - {error}")
                failed += 1

            if result.warnings:
                for warning in result.warnings:
                    print(f"   ⚠️ {warning}")

            if result.performance:
                print(f"   ⏱️ 加载时间: {result.performance['load_time']:.2f}秒")

        await self.validator.close()

        # 生成测试报告
        report = {
            'suite': test_suite['name'],
            'total': total_tests,
            'passed': passed,
            'failed': failed,
            'success_rate': f"{(passed/total_tests)*100:.1f}%",
            'results': self.results
        }

        print(f"\n{'='*60}")
        print(f"📊 测试报告")
        print(f"{'='*60}")
        print(f"总计: {total_tests} | 通过: {passed} | 失败: {failed}")
        print(f"成功率: {report['success_rate']}")

        return report


# 示例：订单系统UI测试套件
ORDER_SYSTEM_TEST_SUITE = {
    'name': '订单系统UI测试',
    'tests': [
        {
            'name': '首页加载',
            'path': '/',
            'elements': [
                '#app',
                '.header',
                '.order-list',
                '.create-order-btn'
            ]
        },
        {
            'name': '创建订单流程',
            'path': '/orders/new',
            'interactions': [
                {'action': 'wait', 'selector': '#product-select'},
                {'action': 'click', 'selector': '#product-select'},
                {'action': 'click', 'selector': 'option[value="1"]'},
                {'action': 'type', 'selector': '#quantity', 'text': '2'},
                {'action': 'type', 'selector': '#customer-name', 'text': '测试客户'},
                {'action': 'click', 'selector': '#submit-order'},
                {'action': 'wait', 'selector': '.success-message'},
                {'action': 'assert', 'selector': '.success-message', 'text': '订单创建成功'}
            ]
        },
        {
            'name': '订单列表显示',
            'path': '/orders',
            'elements': [
                '.order-table',
                '.order-row',
                '.pagination'
            ]
        },
        {
            'name': '订单详情页',
            'path': '/orders/1',
            'elements': [
                '.order-detail',
                '.order-id',
                '.order-status',
                '.order-items',
                '.order-total'
            ]
        }
    ]
}


# 使用示例
async def main():
    """示例：验证订单系统UI"""

    # 1. 启动本地开发服务器（假设是React/Vue应用）
    print("启动开发服务器...")
    server_process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd='/path/to/order-system-ui',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # 等待服务器启动
    await asyncio.sleep(5)

    try:
        # 2. 运行测试套件
        runner = UITestRunner()
        report = await runner.run_test_suite(
            base_url='http://localhost:3000',
            test_suite=ORDER_SYSTEM_TEST_SUITE
        )

        # 3. 保存测试报告
        with open('ui_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n测试报告已保存到: ui_test_report.json")

        # 4. 如果有失败，生成修复建议
        if report['failed'] > 0:
            print("\n🔧 修复建议:")
            for result_item in report['results']:
                if not result_item['result'].success:
                    print(f"\n{result_item['test']}:")
                    for error in result_item['result'].errors or []:
                        if 'Console:' in error:
                            print(f"  - 检查浏览器控制台错误")
                        elif '缺少元素' in error:
                            print(f"  - 确认元素选择器是否正确")
                        elif 'HTTP错误' in error:
                            print(f"  - 检查后端API是否正常")
                        elif '断言失败' in error:
                            print(f"  - 验证业务逻辑是否正确")

    finally:
        # 5. 停止开发服务器
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())