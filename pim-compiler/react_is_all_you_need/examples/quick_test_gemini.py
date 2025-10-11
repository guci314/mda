#!/usr/bin/env python3
"""
快速测试Gemini条件反射路由
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_reflex_router import GeminiReflexRouter

def quick_test():
    print("="*50)
    print("🚀 Gemini条件反射路由 - 快速测试")
    print("="*50)

    # 创建路由器（自动从.env读取配置）
    print("\n1. 初始化路由器...")
    router = GeminiReflexRouter()

    if not router.gemini_api_key:
        print("❌ 未找到API Key")
        print("   请检查: /home/guci/aiProjects/mda/pim-compiler/.env")
        return

    print(f"✅ Gemini API已配置")
    print(f"✅ 代理已配置" if router.http_client.params.get('proxy') else "⚠️ 未使用代理")

    # 测试简单计算
    print("\n2. 测试数学识别和计算...")
    test_input = "25+75等于多少"
    print(f"   输入: {test_input}")

    result = router.route_request(test_input)

    print(f"\n📊 结果:")
    print(f"   路由到: {result['route']}")
    print(f"   答案: {result['result']['response']}")
    print(f"   决策时间: {result['decision']['decision_time']*1000:.1f}ms")
    print(f"   总时间: {result['total_time']*1000:.1f}ms")

    # 测试非数学问题
    if router.deepseek_api_key:
        print("\n3. 测试通用问题识别...")
        test_input = "你好"
        print(f"   输入: {test_input}")

        result = router.route_request(test_input)

        print(f"\n📊 结果:")
        print(f"   路由到: {result['route']}")
        print(f"   答案: {result['result']['response'][:50]}...")
        print(f"   决策时间: {result['decision']['decision_time']*1000:.1f}ms")
        print(f"   总时间: {result['total_time']*1000:.1f}ms")

    print("\n✅ 测试完成！")

if __name__ == "__main__":
    quick_test()