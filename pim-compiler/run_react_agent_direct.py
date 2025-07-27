#!/usr/bin/env python3
"""直接运行ReactAgentGenerator"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    # 检查API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not set")
        return
    
    # 读取PIM
    pim_file = Path("../models/domain/用户管理_pim.md")
    if not pim_file.exists():
        print(f"❌ PIM file not found: {pim_file}")
        return
    
    pim_content = pim_file.read_text(encoding='utf-8')
    print(f"✅ Loaded PIM: {pim_file}")
    
    # 设置输出目录
    output_dir = Path("output/react_agent_enhanced_v2")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 导入ReactAgentGenerator
    try:
        from src.compiler.generators.impl.react_agent_generator import ReactAgentGenerator
        from src.compiler.generators.generator_factory import GeneratorConfig
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    print(f"\n🚀 Starting ReactAgent compilation...")
    print(f"Output directory: {output_dir}")
    
    # 创建配置
    config = GeneratorConfig(
        platform="fastapi",
        output_dir=str(output_dir),
        additional_config={}
    )
    
    # 创建生成器
    generator = ReactAgentGenerator(config)
    
    # 生成PSM
    print("\n1. Generating PSM...")
    start_time = datetime.now()
    psm_content = generator.generate_psm(pim_content)
    psm_time = (datetime.now() - start_time).total_seconds()
    print(f"✅ PSM generated in {psm_time:.2f}s")
    
    # 保存PSM
    psm_file = output_dir / "user_management_psm.md"
    psm_file.write_text(psm_content, encoding='utf-8')
    
    # 生成代码
    print("\n2. Generating code...")
    start_time = datetime.now()
    generator.generate_code(psm_content, str(output_dir))
    code_time = (datetime.now() - start_time).total_seconds()
    print(f"✅ Code generated in {code_time:.2f}s")
    
    print(f"\n✅ Compilation complete!")
    print(f"Total time: {psm_time + code_time:.2f}s")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main()