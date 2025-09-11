#!/usr/bin/env python3
"""
使用NLPL程序让Agent生成PSM
"""

import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from core.kimi_react_agent import KimiReactAgent
from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel

def generate_psm_with_nlpl(use_kimi=True):
    """使用NLPL程序生成PSM"""
    
    work_dir = Path("./output/blog_nlpl")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 清空目录
    for f in work_dir.glob("*"):
        if f.is_file():
            f.unlink()
    
    print("="*80)
    print(f"使用NLPL程序生成PSM文档 - {'Kimi' if use_kimi else 'DeepSeek'}")
    print("="*80)
    
    # 根据选择创建不同的Agent
    if use_kimi:
        executor_agent = KimiReactAgent(
            work_dir=str(work_dir),
            model="kimi-k2-turbo-preview",
            # knowledge_files=[
            #     "knowledge/nltm/executor_agent_as_tool.md",
            #     "knowledge/mda/pim_to_psm_knowledge.md"
            # ],
            interface="""NLPL执行器 - 执行自然语言程序

# 能力：
- 读取并执行NLPL程序
- 管理程序状态
- 执行定义的步骤

# 输入：
- NLPL程序文件
- 初始状态

# 输出：
- 执行结果
- 最终状态
"""
        )
    else:
        # 使用DeepSeek配置
        config = ReactAgentConfig(
            work_dir=str(work_dir),
            memory_level=MemoryLevel.NONE,
            # knowledge_files=[
            #     "knowledge/nltm/executor_agent_as_tool.md",
            #     "knowledge/mda/pim_to_psm_knowledge.md"
            # ],
            interface="""NLPL执行器 - 执行自然语言程序

# 能力：
- 读取并执行NLPL程序
- 管理程序状态
- 执行定义的步骤

# 输入：
- NLPL程序文件
- 初始状态

# 输出：
- 执行结果
- 最终状态
""",
            llm_model="deepseek-chat",
            llm_base_url="https://api.deepseek.com/v1",
            llm_api_key_env="DEEPSEEK_API_KEY",
            llm_temperature=0
        )
        executor_agent = GenericReactAgent(config, name="nlpl_executor")
    
    # 读取NLPL程序
    nlpl_file = Path(__file__).parent / "knowledge/nltm/psm_generation.md"
    with open(nlpl_file, 'r', encoding='utf-8') as f:
        nlpl_program = f.read()
    
    # 创建初始状态
    initial_state = {
        "输入": {
            "pim_file": "/home/guci/aiProjects/mda/pim-compiler/examples/blog.md",
            "psm_file": "blog_psm.md"
        },
        "进度": {
            "当前章节": 0,
            "已完成章节": [],
            "章节内容缓存": ""
        },
        "输出": {
            "psm_内容": "",
            "验证结果": None
        },
        "完成": False
    }
    
    # 将NLPL程序和初始状态写入工作目录
    (work_dir / "program.md").write_text(nlpl_program)
    (work_dir / "state.json").write_text(json.dumps(initial_state, ensure_ascii=False, indent=2))
    
    # 执行任务
    print("\n📋 NLPL程序已准备")
    print(f"工作目录: {work_dir}")
    print("\n🚀 开始执行NLPL程序...")
    
    result = executor_agent.execute_task("""
你是NLPL执行器。请执行以下任务：

1. 读取 program.md 文件，理解PSM生成程序
2. 读取 state.json 文件，获取初始状态
3. 执行 program.md

成功条件：
生成的文件包含所有5个核心章节

""")
    
    print("\n✅ 执行完成")
    print("-" * 40)
    print(result[:500] if result else "无结果")
    
    # 检查生成的文件
    psm_file = work_dir / "blog_psm.md"
    if psm_file.exists():
        size = psm_file.stat().st_size
        print(f"\n📄 PSM文件已生成: {psm_file}")
        print(f"   文件大小: {size} bytes")
        
        # 验证章节
        content = psm_file.read_text()
        required_sections = [
            "Domain Models",
            "Service Layer", 
            "REST API Design",
            "Application Configuration",
            "Testing Specifications"
        ]
        
        print("\n📊 章节验证:")
        for section in required_sections:
            if section in content:
                print(f"   ✅ {section}")
            else:
                print(f"   ❌ {section} (缺失)")
    else:
        print("\n❌ PSM文件未生成")
    
    return work_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="使用NLPL程序生成PSM文档")
    parser.add_argument(
        "--model", 
        choices=["kimi", "deepseek"], 
        default="deepseek",
        help="选择使用的模型 (default: kimi)"
    )
    args = parser.parse_args()
    
    use_kimi = args.model == "kimi"
    
    # 检查对应的API密钥
    if use_kimi:
        if not os.getenv("MOONSHOT_API_KEY"):
            print("❌ 请设置MOONSHOT_API_KEY环境变量")
            exit(1)
    else:
        if not os.getenv("DEEPSEEK_API_KEY"):
            print("❌ 请设置DEEPSEEK_API_KEY环境变量")
            exit(1)
    
    work_dir = generate_psm_with_nlpl(use_kimi=use_kimi)
    print(f"\n完成！文件位于: {work_dir}")