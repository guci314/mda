#!/usr/bin/env python3
"""
运行博客系统生成 - 测试参数映射修复
"""
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from agent_cli.core_v2_new import AgentCLI_V2
from agent_cli.core import LLMConfig

def main():
    # 从环境变量获取配置
    llm_config = LLMConfig.from_env()
    
    # 创建 Agent CLI
    agent = AgentCLI_V2(
        llm_config=llm_config,
        enable_context_compression=True,
        context_size_limit=30 * 1024  # 30KB
    )
    
    # 任务：生成博客管理系统代码
    task = """
基于 blog_management_psm.md 文件生成 FastAPI 博客管理系统代码。

要求：
1. 读取 PSM 文件理解系统设计
2. 生成完整的 FastAPI 项目结构到 blog_management_output_v2 目录
3. 包含所有必要的文件：
   - 数据模型 (models/)
   - API 路由 (api/)
   - 数据库配置 (database.py)
   - 主应用文件 (main.py)
   - 依赖文件 (requirements.txt)
   - 配置文件 (config.py, .env.example)
   - 项目说明 (README.md)
4. 确保所有文件都有实际内容，不能是空文件
5. 代码要符合 FastAPI 最佳实践
"""
    
    print("开始生成博客管理系统代码...")
    print(f"输出目录: blog_management_output_v2")
    print("=" * 60)
    
    success, result = agent.execute_task(task)
    
    print("\n" + "=" * 60)
    print(f"执行结果: {'✅ 成功' if success else '❌ 失败'}")
    print(f"消息: {result}")
    
    # 验证生成的文件
    output_dir = Path("blog_management_output_v2")
    if output_dir.exists():
        print("\n生成的文件:")
        for file_path in output_dir.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  {file_path.relative_to(output_dir)} ({size} bytes)")

if __name__ == "__main__":
    main()