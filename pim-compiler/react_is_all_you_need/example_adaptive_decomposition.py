#!/usr/bin/env python3
"""
自适应任务分解示例 - 展示失败驱动的任务分解

这个示例展示了轻量级元认知如何工作：
1. 尝试执行复杂任务
2. 如果失败或输出不完整，自动分解为更小的步骤
3. 逐步执行子任务
"""

import os
from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel

def test_with_different_models():
    """测试不同模型处理复杂任务的能力"""
    
    # 复杂任务 - 可能会让弱模型失败
    complex_task = """
    生成一个完整的用户管理系统，包括：
    1. SQLAlchemy模型定义（User, Role, Permission）
    2. Pydantic schemas用于数据验证
    3. FastAPI路由实现所有CRUD操作
    4. JWT认证中间件
    5. 单元测试覆盖所有端点
    
    要求所有代码都要完整，不要省略任何部分。
    """
    
    # 测试1：使用强模型（Gemini）
    print("=" * 60)
    print("测试1：使用Gemini（强模型）")
    print("=" * 60)
    
    if os.getenv("GEMINI_API_KEY"):
        gemini_config = ReactAgentConfig(
            work_dir="output/gemini_test",
            memory_level=MemoryLevel.SMART,
            llm_model="gemini-2.5-flash",
            llm_base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            llm_api_key_env="GEMINI_API_KEY",
            llm_temperature=0
        )
        gemini_agent = GenericReactAgent(gemini_config, name="gemini_agent")
        
        print("Gemini通常能一次性完成整个任务...")
        result = gemini_agent.execute_task(complex_task)
        print(f"结果：{'成功' if result else '失败'}")
    else:
        print("跳过：未设置GEMINI_API_KEY")
    
    # 测试2：使用弱模型（Kimi）
    print("\n" + "=" * 60)
    print("测试2：使用Kimi（弱模型）")
    print("=" * 60)
    
    if os.getenv("MOONSHOT_API_KEY"):
        kimi_config = ReactAgentConfig(
            work_dir="output/kimi_test",
            memory_level=MemoryLevel.SMART,
            llm_model="kimi-k2-turbo-preview",
            llm_base_url="https://api.moonshot.cn/v1",
            llm_api_key_env="MOONSHOT_API_KEY",
            llm_temperature=0
        )
        kimi_agent = GenericReactAgent(kimi_config, name="kimi_agent")
        
        print("Kimi可能会失败，触发自适应分解...")
        print("\n预期行为：")
        print("1. 首次尝试可能失败或输出不完整")
        print("2. Agent读取adaptive_task_decomposition.md知识")
        print("3. 根据知识自动分解任务")
        print("4. 逐步执行子任务")
        
        result = kimi_agent.execute_task(complex_task)
        print(f"\n最终结果：{'成功' if result else '需要人工介入'}")
    else:
        print("跳过：未设置MOONSHOT_API_KEY")

def simulate_failure_recovery():
    """模拟失败恢复场景"""
    
    print("\n" + "=" * 60)
    print("模拟失败恢复场景")
    print("=" * 60)
    
    # 创建一个会触发分解的任务
    problematic_task = """
    执行以下任务：
    1. 生成10个不同的API端点
    2. 每个端点都要有完整的代码实现
    3. 包含错误处理和日志记录
    4. 生成对应的测试代码
    
    注意：这个任务故意设计得很大，以触发分解机制。
    """
    
    config = ReactAgentConfig(
        work_dir="output/failure_recovery",
        memory_level=MemoryLevel.SMART,
        # 使用默认的DeepSeek模型
    )
    agent = GenericReactAgent(config, name="recovery_agent")
    
    print("执行可能触发分解的任务...")
    print("\n任务内容：")
    print(problematic_task)
    print("\n开始执行...")
    
    # Agent会自动处理失败情况
    # 因为已经加载了adaptive_task_decomposition.md
    # 它知道如何识别失败信号并进行分解
    result = agent.execute_task(problematic_task)
    
    print("\n执行完成！")
    print("检查output/failure_recovery目录查看生成的文件")

def main():
    """主函数"""
    print("自适应任务分解演示")
    print("=" * 60)
    print("这个演示展示了轻量级元认知如何工作：")
    print("- 不需要复杂的Python类")
    print("- 通过知识文件指导分解")
    print("- 失败驱动而非预先规划")
    print("=" * 60)
    
    # 运行测试
    test_with_different_models()
    
    # 模拟失败恢复
    simulate_failure_recovery()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("关键要点：")
    print("1. 元认知是通过知识文件实现的，不是代码")
    print("2. 分解是失败驱动的，不是预先规划")
    print("3. 每个Agent都自动具备这种能力")
    print("=" * 60)

if __name__ == "__main__":
    main()