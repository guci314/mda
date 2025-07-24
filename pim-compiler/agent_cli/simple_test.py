#!/usr/bin/env python3
"""
简单的 Agent CLI 测试
注意：这个文件应该通过 python -m agent_cli.simple_test 运行
"""
from .core import AgentCLI, LLMConfig


def test_basic_functionality():
    """测试基本功能"""
    print("测试 Agent CLI 基本功能...")
    
    # 创建配置
    config = LLMConfig(
        api_key="test-key",
        base_url="https://api.test.com/v1",
        model="test-model",
        provider="test"
    )
    print(f"✅ 配置创建成功: {config.provider}")
    
    # 创建 CLI 实例
    try:
        cli = AgentCLI(llm_config=config)
        print("✅ AgentCLI 实例创建成功")
        print(f"   - 提供商: {cli.llm_config.provider}")
        print(f"   - 模型: {cli.llm_config.model}")
        print(f"   - 工具数: {len(cli.tools)}")
    except Exception as e:
        print(f"❌ 创建失败: {e}")


if __name__ == "__main__":
    test_basic_functionality()