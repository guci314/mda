#!/usr/bin/env python3
"""MDA Demo - PSM Agent for PIM to PSM transformation"""

import os
# Disable cache for better performance with large cache files
# Uncomment the line below to disable cache
os.environ['DISABLE_LANGCHAIN_CACHE'] = 'true'

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from pathlib import Path

# 如果使用 Gemini 直连需要导入 httpx（OpenRouter不需要）
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# PSM Agent configuration
psm_config = ReactAgentConfig(
    work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/mda_demo",
    memory_level=MemoryLevel.SMART,
    knowledge_files=["knowledge/mda/pim_to_psm_knowledge.md"],
    llm_model="deepseek-chat",
    llm_base_url="https://api.deepseek.com/v1",
    llm_api_key_env="DEEPSEEK_API_KEY",
    llm_temperature=0,
    enable_project_exploration=False  # 禁用项目探索
)

# Create PSM Generation Agent
psm_generation_agent = GenericReactAgent(psm_config, name="psm_generation_agent")
psm_generation_agent.interface = """PSM转换专家 - PIM到PSM转换器

能力：
- 将PIM（平台无关模型）转换为PSM（平台特定模型）

用法：
提供PIM文档路径或内容，我将生成相应的PSM文档。

示例："将library_borrowing_system_pim.md转换为PSM"
"""

# FastAPI App Generation Agent configuration
fastapi_config = ReactAgentConfig(
    work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/mda_demo",
    memory_level=MemoryLevel.SMART,
    knowledge_files=["knowledge/mda/fastapi_generation_knowledge.md"],
    llm_model="deepseek-chat",
    llm_base_url="https://api.deepseek.com/v1",
    llm_api_key_env="DEEPSEEK_API_KEY",
    llm_temperature=0,
    enable_project_exploration=False  # 禁用项目探索
)

# Create FastAPI App Generation Agent
fastapi_app_generation_agent = GenericReactAgent(fastapi_config, name="fastapi_app_generation_agent")
fastapi_app_generation_agent.interface = """FastAPI应用生成专家 - PSM到FastAPI代码生成器

能力：
- 从PSM文档生成完整的FastAPI应用代码

用法：
提供PSM文档路径或内容，我将生成相应的FastAPI应用。

示例："从library_borrowing_psm.md生成FastAPI应用"
"""

# ========== Claude Sonnet 4 配置 (通过 OpenRouter) ==========
# PSM Generation Agent with Claude Sonnet (via OpenRouter)
psm_config_claude = ReactAgentConfig(
    work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/mda_demo",
    memory_level=MemoryLevel.SMART,
    knowledge_files=["knowledge/mda/pim_to_psm_knowledge.md"],
    llm_model="anthropic/claude-sonnet-4",  # OpenRouter 的 Claude Sonnet 4 模型
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY",  # 需要设置 OPENROUTER_API_KEY 环境变量
    llm_temperature=0,
    context_window=200000,  # Claude supports 200k tokens context
    enable_project_exploration=False  # 禁用项目探索
)

# FastAPI App Generation Agent with Claude Sonnet (via OpenRouter)
fastapi_config_claude = ReactAgentConfig(
    work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/mda_demo",
    memory_level=MemoryLevel.SMART,
    knowledge_files=["knowledge/mda/fastapi_generation_knowledge.md"],
    llm_model="anthropic/claude-sonnet-4",  # OpenRouter 的 Claude Sonnet 4 模型
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY",  # 需要设置 OPENROUTER_API_KEY 环境变量
    llm_temperature=0,
    context_window=200000,  # Claude supports 200k tokens context
    enable_project_exploration=False  # 禁用项目探索
)

# Create Claude Agents
psm_generation_agent_claude = GenericReactAgent(psm_config_claude, name="psm_generation_agent_claude")
psm_generation_agent_claude.interface = """PSM转换专家 (Claude) - PIM到PSM转换器

能力：
- 将PIM（平台无关模型）转换为PSM（平台特定模型）

用法：
提供PIM文档路径或内容，我将生成相应的PSM文档。

示例："将library_borrowing_system_pim.md转换为PSM"
"""

fastapi_app_generation_agent_claude = GenericReactAgent(fastapi_config_claude, name="fastapi_app_generation_agent_claude")
fastapi_app_generation_agent_claude.interface = """FastAPI应用生成专家 (Claude) - PSM到FastAPI代码生成器

能力：
- 从PSM文档生成完整的FastAPI应用代码

用法：
提供PSM文档路径或内容，我将生成相应的FastAPI应用。

示例："从library_borrowing_psm.md生成FastAPI应用"
"""

# ========== Gemini 配置 (通过 OpenRouter) ==========
# PSM Generation Agent with Gemini (via OpenRouter)
psm_config_gemini = ReactAgentConfig(
    work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/mda_demo",
    memory_level=MemoryLevel.SMART,
    knowledge_files=["knowledge/mda/pim_to_psm_knowledge.md"],
    llm_model="google/gemini-2.5-pro",  # OpenRouter 的 Gemini 模型
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY",  # 需要设置 OPENROUTER_API_KEY 环境变量
    llm_temperature=0,
    context_window=1000000,  # Gemini 支持 1M tokens context
    enable_project_exploration=False  # 禁用项目探索
)

# FastAPI App Generation Agent with Gemini (via OpenRouter)
fastapi_config_gemini = ReactAgentConfig(
    work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/mda_demo",
    memory_level=MemoryLevel.SMART,
    knowledge_files=["knowledge/mda/fastapi_generation_knowledge.md"],
    llm_model="google/gemini-2.5-pro",  # OpenRouter 的 Gemini 模型
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY",  # 需要设置 OPENROUTER_API_KEY 环境变量
    llm_temperature=0,
    context_window=1000000,  # Gemini 支持 1M tokens context
    enable_project_exploration=False  # 禁用项目探索
)

# Create Gemini Agents
psm_generation_agent_gemini = GenericReactAgent(psm_config_gemini, name="psm_generation_agent_gemini")
psm_generation_agent_gemini.interface = """PSM转换专家 (Gemini) - PIM到PSM转换器

能力：
- 将PIM（平台无关模型）转换为PSM（平台特定模型）

用法：
提供PIM文档路径或内容，我将生成相应的PSM文档。

示例："将library_borrowing_system_pim.md转换为PSM"
"""

fastapi_app_generation_agent_gemini = GenericReactAgent(fastapi_config_gemini, name="fastapi_app_generation_agent_gemini")
fastapi_app_generation_agent_gemini.interface = """FastAPI应用生成专家 (Gemini) - PSM到FastAPI代码生成器

能力：
- 从PSM文档生成完整的FastAPI应用代码

用法：
提供PSM文档路径或内容，我将生成相应的FastAPI应用。

示例："从library_borrowing_psm.md生成FastAPI应用"
"""

def clean_output_directory(work_dir):
    """清理输出目录，只保留PIM文件"""
    import os
    import shutil
    
    print(f"\n清理目录: {work_dir}")
    
    # 保存PIM文件的列表
    pim_files = []
    
    # 遍历目录，找出所有PIM文件（特征：*_pim.md）
    for file in os.listdir(work_dir):
        file_path = os.path.join(work_dir, file)
        if os.path.isfile(file_path):
            # PIM文件的特征：以_pim.md结尾
            if file.endswith('_pim.md'):
                pim_files.append(file)
                print(f"  保留PIM文件: {file}")
    
    # 删除所有其他文件和目录
    for item in os.listdir(work_dir):
        item_path = os.path.join(work_dir, item)
        if item not in pim_files:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"  删除目录: {item}")
            else:
                os.remove(item_path)
                print(f"  删除文件: {item}")
    
    print("清理完成！\n")

def main_deepseek():
    """Main function to demonstrate MDA agents"""
    
    # 清理输出目录
    clean_output_directory("/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/mda_demo")
    
    # PSM Generation
    print("=" * 60)
    print("PSM生成Agent已配置:")
    print(f"  模型: {psm_config.llm_model}")
    print(f"  工作目录: {psm_config.work_dir}")
    print(f"  知识文件: {psm_config.knowledge_files}")
    print(f"  上下文窗口: {psm_config.context_window} tokens")
    print(f"  内存令牌限制: {psm_config.max_token_limit}")
    
    # PSM generation task
    psm_task = """
    执行以下步骤生成PSM文档：
    
    1. 使用工具读取library_borrowing_system_pim.md文件，分析其PIM内容
    
    2. 根据知识文件中的PSM文档结构，将PIM转换为FastAPI平台的PSM，必须包含：
       - Domain Models（领域模型）
       - Service Layer（服务层）
       - REST API Design（API设计）
       - Application Configuration（应用配置）
       - Testing Specifications（测试规范）
    
    3. 【重要】使用文件写入工具创建library_borrowing_system_psm.md文件
       - 必须调用WriteFileSystemTool或类似工具
       - 文件内容必须是完整的Markdown格式PSM文档
       - 不要只是输出内容，必须实际创建文件
    
    4. 创建文件后，使用工具验证：
       - 检查library_borrowing_system_psm.md文件是否存在
       - 读取文件内容，确认包含所有必需的PSM章节
       - 如果文件不存在，重新创建
    
    注意：这不是一个分析任务，而是一个文件生成任务。必须使用工具创建实际的.md文件。
    """
    
    print("\n[步骤 1] 从PIM生成PSM...")
    print("任务:", psm_task)
    
    psm_result = psm_generation_agent.execute_task(psm_task)
    print("\nPSM生成完成！")
    
    # FastAPI App Generation
    print("\n" + "=" * 60)
    print("FastAPI应用生成Agent已配置:")
    print(f"  模型: {fastapi_config.llm_model}")
    print(f"  工作目录: {fastapi_config.work_dir}")
    print(f"  知识文件: {fastapi_config.knowledge_files}")
    
    # Task 1: Generate FastAPI App
    generate_app_task = """
    读取library_borrowing_system_psm.md文件，生成完整的FastAPI应用代码。
    创建所有必要的文件和目录结构，包括models、schemas、services、routers等。
    生成requirements.txt文件，包含所有必要的依赖。
    """
    
    print("\n[步骤 2.1] 生成FastAPI应用代码...")
    print("任务:", generate_app_task)
    fastapi_result_1 = fastapi_app_generation_agent.execute_task(generate_app_task)
    
    # Task 2: Create and Fix Tests
    create_test_task = """
    为生成的FastAPI应用创建测试文件。
    在tests目录下创建test_main.py，包含基本的API端点测试。
    确保测试文件可以被pytest正确识别和运行。
    """
    
    print("\n[步骤 2.2] 创建和修正测试...")
    print("任务:", create_test_task)
    fastapi_result_2 = fastapi_app_generation_agent.execute_task(create_test_task)
    
    # Task 3: Run App and Tests with 100% Success Requirement
    run_app_task = """
    运行生成的FastAPI应用并验证，要求达到以下成功标准：
    
    1. 安装requirements.txt中的所有依赖
    
    2. 运行pytest执行所有测试，必须满足：
       - 所有测试必须100%通过，不允许有任何失败
       - 如果有测试失败，必须分析失败原因并修复代码
       - 修复后重新运行测试，直到所有测试全部通过
       - 循环执行"运行测试→分析失败→修复代码→重新测试"直到达到100%通过率
    
    3. 只有在所有测试100%通过后，才能继续：
       - 使用uvicorn启动应用，确认应用能正常运行
       - 使用curl --noproxy "*" 测试健康检查端点 http://localhost:8000/
    
    成功标准：
    - pytest显示所有测试passed，0 failed
    - 测试通过率必须达到100%
    - 不允许跳过任何失败的测试
    
    注意：这是一个硬性要求，必须修复所有测试失败，不能仅仅运行测试就认为完成任务。
    """
    
    print("\n[步骤 2.3] 运行应用和测试 - 要求100%测试通过...")
    print("任务:", run_app_task)
    fastapi_result_3 = fastapi_app_generation_agent.execute_task(run_app_task)
    
    print("\nFastAPI应用生成、测试和运行完成！")
    
    print("\n" + "=" * 60)
    print("MDA流水线成功完成！")
    print("生成的文件位于:", psm_config.work_dir)

def main_claude():
    """Main function to demonstrate MDA agents with Claude Sonnet"""
    
    # 清理输出目录
    clean_output_directory("/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/mda_demo")
    
    # PSM Generation
    print("=" * 60)
    print("PSM生成Agent已配置 (Claude Sonnet):")
    print(f"  模型: {psm_config_claude.llm_model}")
    print(f"  工作目录: {psm_config_claude.work_dir}")
    print(f"  知识文件: {psm_config_claude.knowledge_files}")
    print(f"  上下文窗口: {psm_config_claude.context_window} tokens")
    
    # PSM generation task
    psm_task = """
    执行以下步骤生成PSM文档：
    
    1. 使用工具读取library_borrowing_system_pim.md文件，分析其PIM内容
    
    2. 根据知识文件中的PSM文档结构，将PIM转换为FastAPI平台的PSM，必须包含：
       - Domain Models（领域模型）
       - Service Layer（服务层）
       - REST API Design（API设计）
       - Application Configuration（应用配置）
       - Testing Specifications（测试规范）
    
    3. 【重要】使用文件写入工具创建library_borrowing_system_psm.md文件
       - 必须调用WriteFileSystemTool或类似工具
       - 文件内容必须是完整的Markdown格式PSM文档
       - 不要只是输出内容，必须实际创建文件
    
    4. 创建文件后，使用工具验证：
       - 检查library_borrowing_system_psm.md文件是否存在
       - 读取文件内容，确认包含所有必需的PSM章节
       - 如果文件不存在，重新创建
    
    注意：这不是一个分析任务，而是一个文件生成任务。必须使用工具创建实际的.md文件。
    """
    
    print("\n[步骤 1] 从PIM生成PSM (使用Claude)...")
    print("任务:", psm_task)
    
    psm_result = psm_generation_agent_claude.execute_task(psm_task)
    print("\nPSM生成完成！")
    
    # FastAPI App Generation
    print("\n" + "=" * 60)
    print("FastAPI应用生成Agent已配置 (Claude Sonnet):")
    print(f"  模型: {fastapi_config_claude.llm_model}")
    print(f"  工作目录: {fastapi_config_claude.work_dir}")
    print(f"  知识文件: {fastapi_config_claude.knowledge_files}")
    
    # Task 1: Generate FastAPI App
    generate_app_task = """
    读取library_borrowing_system_psm.md文件，生成完整的FastAPI应用代码。
    创建所有必要的文件和目录结构，包括models、schemas、services、routers等。
    生成requirements.txt文件，包含所有必要的依赖。
    """
    
    print("\n[步骤 2.1] 生成FastAPI应用代码 (使用Claude)...")
    print("任务:", generate_app_task)
    fastapi_result_1 = fastapi_app_generation_agent_claude.execute_task(generate_app_task)
    
    # Task 2: Create and Fix Tests
    create_test_task = """
    为生成的FastAPI应用创建测试文件。
    在tests目录下创建test_main.py，包含基本的API端点测试。
    确保测试文件可以被pytest正确识别和运行。
    """
    
    print("\n[步骤 2.2] 创建和修正测试 (使用Claude)...")
    print("任务:", create_test_task)
    fastapi_result_2 = fastapi_app_generation_agent_claude.execute_task(create_test_task)
    
    # Task 3: Run App and Tests with 100% Success Requirement
    run_app_task = """
    运行生成的FastAPI应用并验证，要求达到以下成功标准：
    
    1. 安装requirements.txt中的所有依赖
    
    2. 运行pytest执行所有测试，必须满足：
       - 所有测试必须100%通过，不允许有任何失败
       - 如果有测试失败，必须分析失败原因并修复代码
       - 修复后重新运行测试，直到所有测试全部通过
       - 循环执行"运行测试→分析失败→修复代码→重新测试"直到达到100%通过率
    
    3. 只有在所有测试100%通过后，才能继续：
       - 使用uvicorn启动应用，确认应用能正常运行
       - 使用curl --noproxy "*" 测试健康检查端点 http://localhost:8000/
    
    成功标准：
    - pytest显示所有测试passed，0 failed
    - 测试通过率必须达到100%
    - 不允许跳过任何失败的测试
    
    注意：这是一个硬性要求，必须修复所有测试失败，不能仅仅运行测试就认为完成任务。
    """
    
    print("\n[步骤 2.3] 运行应用和测试 - 要求100%测试通过 (使用Claude)...")
    print("任务:", run_app_task)
    fastapi_result_3 = fastapi_app_generation_agent_claude.execute_task(run_app_task)
    
    print("\nFastAPI应用生成、测试和运行完成！")
    
    print("\n" + "=" * 60)
    print("MDA流水线成功完成 (Claude Sonnet)！")
    print("生成的文件位于:", psm_config_claude.work_dir)

def main_gemini():
    """Main function to demonstrate MDA agents with Gemini"""
    
    # 清理输出目录
    clean_output_directory("/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/mda_demo")
    
    # PSM Generation
    print("=" * 60)
    print("PSM生成Agent已配置 (Gemini):")
    print(f"  模型: {psm_config_gemini.llm_model}")
    print(f"  工作目录: {psm_config_gemini.work_dir}")
    print(f"  知识文件: {psm_config_gemini.knowledge_files}")
    print(f"  上下文窗口: {psm_config_gemini.context_window} tokens")
    
    # PSM generation task
    psm_task = """
    执行以下步骤生成PSM文档：
    
    1. 使用工具读取library_borrowing_system_pim.md文件，分析其PIM内容
    
    2. 根据知识文件中的PSM文档结构，将PIM转换为FastAPI平台的PSM，必须包含：
       - Domain Models（领域模型）
       - Service Layer（服务层）
       - REST API Design（API设计）
       - Application Configuration（应用配置）
       - Testing Specifications（测试规范）
    
    3. 【重要】使用文件写入工具创建library_borrowing_system_psm.md文件
       - 必须调用WriteFileSystemTool或类似工具
       - 文件内容必须是完整的Markdown格式PSM文档
       - 不要只是输出内容，必须实际创建文件
    
    4. 创建文件后，使用工具验证：
       - 检查library_borrowing_system_psm.md文件是否存在
       - 读取文件内容，确认包含所有必需的PSM章节
       - 如果文件不存在，重新创建
    
    注意：这不是一个分析任务，而是一个文件生成任务。必须使用工具创建实际的.md文件。
    """
    
    print("\n[步骤 1] 从PIM生成PSM (使用Gemini)...")
    print("任务:", psm_task)
    
    psm_result = psm_generation_agent_gemini.execute_task(psm_task)
    print("\nPSM生成完成！")
    
    # FastAPI App Generation
    print("\n" + "=" * 60)
    print("FastAPI应用生成Agent已配置 (Gemini):")
    print(f"  模型: {fastapi_config_gemini.llm_model}")
    print(f"  工作目录: {fastapi_config_gemini.work_dir}")
    print(f"  知识文件: {fastapi_config_gemini.knowledge_files}")
    
    # Task 1: Generate FastAPI App
    generate_app_task = """
    读取library_borrowing_system_psm.md文件，生成完整的FastAPI应用代码。
    创建所有必要的文件和目录结构，包括models、schemas、services、routers等。
    生成requirements.txt文件，包含所有必要的依赖。
    """
    
    print("\n[步骤 2.1] 生成FastAPI应用代码 (使用Gemini)...")
    print("任务:", generate_app_task)
    fastapi_result_1 = fastapi_app_generation_agent_gemini.execute_task(generate_app_task)
    
    # Task 2: Create and Fix Tests
    create_test_task = """
    为生成的FastAPI应用创建测试文件。
    在tests目录下创建test_main.py，包含基本的API端点测试。
    确保测试文件可以被pytest正确识别和运行。
    """
    
    print("\n[步骤 2.2] 创建和修正测试 (使用Gemini)...")
    print("任务:", create_test_task)
    fastapi_result_2 = fastapi_app_generation_agent_gemini.execute_task(create_test_task)
    
    # Task 3: Run App and Tests with 100% Success Requirement
    run_app_task = """
    运行生成的FastAPI应用并验证，要求达到以下成功标准：
    
    1. 安装requirements.txt中的所有依赖
    
    2. 运行pytest执行所有测试，必须满足：
       - 所有测试必须100%通过，不允许有任何失败
       - 如果有测试失败，必须分析失败原因并修复代码
       - 修复后重新运行测试，直到所有测试全部通过
       - 循环执行"运行测试→分析失败→修复代码→重新测试"直到达到100%通过率
    
    3. 只有在所有测试100%通过后，才能继续：
       - 使用uvicorn启动应用，确认应用能正常运行
       - 使用curl --noproxy "*" 测试健康检查端点 http://localhost:8000/
    
    成功标准：
    - pytest显示所有测试passed，0 failed
    - 测试通过率必须达到100%
    - 不允许跳过任何失败的测试
    
    注意：这是一个硬性要求，必须修复所有测试失败，不能仅仅运行测试就认为完成任务。
    """
    
    print("\n[步骤 2.3] 运行应用和测试 - 要求100%测试通过 (使用Gemini)...")
    print("任务:", run_app_task)
    fastapi_result_3 = fastapi_app_generation_agent_gemini.execute_task(run_app_task)
    
    print("\nFastAPI应用生成、测试和运行完成！")
    
    print("\n" + "=" * 60)
    print("MDA流水线成功完成 (Gemini)！")
    print("生成的文件位于:", psm_config_gemini.work_dir)

if __name__ == "__main__":
    import sys
    import time
    
    import os
    os.environ["http_proxy"] = "http://127.0.0.1:7890"
    os.environ["https_proxy"] = "http://127.0.0.1:7890"
    
    # # 根据命令行参数选择使用哪个模型
    # if len(sys.argv) > 1:
    #     if sys.argv[1] == "gemini":
    #         print("使用 Gemini 模型 (通过 OpenRouter)")
    #         main_gemini()
    #     elif sys.argv[1] == "claude":
    #         print("使用 Claude Sonnet 4 模型 (通过 OpenRouter)")
    #         main_claude()
    #     else:
    #         print("使用 DeepSeek 模型")
    #         main_deepseek()
    # else:
    #     # 默认使用 DeepSeek
    #     print("使用 DeepSeek 模型 (默认)")
    #     print("提示: 可以使用 'python mda_demo.py claude' 或 'python mda_demo.py gemini' 选择其他模型")
    #     main_deepseek()
    
    
    # main_gemini()
    main_deepseek()
    # main_claude()
    # 等待一小段时间让后台任务完成或被正确取消
    time.sleep(10)
    print("\n程序执行完成！")