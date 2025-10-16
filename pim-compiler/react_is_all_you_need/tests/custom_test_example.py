#!/usr/bin/env python3
"""
自定义测试用例示例

展示如何添加自己的测试用例来验证compact_prompt.md
"""

import os
from test_compact_prompt import CompactPromptTester


def run_custom_tests():
    """运行自定义测试"""

    # 创建测试器
    tester = CompactPromptTester(
        model="deepseek-chat",
        base_url="https://api.deepseek.com/v1"
    )

    print("🧪 运行自定义测试用例\n")

    # ===== 自定义测试用例1: 你的场景 =====
    # 例如：测试Agent是否能正确压缩多轮调试对话

    result = tester.test_case(
        name="多轮调试对话压缩",
        dialogue_history=[
            {"role": "user", "content": "代码报错了"},
            {"role": "assistant", "content": "什么错误？"},
            {"role": "user", "content": "ImportError: No module named 'requests'"},
            {"role": "assistant", "content": "需要安装requests"},
            {"role": "user", "content": "怎么安装？"},
            {"role": "assistant", "content": "pip install requests"},
            {"role": "user", "content": "还是不行"},
            {"role": "assistant", "content": "用pip3试试"},
            {"role": "user", "content": "成功了！"},
            {"role": "assistant", "content": "太好了"},
            {"role": "user", "content": "谢谢"},
            {"role": "assistant", "content": "不客气"}
        ],
        description="Python调试助手",
        expectations={
            "l2_content": "应该提取'ImportError → pip3 install requests'",
            "l3_context": "客套话应该压缩或删除",
            "process": "中间的来回讨论应该精简"
        }
    )

    # 检查结果
    if result.evaluation_score >= 0.7:
        print(f"\n✅ 测试通过！评分: {result.evaluation_score:.1%}")
    else:
        print(f"\n⚠️ 测试需要改进。评分: {result.evaluation_score:.1%}")

    print(f"\n压缩结果:")
    print(result.compressed_content)


if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 错误：未找到DEEPSEEK_API_KEY环境变量")
        exit(1)

    run_custom_tests()
