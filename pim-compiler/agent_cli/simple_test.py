#!/usr/bin/env python3
"""
简单测试连接主义推理
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# 加载 .env 文件
load_dotenv()

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_cli.core import AgentCLI, LLMConfig, Action, ActionType


def test_llm_decision():
    """测试LLM决策功能"""
    print("测试 LLM 决策功能")
    print("="*50)
    
    try:
        # 创建配置
        config = LLMConfig.from_env("deepseek")
        cli = AgentCLI(llm_config=config)
        
        # 设置测试上下文
        cli.context = {
            "task": "创建用户认证系统",
            "file_content": "用户模型已定义"
        }
        
        # 测试决策
        thought = "已经理解了用户模型，现在需要生成认证相关的代码"
        step = "生成JWT认证代码"
        
        print(f"输入思考: {thought}")
        print(f"当前步骤: {step}")
        print("\n调用LLM进行决策...")
        
        action = cli._decide_action(thought, step)
        
        print(f"\nLLM决策结果:")
        print(f"  动作类型: {action.type.value}")
        print(f"  描述: {action.description}")
        if action.params:
            print(f"  参数: {json.dumps(action.params, indent=2, ensure_ascii=False)}")
        
        # 测试符号主义回退
        print("\n\n测试符号主义回退:")
        action_symbolic = cli._decide_action_symbolic(thought, step)
        print(f"  动作类型: {action_symbolic.type.value}")
        print(f"  描述: {action_symbolic.description}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_llm_planning():
    """测试LLM规划功能"""
    print("\n\n测试 LLM 规划功能")
    print("="*50)
    
    try:
        config = LLMConfig.from_env("deepseek")
        cli = AgentCLI(llm_config=config)
        
        task = "设计一个RESTful API用于图书管理"
        print(f"任务: {task}")
        print("\n调用LLM进行任务规划...")
        
        task_obj = cli.plan(task)
        
        print(f"\n规划结果:")
        print(f"  目标: {task_obj.goal}")
        print(f"  步骤数: {len(task_obj.steps)}")
        print("  执行步骤:")
        for i, step in enumerate(task_obj.steps, 1):
            print(f"    {i}. {step.name}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🤖 连接主义推理简单测试")
    print("="*50)
    print("此测试验证LLM决策和规划功能\n")
    
    test_llm_decision()
    test_llm_planning()
    
    print("\n\n✅ 测试完成！")
    print("如果看到了LLM的决策结果和规划步骤，说明连接主义推理正常工作。")