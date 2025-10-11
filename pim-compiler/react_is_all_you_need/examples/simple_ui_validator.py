#!/usr/bin/env python3
"""
简化的UI验证脚本
供Agent直接调用，无需MCP工具
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# 尝试导入pyppeteer，如果失败提供安装指引
try:
    from pyppeteer import launch
except ImportError:
    print("❌ 需要安装pyppeteer:")
    print("   pip install pyppeteer")
    print("\n或使用playwright (推荐):")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)


async def validate_ui(url='http://localhost:3000', config=None):
    """
    验证UI界面的简单函数

    Args:
        url: 要验证的URL
        config: 测试配置

    Returns:
        验证结果字典
    """
    # 默认配置
    if config is None:
        config = {
            'required_elements': ['#app', 'body'],
            'timeout': 30000,
            'screenshot': True
        }

    browser = None
    result = {
        'url': url,
        'success': True,
        'errors': [],
        'warnings': [],
        'console_errors': [],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        # 启动浏览器（无头模式）
        print(f"🚀 启动浏览器...")
        browser = await launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        page = await browser.newPage()

        # 收集console错误
        console_errors = []
        page.on('console', lambda msg:
            console_errors.append(msg.text) if msg.type in ['error', 'warning'] else None
        )

        # 访问页面
        print(f"📍 访问URL: {url}")
        try:
            response = await page.goto(url, {
                'waitUntil': 'networkidle2',
                'timeout': config.get('timeout', 30000)
            })

            # 检查HTTP状态
            if response.status >= 400:
                result['errors'].append(f'HTTP {response.status} 错误')
                result['success'] = False
            else:
                print(f"✅ 页面加载成功 (HTTP {response.status})")

        except Exception as e:
            result['errors'].append(f'页面加载失败: {str(e)}')
            result['success'] = False
            return result

        # 等待一下让页面完全渲染
        await page.waitFor(1000)

        # 获取页面内容
        html = await page.content()

        # 检查是否空白页
        if len(html.strip()) < 200:  # 过短可能是空白页
            result['errors'].append('页面可能为空')
            result['success'] = False

        # 检查必需元素
        print(f"🔍 检查页面元素...")
        for selector in config.get('required_elements', []):
            try:
                element = await page.querySelector(selector)
                if not element:
                    result['errors'].append(f'缺少元素: {selector}')
                    result['success'] = False
                else:
                    # 检查元素是否可见
                    is_visible = await page.evaluate(
                        '(element) => element && element.offsetParent !== null',
                        element
                    )
                    if not is_visible:
                        result['warnings'].append(f'元素不可见: {selector}')
            except Exception as e:
                result['errors'].append(f'检查元素失败 {selector}: {str(e)}')

        # 检查常见错误模式
        error_patterns = [
            ('React错误', ['Error:', 'Cannot read', 'undefined is not']),
            ('Vue错误', ['[Vue warn]', 'Vue error']),
            ('Angular错误', ['ERROR Error:', 'ExpressionChanged']),
            ('网络错误', ['Failed to fetch', 'NetworkError', '404', '500'])
        ]

        for error_type, patterns in error_patterns:
            for pattern in patterns:
                if pattern in html or any(pattern in err for err in console_errors):
                    result['errors'].append(f'{error_type}: 检测到 "{pattern}"')
                    result['success'] = False

        # 添加console错误到结果
        if console_errors:
            result['console_errors'] = console_errors[:10]  # 最多10条
            result['success'] = False

        # 截图
        if config.get('screenshot', False):
            screenshot_path = 'ui_validation_screenshot.png'
            await page.screenshot({
                'path': screenshot_path,
                'fullPage': True
            })
            result['screenshot'] = screenshot_path
            print(f"📸 已保存截图: {screenshot_path}")

        # 获取页面标题
        title = await page.title()
        result['page_title'] = title

        # 简单的性能检查
        perf_data = await page.evaluate('''() => {
            const timing = performance.timing;
            return {
                loadTime: timing.loadEventEnd - timing.navigationStart,
                domReady: timing.domContentLoadedEventEnd - timing.navigationStart
            };
        }''')

        if perf_data['loadTime'] > 5000:  # 超过5秒
            result['warnings'].append(f"页面加载缓慢: {perf_data['loadTime']/1000:.1f}秒")

        result['performance'] = perf_data

    except Exception as e:
        result['errors'].append(f'验证过程异常: {str(e)}')
        result['success'] = False

    finally:
        if browser:
            await browser.close()

    return result


def print_result(result):
    """打印验证结果"""
    print("\n" + "="*50)
    print("📊 UI验证结果")
    print("="*50)

    print(f"URL: {result['url']}")
    print(f"时间: {result['timestamp']}")
    print(f"状态: {'✅ 通过' if result['success'] else '❌ 失败'}")

    if result.get('page_title'):
        print(f"页面标题: {result['page_title']}")

    if result.get('performance'):
        print(f"加载时间: {result['performance']['loadTime']/1000:.1f}秒")

    if result['errors']:
        print(f"\n❌ 错误 ({len(result['errors'])}个):")
        for error in result['errors']:
            print(f"  - {error}")

    if result['warnings']:
        print(f"\n⚠️  警告 ({len(result['warnings'])}个):")
        for warning in result['warnings']:
            print(f"  - {warning}")

    if result['console_errors']:
        print(f"\n🔴 Console错误 ({len(result['console_errors'])}个):")
        for error in result['console_errors'][:5]:  # 只显示前5个
            print(f"  - {error[:100]}...")  # 截断过长的错误

    if result.get('screenshot'):
        print(f"\n📸 截图已保存: {result['screenshot']}")

    print("\n" + "="*50)


async def validate_with_interactions(url='http://localhost:3000', interactions=None):
    """
    带交互的UI验证

    Args:
        url: 基础URL
        interactions: 交互步骤列表

    Example interactions:
        [
            {'action': 'goto', 'url': '/login'},
            {'action': 'type', 'selector': '#username', 'text': 'test'},
            {'action': 'type', 'selector': '#password', 'text': 'pass'},
            {'action': 'click', 'selector': '#submit'},
            {'action': 'wait', 'selector': '.dashboard'},
            {'action': 'screenshot', 'path': 'after_login.png'}
        ]
    """
    if interactions is None:
        return await validate_ui(url)

    browser = None
    result = {
        'url': url,
        'success': True,
        'errors': [],
        'interactions_completed': 0,
        'total_interactions': len(interactions)
    }

    try:
        browser = await launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.newPage()

        # 执行交互步骤
        for i, step in enumerate(interactions):
            action = step.get('action')

            try:
                if action == 'goto':
                    full_url = url + step.get('url', '')
                    await page.goto(full_url, {'waitUntil': 'networkidle2'})
                    print(f"✅ 导航到: {full_url}")

                elif action == 'type':
                    await page.type(step['selector'], step['text'])
                    print(f"✅ 输入文本到: {step['selector']}")

                elif action == 'click':
                    await page.click(step['selector'])
                    await page.waitFor(500)  # 等待响应
                    print(f"✅ 点击: {step['selector']}")

                elif action == 'wait':
                    await page.waitForSelector(step['selector'], {'timeout': 5000})
                    print(f"✅ 等待元素: {step['selector']}")

                elif action == 'screenshot':
                    await page.screenshot({'path': step.get('path', f'step_{i}.png')})
                    print(f"✅ 截图保存: {step.get('path')}")

                result['interactions_completed'] += 1

            except Exception as e:
                result['errors'].append(f"步骤{i+1}失败 ({action}): {str(e)}")
                result['success'] = False
                break

    except Exception as e:
        result['errors'].append(f'交互测试异常: {str(e)}')
        result['success'] = False

    finally:
        if browser:
            await browser.close()

    return result


# 主函数
async def main():
    """主函数，可以直接运行测试"""

    # 从命令行参数获取URL
    url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:3000'

    # 测试配置
    config = {
        'required_elements': [
            '#app',        # React/Vue应用容器
            'body',        # 基础元素
            # 根据实际项目添加更多关键元素
        ],
        'screenshot': True,
        'timeout': 30000
    }

    print(f"🧪 开始UI验证测试")
    print(f"   URL: {url}")
    print(f"   配置: {len(config['required_elements'])}个必需元素")

    # 执行验证
    result = await validate_ui(url, config)

    # 打印结果
    print_result(result)

    # 保存JSON结果
    with open('ui_validation_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"📄 详细结果已保存: ui_validation_result.json")

    # 返回状态码（0=成功，1=失败）
    return 0 if result['success'] else 1


if __name__ == '__main__':
    # 运行验证
    exit_code = asyncio.run(main())
    sys.exit(exit_code)