#!/usr/bin/env python3
"""
使用 Agent CLI v2 生成博客管理系统代码
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from agent_cli.core import LLMConfig
from agent_cli.core_v2_new import AgentCLI_V2


def generate_blog_system():
    """生成博客管理系统"""
    print("=== 使用 Agent CLI v2 生成博客管理系统 ===\n")
    
    # 定义任务
    task = """根据 blog_management_psm.md 文件生成完整的 FastAPI 博客管理系统。
需要生成以下内容：
1. 完整的项目结构（按照 PSM 中定义的目录结构）
2. 所有数据模型（models/）
3. 所有 API 路由（api/）
4. 认证和安全功能（core/）
5. Pydantic schemas（schemas/）
6. 数据库配置（database.py）
7. 主应用文件（main.py）
8. 配置文件（config.py）
9. 工具函数（utils/）
10. 依赖文件（requirements.txt）
11. 环境变量示例（.env.example）
12. 项目说明（README.md）

将所有文件生成到 blog_management_output 目录下。
确保代码结构清晰、功能完整、可以直接运行。"""
    
    # 配置
    try:
        llm_config = LLMConfig.from_env()
        
        # 创建 Agent CLI，启用压缩功能处理大量生成的文件
        agent = AgentCLI_V2(
            llm_config=llm_config,
            enable_context_compression=True,
            context_size_limit=30 * 1024,  # 30KB
            recent_file_window=5,  # 保护最近5个文件
            max_actions_per_step=20  # 允许每步更多动作
        )
        
        print("Agent CLI v2 配置:")
        print(f"- 提供商: {llm_config.provider}")
        print(f"- 模型: {llm_config.model}")
        print(f"- 压缩功能: 已启用")
        print(f"- 每步最大动作数: 20")
        print()
        
        # 执行任务
        print("开始生成代码...")
        print(f"任务: {task}\n")
        
        success, result = agent.execute_task(task)
        
        if success:
            print(f"\n✅ 代码生成成功！")
            print(f"结果: {result}")
            
            # 显示生成的文件
            output_dir = "blog_management_output"
            if os.path.exists(output_dir):
                print(f"\n生成的文件在: {output_dir}")
                # 使用 tree 命令显示目录结构
                subprocess.run(["tree", output_dir], capture_output=False)
        else:
            print(f"\n❌ 代码生成失败！")
            print(f"错误: {result}")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


def run_in_background():
    """在后台运行代码生成任务"""
    print("=== 后台运行博客系统代码生成 ===\n")
    
    # 日志文件
    log_file = "blog_generation.log"
    pid_file = "blog_generation.pid"
    
    # 使用 Agent CLI 命令行方式运行
    cmd = [
        sys.executable, "-m", "agent_cli", "run",
        """根据 blog_management_psm.md 文件生成完整的 FastAPI 博客管理系统。
需要生成以下内容：
1. 完整的项目结构（按照 PSM 中定义的目录结构）
2. 所有数据模型（models/）
3. 所有 API 路由（api/）
4. 认证和安全功能（core/）
5. Pydantic schemas（schemas/）
6. 数据库配置（database.py）
7. 主应用文件（main.py）
8. 配置文件（config.py）
9. 工具函数（utils/）
10. 依赖文件（requirements.txt）
11. 环境变量示例（.env.example）
12. 项目说明（README.md）

将所有文件生成到 blog_management_output 目录下。
确保代码结构清晰、功能完整、可以直接运行。""",
        "--max-actions", "20"
    ]
    
    print(f"命令: {' '.join(cmd)}")
    print(f"日志文件: {log_file}")
    print(f"PID 文件: {pid_file}\n")
    
    # 启动后台进程
    with open(log_file, "w") as log:
        process = subprocess.Popen(
            cmd,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
    # 保存 PID
    with open(pid_file, "w") as f:
        f.write(str(process.pid))
        
    print(f"✓ 已在后台启动，PID: {process.pid}")
    print(f"\n使用以下命令监控:")
    print(f"  tail -f {log_file}")
    print(f"\n或运行监控脚本:")
    print(f"  python monitor_blog_generation.py")
    
    return process.pid


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="生成博客管理系统")
    parser.add_argument("--background", "-b", action="store_true", 
                       help="在后台运行")
    
    args = parser.parse_args()
    
    if args.background:
        run_in_background()
    else:
        generate_blog_system()