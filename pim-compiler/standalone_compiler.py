#!/usr/bin/env python3
"""独立的编译脚本，直接使用ReactAgentGenerator"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# 导入必要的库
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def setup_logger(name):
    """简单的日志设置"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)

def main():
    """主函数"""
    logger = setup_logger(__name__)
    
    # 配置参数
    pim_file = Path("../models/domain/用户管理_pim.md")
    generator_type = "react-agent"
    platform = "fastapi"
    output_dir = Path("output/react_agent_enhanced_v3")
    
    logger.info(f"Using generator: {generator_type}")
    logger.info(f"Target platform: {platform}")
    logger.info(f"Output directory: {output_dir}")
    
    # 检查PIM文件
    if not pim_file.exists():
        logger.error(f"PIM file not found: {pim_file}")
        return 1
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 导入ReactAgentGenerator
        from src.compiler.generators.impl.react_agent_generator import ReactAgentGenerator
        from src.compiler.generators.base_generator import GeneratorConfig
        
        # 创建配置
        config = GeneratorConfig(
            platform=platform,
            output_dir=str(output_dir),
            additional_config={}
        )
        
        logger.info("Initialized ReactAgentGenerator")
        
        # 读取PIM内容
        pim_content = pim_file.read_text(encoding='utf-8')
        logger.info(f"Starting compilation of {pim_file}")
        
        # 创建生成器实例
        generator = ReactAgentGenerator(config)
        
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
        start_time = time.time()
        generator.generate_code(psm_content, str(output_dir))
        code_time = time.time() - start_time
        logger.info(f"Code generated in {code_time:.2f} seconds")
        
        # 统计结果
        python_files = list(output_dir.rglob("*.py"))
        total_files = list(output_dir.rglob("*.*"))
        
        print("\n" + "=" * 50)
        print("✅ Compilation Successful!")
        print("=" * 50)
        print(f"Generator: {generator_type}")
        print(f"Platform: {platform}")
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
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("Trying alternative import method...")
        
        # 如果导入失败，尝试直接执行
        try:
            # 直接运行ReactAgentGenerator的代码
            exec(open("src/compiler/generators/impl/react_agent_generator.py").read())
        except Exception as e2:
            logger.error(f"Alternative method also failed: {e2}")
            return 1
    except Exception as e:
        logger.error(f"Compilation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())