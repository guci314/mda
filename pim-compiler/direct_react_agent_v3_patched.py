#!/usr/bin/env python3
"""改进版ReactAgentGenerator v3 - 带Pydantic兼容性修复"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 修复 Pydantic 兼容性
import fix_pydantic_compatibility

# 导入原始模块
from direct_react_agent_v3_fixed import *

# 覆盖 _create_memory 方法，使用 WindowMemory 替代 SummaryBufferMemory
original_create_memory = ReactAgentGenerator._create_memory

def new_create_memory(self):
    """根据配置创建记忆系统 - 修复版"""
    if self.config.memory_level == MemoryLevel.NONE:
        logger.info("Memory disabled - using stateless mode")
        return None
        
    elif self.config.memory_level == MemoryLevel.SMART:
        # 使用 ConversationBufferWindowMemory 替代 ConversationSummaryBufferMemory
        logger.info(f"Using smart memory (window buffer) with k=50 messages")
        from langchain.memory import ConversationBufferWindowMemory
        
        # 计算合理的窗口大小
        # 假设平均每条消息 200 tokens，30000 tokens 约等于 150 条消息
        # 保守设置为 50 条消息（25轮对话）
        k = min(50, self.config.max_token_limit // 600)
        
        return ConversationBufferWindowMemory(
            k=k,  # 保留最近 k 条消息
            memory_key="chat_history",
            return_messages=True
        )
        
    elif self.config.memory_level == MemoryLevel.PRO:
        # PRO 模式保持不变
        return original_create_memory(self)

# 应用补丁
ReactAgentGenerator._create_memory = new_create_memory

# 更新说明文字
def new_main():
    """主函数 - 支持三级记忆配置（Pydantic兼容版）"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="ReactAgent Generator with Memory Support (Pydantic v1 Compatible)")
    parser.add_argument("--memory", choices=["none", "smart", "pro"], 
                       default="smart", help="Memory level: none, smart (window), or pro (sqlite)")
    parser.add_argument("--session-id", type=str, help="Session ID for persistent memory")
    parser.add_argument("--max-tokens", type=int, default=30000,
                       help="Max token limit for smart memory (used to calculate window size)")
    parser.add_argument("--pim-file", type=str, 
                       default="../models/domain/用户管理_pim.md", 
                       help="Path to PIM file")
    parser.add_argument("--output-dir", type=str, 
                       default="output/react_agent_v3", 
                       help="Output directory")
    args = parser.parse_args()
    
    # 配置
    pim_file = Path(args.pim_file)
    output_dir = Path(args.output_dir)
    
    # 根据memory参数映射到MemoryLevel
    memory_mapping = {
        "none": MemoryLevel.NONE,
        "smart": MemoryLevel.SMART,
        "pro": MemoryLevel.PRO
    }
    memory_level = memory_mapping[args.memory]
    
    logger.info(f"Using generator: react-agent (v3 - Pydantic Compatible)")
    logger.info(f"Memory level: {args.memory}")
    if args.memory == "smart":
        logger.info("Note: Using ConversationBufferWindowMemory due to Pydantic v1")
    logger.info(f"Target platform: fastapi")
    logger.info(f"Output directory: {output_dir}")
    
    # 其余代码与原版相同...
    # 检查PIM文件
    if not pim_file.exists():
        logger.error(f"PIM file not found: {pim_file}")
        return 1
    
    # 读取PIM内容
    pim_content = pim_file.read_text(encoding='utf-8')
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建配置 - 包含记忆配置
    config = GeneratorConfig(
        platform="fastapi",
        output_dir=str(output_dir),
        additional_config={},
        memory_level=memory_level,
        session_id=args.session_id,
        max_token_limit=args.max_tokens
    )
    
    try:
        # 创建生成器
        generator = ReactAgentGenerator(config)
        logger.info("Initialized ReactAgentGenerator v3 (Pydantic v1 Compatible)")
        logger.info(f"Starting compilation of {pim_file}")
        
        # 步骤1：生成PSM
        logger.info("Step 1: Generating PSM...")
        start_time = time.time()
        psm_content = generator.generate_psm(pim_content)
        psm_time = time.time() - start_time
        logger.info(f"PSM generated in {psm_time:.2f} seconds")
        
        # 保存PSM
        psm_file = output_dir / "user_management_psm.md"
        psm_file.write_text(psm_content, encoding='utf-8')
        
        # 步骤2：生成代码
        logger.info("Step 2: Generating code with proper package structure...")
        print("\n[1m> Entering new AgentExecutor chain...[0m")
        
        start_time = time.time()
        generator.generate_code(psm_content, str(output_dir))
        code_time = time.time() - start_time
        
        print("[1m> Finished chain.[0m")
        logger.info(f"Code generated and tested in {code_time:.2f} seconds")
        
        # 统计
        python_files = list(output_dir.rglob("*.py"))
        total_files = list(output_dir.rglob("*.*"))
        
        print("\n" + "=" * 50)
        print("✅ Compilation Successful!")
        print("=" * 50)
        print(f"Generator: react-agent v3 (Pydantic v1 Compatible)")
        print(f"Platform: fastapi")
        print(f"Output: {output_dir}")
        print(f"\nMemory Configuration:")
        print(f"  - Level: {args.memory}")
        if args.memory == "smart":
            k = min(50, config.max_token_limit // 600)
            print(f"  - Window size: {k} messages")
            print(f"  - Note: Using WindowMemory due to Pydantic v1")
        elif args.memory == "pro":
            print(f"  - Session ID: {config.session_id}")
            print(f"  - Database: {config.db_path}")
        print(f"\nStatistics:")
        print(f"  - PSM generation: {psm_time:.2f}s")
        print(f"  - Code generation & testing: {code_time:.2f}s")
        print(f"  - Total time: {psm_time + code_time:.2f}s")
        print(f"  - Files generated: {len(total_files)}")
        print(f"  - Python files: {len(python_files)}")
        
        # 保存日志
        log_file = output_dir / "compile_output.log"
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Compilation completed at {datetime.now()}\n")
            f.write(f"Total time: {psm_time + code_time:.2f}s\n")
            f.write(f"Files generated: {len(total_files)}\n")
        
        print("\nNext steps:")
        print(f"  cd {output_dir}")
        print("  python -m uvicorn <app_name>.main:app --reload")
        
        return 0
        
    except Exception as e:
        logger.error(f"Compilation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

# 替换主函数
if __name__ == "__main__":
    sys.exit(new_main())