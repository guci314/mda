#!/usr/bin/env python3
"""使用官方ReactAgentGenerator编译PIM"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime
import time

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# 直接导入需要的类
from src.compiler.generators.impl.react_agent_generator import ReactAgentGenerator
from src.compiler.generators.base_generator import GeneratorConfig

def main():
    """主函数"""
    # 配置
    pim_file = Path("../models/domain/用户管理_pim.md")
    output_dir = Path("output/react_agent_official")
    
    logger.info(f"Using generator: react-agent")
    logger.info(f"Target platform: fastapi")
    logger.info(f"Output directory: {output_dir}")
    
    # 检查PIM文件
    if not pim_file.exists():
        logger.error(f"PIM file not found: {pim_file}")
        return 1
    
    # 读取PIM内容
    pim_content = pim_file.read_text(encoding='utf-8')
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建配置
    config = GeneratorConfig(
        platform="fastapi",
        output_dir=str(output_dir),
        additional_config={}
    )
    
    try:
        # 创建生成器
        generator = ReactAgentGenerator(config)
        logger.info("Initialized ConfigurableCompiler with generator: react-agent")
        logger.info(f"Starting compilation of {pim_file}")
        logger.info("Using generator: react-agent")
        logger.info("Target platform: fastapi")
        
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
        logger.info("Step 2: Generating code...")
        print("\n[1m> Entering new AgentExecutor chain...[0m")
        
        start_time = time.time()
        generator.generate_code(psm_content, str(output_dir))
        code_time = time.time() - start_time
        
        print("[1m> Finished chain.[0m")
        logger.info(f"Code generated in {code_time:.2f} seconds")
        
        # 统计
        python_files = list(output_dir.rglob("*.py"))
        total_files = list(output_dir.rglob("*.*"))
        
        print("\n" + "=" * 50)
        print("✅ Compilation Successful!")
        print("=" * 50)
        print(f"Generator: react-agent")
        print(f"Platform: fastapi")
        print(f"Output: {output_dir}")
        print(f"\nStatistics:")
        print(f"  - PSM generation: {psm_time:.2f}s")
        print(f"  - Code generation: {code_time:.2f}s")
        print(f"  - Total time: {psm_time + code_time:.2f}s")
        print(f"  - Files generated: {len(total_files)}")
        print(f"  - Python files: {len(python_files)}")
        
        print("\nNext steps:")
        print(f"  cd {output_dir}/generated")
        print("  pip install -r requirements.txt")
        print("  uvicorn main:app --reload")
        
        return 0
        
    except Exception as e:
        logger.error(f"Compilation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())