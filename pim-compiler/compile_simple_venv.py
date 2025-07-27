#!/usr/bin/env python3
"""简单的虚拟环境编译脚本"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# 设置环境变量
os.environ["PYTHONPATH"] = f"{project_root}:{project_root / 'src'}:{os.environ.get('PYTHONPATH', '')}"

# 导入必要的模块
from src.compiler.generators.impl.react_agent_generator import ReactAgentGenerator
from src.compiler.generators.base_generator import GeneratorConfig

def main():
    print("=== Simple Virtual Environment Compilation ===")
    print(f"Python: {sys.executable}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    
    # 读取PIM文件
    pim_file = project_root / "examples" / "user_management.md"
    pim_content = pim_file.read_text(encoding='utf-8')
    
    # 配置生成器
    config = GeneratorConfig(
        name="react-agent",
        model="deepseek-chat",
        temperature=0.7,
        max_iterations=20,
        extra_params={
            "use_parallel": False,  # 使用Agent模式以测试工具
            "cache_path": ".langchain_cache.db"
        }
    )
    
    # 创建生成器
    generator = ReactAgentGenerator(config)
    
    # 设置输出目录
    output_dir = project_root / "output" / "venv_simple" / "react_agent"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nGenerating PSM...")
    # 生成PSM
    psm_result = generator.generate_psm(
        pim_content,
        platform="fastapi",
        output_dir=output_dir / "user_management"
    )
    
    if psm_result.success:
        print(f"✅ PSM generated in {psm_result.generation_time:.2f}s")
        
        print(f"\nGenerating code...")
        # 生成代码
        code_result = generator.generate_code(
            psm_result.psm_content,
            output_dir=output_dir / "user_management" / "generated",
            platform="fastapi"
        )
        
        if code_result.success:
            print(f"✅ Code generated in {code_result.generation_time:.2f}s")
            print(f"Files: {len(code_result.code_files)}")
            print(f"Output: {output_dir}")
        else:
            print(f"❌ Code generation failed: {code_result.error_message}")
    else:
        print(f"❌ PSM generation failed: {psm_result.error_message}")

if __name__ == "__main__":
    main()