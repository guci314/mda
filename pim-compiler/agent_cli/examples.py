#!/usr/bin/env python3
"""
Agent CLI 使用示例
展示如何使用不同的 LLM 提供商
"""
from agent_cli import AgentCLI, LLMConfig


def example_openai():
    """使用 OpenAI 的示例"""
    print("=== OpenAI 示例 ===")
    
    # 方式1：从环境变量加载
    # export OPENAI_API_KEY="sk-..."
    # export LLM_PROVIDER=openai
    try:
        config = LLMConfig.from_env("openai")
        cli = AgentCLI(llm_config=config)
        success, message = cli.execute_task("分析 Python 代码质量的最佳实践")
        print(f"结果: {message}")
    except Exception as e:
        print(f"需要设置 OPENAI_API_KEY: {e}")
    
    # 方式2：手动配置
    config = LLMConfig(
        api_key="your-openai-key",
        base_url="https://api.openai.com/v1",
        model="gpt-3.5-turbo",
        provider="openai",
        temperature=0.7,
        max_tokens=1000
    )
    # cli = AgentCLI(llm_config=config)


def example_deepseek():
    """使用 DeepSeek 的示例"""
    print("\n=== DeepSeek 示例 ===")
    
    # DeepSeek 配置
    config = LLMConfig(
        api_key="your-deepseek-key",
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
        provider="deepseek",
        temperature=0.3
    )
    
    # 创建 CLI
    # cli = AgentCLI(llm_config=config)
    
    # PIM 转换任务
    task = "将用户管理系统的 PIM 转换为 FastAPI 的 PSM"
    # success, message = cli.execute_task(task)
    
    print(f"配置完成: {config.provider} - {config.model}")


def example_qwen():
    """使用通义千问的示例"""
    print("\n=== 通义千问示例 ===")
    
    # 通义千问配置
    config = LLMConfig(
        api_key="your-dashscope-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-turbo",
        provider="qwen"
    )
    
    # 代码生成任务
    # cli = AgentCLI(llm_config=config)
    # code = cli.generate_code("创建一个用户认证的 REST API")
    
    print(f"配置完成: {config.provider} - {config.model}")


def example_custom_provider():
    """使用自定义兼容 OpenAI API 的服务"""
    print("\n=== 自定义提供商示例 ===")
    
    # 任何兼容 OpenAI API 的服务都可以使用
    config = LLMConfig(
        api_key="your-api-key",
        base_url="https://your-api-endpoint.com/v1",
        model="your-model-name",
        provider="custom",
        temperature=0.5,
        max_tokens=2000
    )
    
    # 使用示例
    # cli = AgentCLI(llm_config=config)
    
    print(f"配置完成: 自定义服务 - {config.base_url}")


def example_multi_provider_workflow():
    """多提供商工作流示例"""
    print("\n=== 多提供商工作流示例 ===")
    
    # 场景：使用不同提供商处理不同任务
    
    # 1. 使用 DeepSeek 进行代码生成（便宜）
    deepseek_config = LLMConfig(
        api_key="deepseek-key",
        base_url="https://api.deepseek.com/v1",
        model="deepseek-coder",
        provider="deepseek"
    )
    
    # 2. 使用 GPT-4 进行复杂分析（强大）
    gpt4_config = LLMConfig(
        api_key="openai-key",
        base_url="https://api.openai.com/v1",
        model="gpt-4",
        provider="openai"
    )
    
    # 3. 使用通义千问处理中文文档（中文优化）
    qwen_config = LLMConfig(
        api_key="dashscope-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-max",
        provider="qwen"
    )
    
    print("多提供商配置完成:")
    print("- 代码生成: DeepSeek (低成本)")
    print("- 复杂分析: GPT-4 (高性能)")
    print("- 中文处理: 通义千问 (中文优化)")


def example_batch_processing():
    """批处理示例"""
    print("\n=== 批处理示例 ===")
    
    import glob
    from concurrent.futures import ThreadPoolExecutor
    
    # 配置
    config = LLMConfig.from_env("deepseek")  # 使用便宜的提供商
    
    def process_file(file_path):
        """处理单个文件"""
        cli = AgentCLI(llm_config=config)
        task = f"分析 {file_path} 文件的代码质量"
        return cli.execute_task(task)
    
    # 模拟批处理
    files = ["file1.py", "file2.py", "file3.py"]
    print(f"批处理 {len(files)} 个文件")
    
    # 使用线程池并发处理
    # with ThreadPoolExecutor(max_workers=3) as executor:
    #     results = list(executor.map(process_file, files))


def main():
    """运行所有示例"""
    examples = [
        example_openai,
        example_deepseek,
        example_qwen,
        example_custom_provider,
        example_multi_provider_workflow,
        example_batch_processing
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"示例运行出错: {e}")
    
    print("\n提示：")
    print("1. 请替换示例中的 API Key")
    print("2. 取消注释要运行的代码")
    print("3. 确保已安装依赖: pip install langchain-openai")


if __name__ == "__main__":
    main()