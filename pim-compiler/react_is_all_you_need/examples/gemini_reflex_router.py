#!/usr/bin/env python3
"""
Gemini Flash 条件反射路由器
使用Gemini Flash做快速模式识别，实现智能路由：
- 数学计算 → Python计算器
- 其他问题 → DeepSeek

演示条件反射的核心理念：快速模式匹配 + 专用处理器
"""

import os
import sys
import json
import time
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 导入计算器模块
from calculator_module import CalculatorService

# API客户端
import requests
import httpx


class IntentType(Enum):
    """意图类型"""
    MATH = "math"           # 数学计算
    GENERAL = "general"     # 通用问题
    UNKNOWN = "unknown"     # 未知


@dataclass
class RouteDecision:
    """路由决策"""
    intent: IntentType
    confidence: float
    reasoning: str
    response_time: float


class GeminiReflexRouter:
    """
    Gemini Flash 条件反射路由器
    使用极快的模式匹配决定路由
    """

    def __init__(self, gemini_api_key: str = None, deepseek_api_key: str = None,
                 use_proxy: bool = True, proxy_url: str = "socks5://127.0.0.1:7890"):
        """初始化路由器

        Args:
            gemini_api_key: Gemini API密钥，如果不提供会从.env文件读取
            deepseek_api_key: DeepSeek API密钥
            use_proxy: 是否使用代理（中国网络环境需要）
            proxy_url: 代理地址
        """
        # 读取.env文件获取API Key
        if not gemini_api_key:
            env_path = "/home/guci/aiProjects/mda/pim-compiler/.env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            gemini_api_key = line.split("=", 1)[1].strip()
                            break

        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

        # DeepSeek API Key
        if not deepseek_api_key:
            env_path = "/home/guci/aiProjects/mda/pim-compiler/.env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith("DEEPSEEK_API_KEY="):
                            deepseek_api_key = line.split("=", 1)[1].strip()
                            break

        self.deepseek_api_key = deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")

        # 计算器服务
        self.calculator = CalculatorService()

        # Gemini配置
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.gemini_model = "gemini-2.0-flash-exp"  # 最新最快的Flash模型

        # 创建HTTP客户端（使用代理）
        if use_proxy:
            try:
                # 安装httpx的socks支持：pip install "httpx[socks]"
                # 新版httpx使用proxies参数而不是proxy
                self.http_client = httpx.Client(
                    proxies=proxy_url,  # 使用proxies而不是proxy
                    timeout=30,
                    verify=False
                )
                print(f"✅ 已配置代理: {proxy_url}")
            except Exception as e:
                print(f"⚠️ 代理配置失败: {e}")
                print("   尝试直接连接...")
                self.http_client = httpx.Client(timeout=30)
        else:
            self.http_client = httpx.Client(timeout=30)

        # DeepSeek配置
        self.deepseek_base_url = "https://api.deepseek.com/v1"

        # 性能统计
        self.stats = {
            'total_requests': 0,
            'math_routes': 0,
            'general_routes': 0,
            'avg_decision_time': 0,
            'avg_math_time': 0,
            'avg_general_time': 0
        }

        # 初始化简单的模式匹配（备用）
        self._init_patterns()

    def _init_patterns(self):
        """初始化快速模式匹配（当API不可用时的备用方案）"""
        self.math_patterns = [
            r'\d+\s*[\+\-\*\/]\s*\d+',  # 基础运算
            r'计算|等于|多少|结果',       # 中文数学关键词
            r'calculate|equals|sum',      # 英文数学关键词
            r'根号|平方|立方|sin|cos',    # 数学函数
            r'百分之|%|percent',          # 百分比
            r'转换|convert|to',           # 单位转换
        ]

    def detect_intent(self, user_input: str) -> RouteDecision:
        """
        使用Gemini Flash快速检测意图
        这是条件反射的核心：极快的模式识别
        """
        start_time = time.time()

        # 方案1：使用Gemini Flash API（推荐）
        try:
            decision = self._gemini_detect_intent(user_input)
            decision.response_time = time.time() - start_time
            return decision
        except Exception as e:
            print(f"⚠️ Gemini API调用失败: {e}")
            print("   切换到本地模式匹配...")

        # 方案2：本地快速模式匹配（备用）
        decision = self._local_detect_intent(user_input)
        decision.response_time = time.time() - start_time
        return decision

    def _gemini_detect_intent(self, user_input: str) -> RouteDecision:
        """使用Gemini Flash API检测意图"""

        # 精心设计的提示词，让Gemini专注于意图分类
        prompt = f"""判断这个用户输入是否是数学计算问题。

用户输入: "{user_input}"

回答格式（JSON）：
{{
    "is_math": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "一句话解释"
}}

判断标准：
- 数学计算：加减乘除、函数运算、单位换算、百分比计算等
- 非数学：问候、闲聊、知识问答、代码问题、其他

只返回JSON，不要其他内容。"""

        # 调用Gemini API（使用httpx客户端）
        url = f"{self.gemini_base_url}/models/{self.gemini_model}:generateContent"

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,  # 低温度，确保稳定输出
                "maxOutputTokens": 100,  # 限制输出长度
                "topP": 0.8
            }
        }

        # 添加API key到URL
        url = f"{url}?key={self.gemini_api_key}"

        # 使用httpx客户端（带代理）
        response = self.http_client.post(url, headers=headers, json=data, timeout=5)

        if response.status_code == 200:
            result = response.json()

            # 提取生成的文本
            generated_text = result['candidates'][0]['content']['parts'][0]['text']

            # 解析JSON
            try:
                # 提取JSON部分（去除可能的markdown标记）
                json_str = generated_text
                if '```' in json_str:
                    json_str = json_str.split('```')[1]
                    if json_str.startswith('json'):
                        json_str = json_str[4:]

                intent_data = json.loads(json_str.strip())

                return RouteDecision(
                    intent=IntentType.MATH if intent_data['is_math'] else IntentType.GENERAL,
                    confidence=intent_data['confidence'],
                    reasoning=intent_data['reasoning'],
                    response_time=0  # 将在外部设置
                )
            except json.JSONDecodeError:
                # JSON解析失败，降级到简单判断
                is_math = '是' in generated_text or 'true' in generated_text.lower()
                return RouteDecision(
                    intent=IntentType.MATH if is_math else IntentType.GENERAL,
                    confidence=0.7,
                    reasoning="Gemini返回格式异常，使用简单判断",
                    response_time=0
                )
        else:
            raise Exception(f"API返回错误: {response.status_code}")

    def _local_detect_intent(self, user_input: str) -> RouteDecision:
        """本地快速模式匹配（备用方案）"""

        # 首先使用计算器模块的判断
        if self.calculator.can_handle(user_input):
            return RouteDecision(
                intent=IntentType.MATH,
                confidence=0.9,
                reasoning="计算器模块识别为数学问题",
                response_time=0
            )

        # 使用正则表达式快速匹配
        text_lower = user_input.lower()
        for pattern in self.math_patterns:
            if re.search(pattern, text_lower):
                return RouteDecision(
                    intent=IntentType.MATH,
                    confidence=0.8,
                    reasoning=f"匹配到数学模式: {pattern[:20]}",
                    response_time=0
                )

        # 默认为通用问题
        return RouteDecision(
            intent=IntentType.GENERAL,
            confidence=0.7,
            reasoning="未匹配到数学模式",
            response_time=0
        )

    def route_request(self, user_input: str) -> Dict[str, Any]:
        """
        主路由逻辑：条件反射的执行
        """
        self.stats['total_requests'] += 1
        total_start = time.time()

        # Step 1: 快速意图识别（条件反射）
        print(f"\n🧠 分析输入: {user_input}")
        decision = self.detect_intent(user_input)

        print(f"⚡ 意图识别: {decision.intent.value}")
        print(f"   置信度: {decision.confidence:.2%}")
        print(f"   推理: {decision.reasoning}")
        print(f"   决策用时: {decision.response_time*1000:.1f}ms")

        # Step 2: 路由到对应处理器
        if decision.intent == IntentType.MATH and decision.confidence > 0.6:
            # 路由到计算器
            self.stats['math_routes'] += 1
            result = self._handle_math(user_input)
            route_type = "calculator"
        else:
            # 路由到DeepSeek
            self.stats['general_routes'] += 1
            result = self._handle_general(user_input)
            route_type = "deepseek"

        # 统计
        total_time = time.time() - total_start
        self._update_stats(decision.intent, total_time)

        return {
            'input': user_input,
            'route': route_type,
            'decision': {
                'intent': decision.intent.value,
                'confidence': decision.confidence,
                'reasoning': decision.reasoning,
                'decision_time': decision.response_time
            },
            'result': result,
            'total_time': total_time
        }

    def _handle_math(self, user_input: str) -> Dict[str, Any]:
        """处理数学计算（调用Python计算器）"""
        print(f"🔢 路由到: Python计算器")

        start_time = time.time()
        result = self.calculator.execute(user_input)
        calc_time = time.time() - start_time

        print(f"   计算结果: {result.get('display', result.get('error'))}")
        print(f"   计算用时: {calc_time*1000:.1f}ms")

        return {
            'handler': 'calculator',
            'response': result['display'],
            'details': result,
            'time': calc_time
        }

    def _handle_general(self, user_input: str) -> Dict[str, Any]:
        """处理通用问题（调用DeepSeek）"""
        print(f"💭 路由到: DeepSeek")

        if not self.deepseek_api_key:
            return {
                'handler': 'deepseek',
                'response': "DeepSeek API未配置，无法处理通用问题",
                'error': 'API_KEY_MISSING',
                'time': 0
            }

        start_time = time.time()

        try:
            # 调用DeepSeek API
            url = f"{self.deepseek_base_url}/chat/completions"

            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }

            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
            else:
                answer = f"DeepSeek API错误: {response.status_code}"

        except Exception as e:
            answer = f"调用DeepSeek失败: {str(e)}"

        api_time = time.time() - start_time

        print(f"   回答: {answer[:100]}...")
        print(f"   API用时: {api_time*1000:.1f}ms")

        return {
            'handler': 'deepseek',
            'response': answer,
            'time': api_time
        }

    def _update_stats(self, intent: IntentType, total_time: float):
        """更新统计信息"""
        n = self.stats['total_requests']

        # 更新平均决策时间
        old_avg = self.stats['avg_decision_time']
        self.stats['avg_decision_time'] = (old_avg * (n-1) + total_time) / n

        # 更新各类型平均时间
        if intent == IntentType.MATH:
            m = self.stats['math_routes']
            old_math_avg = self.stats['avg_math_time']
            self.stats['avg_math_time'] = (old_math_avg * (m-1) + total_time) / m
        else:
            g = self.stats['general_routes']
            old_general_avg = self.stats['avg_general_time']
            self.stats['avg_general_time'] = (old_general_avg * (g-1) + total_time) / g

    def print_stats(self):
        """打印统计信息"""
        print("\n" + "="*50)
        print("📊 路由统计")
        print("="*50)
        print(f"总请求数: {self.stats['total_requests']}")
        print(f"数学路由: {self.stats['math_routes']} "
              f"({self.stats['math_routes']/max(1, self.stats['total_requests'])*100:.1f}%)")
        print(f"通用路由: {self.stats['general_routes']} "
              f"({self.stats['general_routes']/max(1, self.stats['total_requests'])*100:.1f}%)")
        print(f"平均响应时间: {self.stats['avg_decision_time']*1000:.1f}ms")

        if self.stats['math_routes'] > 0:
            print(f"数学平均时间: {self.stats['avg_math_time']*1000:.1f}ms")
        if self.stats['general_routes'] > 0:
            print(f"通用平均时间: {self.stats['avg_general_time']*1000:.1f}ms")


def demo_routing():
    """演示路由功能"""
    print("="*60)
    print("🚀 Gemini条件反射路由器演示")
    print("="*60)

    # 创建路由器（自动从.env读取API Keys）
    router = GeminiReflexRouter()

    if not router.gemini_api_key:
        print("❌ 错误: 未找到GEMINI_API_KEY")
        print("   请检查 /home/guci/aiProjects/mda/pim-compiler/.env 文件")
        return

    print(f"✅ Gemini API已配置")
    print(f"{'✅' if router.deepseek_api_key else '⚠️'} DeepSeek API"
          f"{'已配置' if router.deepseek_api_key else '未配置（将跳过通用问题）'}")

    # 测试用例
    test_cases = [
        # 明显的数学问题
        "1+1等于多少",
        "计算100的20%",
        "根号16是多少",
        "5的平方",

        # 明显的通用问题
        "你好，今天天气怎么样",
        "Python是什么语言",
        "如何学习编程",

        # 边界案例
        "帮我算一下今年的税收",  # 包含"算"但不是纯数学
        "1984年发生了什么",      # 包含数字但不是计算
        "三体问题怎么解决",       # 包含"三"但是物理问题
    ]

    print("\n开始测试路由...\n")

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{len(test_cases)}")
        print(f"{'='*60}")

        result = router.route_request(test_input)

        print(f"\n📝 总结:")
        print(f"   路由到: {result['route']}")
        print(f"   总耗时: {result['total_time']*1000:.1f}ms")

        time.sleep(0.5)  # 避免API限流

    # 打印统计
    router.print_stats()


def interactive_mode():
    """交互模式"""
    print("="*60)
    print("💬 Gemini条件反射路由器 - 交互模式")
    print("="*60)

    # 创建路由器（自动从.env读取API Keys）
    router = GeminiReflexRouter()

    if not router.gemini_api_key:
        print("❌ 未找到GEMINI_API_KEY")
        print("   请检查 /home/guci/aiProjects/mda/pim-compiler/.env 文件")
        return

    print("\n说明:")
    print("- 数学问题会路由到Python计算器（极快）")
    print("- 其他问题会路由到DeepSeek（较慢）")
    print("- 输入 /stats 查看统计")
    print("- 输入 /quit 退出")
    print("-"*40)

    while True:
        user_input = input("\n👤 > ").strip()

        if user_input == "/quit":
            break
        elif user_input == "/stats":
            router.print_stats()
            continue
        elif not user_input:
            continue

        result = router.route_request(user_input)

        print(f"\n🤖 > {result['result']['response']}")

        # 显示路由信息
        print(f"\n[路由: {result['route']} | "
              f"决策: {result['decision']['decision_time']*1000:.0f}ms | "
              f"总计: {result['total_time']*1000:.0f}ms]")

    print("\n👋 再见！")
    router.print_stats()


def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        demo_routing()


if __name__ == "__main__":
    main()