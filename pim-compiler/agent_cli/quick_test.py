#!/usr/bin/env python3
"""
快速测试 Agent CLI 修复
"""
import sys
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

if __name__ == "__main__":
    test_deepseek()