#!/usr/bin/env python3
"""
快速测试 Agent CLI 修复
"""
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_cli.core import AgentCLI, LLMConfig

def test_deepseek():
    """测试 DeepSeek 提供商"""
    print("测试 DeepSeek Agent CLI...")
    
    try:
        # 创建配置
        config = LLMConfig.from_env("deepseek")
        print(f"✅ 配置加载成功: {config.model}")
        
        # 创建 CLI
        cli = AgentCLI(llm_config=config)
        
        # 执行简单任务
        task = "创建一个简单的用户认证系统的设计方案，包含注册和登录功能"
        print(f"\n执行任务: {task}")
        
        success, message = cli.execute_task(task)
        
        print(f"\n结果: {'✅ 成功' if success else '❌ 失败'}")
        print(f"消息: {message}")
        
        # 获取执行摘要
        summary = cli.get_execution_summary()
        print(f"\n执行摘要:")
        print(f"- 总动作数: {summary['total_actions']}")
        print(f"- 上下文键: {summary['context_keys']}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_openrouter():
    """测试 OpenRouter 提供商"""
    print("\n" + "="*60)
    print("测试 OpenRouter (Google Gemini) Agent CLI...")
    print("="*60)
    
    try:
        # 创建配置
        config = LLMConfig.from_env("openrouter")
        print(f"✅ 配置加载成功: {config.model}")
        
        # 创建 CLI
        cli = AgentCLI(llm_config=config)
        
        # 执行任务
        task = "创建一个简单的待办事项应用的设计方案"
        print(f"\n执行任务: {task}")
        
        start_time = time.time()
        success, message = cli.execute_task(task)
        duration = time.time() - start_time
        
        print(f"\n结果: {'✅ 成功' if success else '❌ 失败'}")
        print(f"消息: {message}")
        print(f"耗时: {duration:.1f} 秒")
        
        # 获取执行摘要
        summary = cli.get_execution_summary()
        print(f"\n执行摘要:")
        print(f"- 总动作数: {summary['total_actions']}")
        print(f"- 上下文键: {summary['context_keys']}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_moonshot():
    """测试 Moonshot 提供商"""
    print("\n" + "="*60)
    print("测试 Moonshot (月之暗面) Agent CLI...")
    print("="*60)
    
    try:
        # 创建配置
        config = LLMConfig.from_env("moonshot")
        print(f"✅ 配置加载成功: {config.model}")
        
        # 创建 CLI
        cli = AgentCLI(llm_config=config)
        
        # 执行任务
        task = "创建一个简单的用户认证系统的设计方案，包含注册和登录功能"
        print(f"\n执行任务: {task}")
        
        start_time = time.time()
        success, message = cli.execute_task(task)
        duration = time.time() - start_time
        
        print(f"\n结果: {'✅ 成功' if success else '❌ 失败'}")
        print(f"消息: {message}")
        print(f"耗时: {duration:.1f} 秒")
        
        # 获取执行摘要
        summary = cli.get_execution_summary()
        print(f"\n执行摘要:")
        print(f"- 总动作数: {summary['total_actions']}")
        print(f"- 上下文键: {summary['context_keys']}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        provider = sys.argv[1].lower()
        if provider == "moonshot":
            test_moonshot()
        elif provider == "openrouter":
            test_openrouter()
        elif provider == "deepseek":
            test_deepseek()
        elif provider == "all":
            test_deepseek()
            test_moonshot()
            test_openrouter()
        else:
            print(f"未知的提供商: {provider}")
            print("支持的提供商: deepseek, moonshot, openrouter, all")
    else:
        test_deepseek()
        print("\n提示: 使用 'python quick_test.py moonshot' 测试 Moonshot")
        print("      使用 'python quick_test.py openrouter' 测试 OpenRouter")
        print("      使用 'python quick_test.py all' 测试所有提供商")