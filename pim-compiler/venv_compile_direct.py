#!/usr/bin/env python3
"""直接在虚拟环境中编译，不使用compile_pim.py"""

import os
import sys
from pathlib import Path
import time

# 添加src到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# 现在可以导入了
from compiler.config import CompilerConfig
from compiler.compiler_factory import CompilerFactory

def main():
    """主函数"""
    print("=== Direct Compilation in Virtual Environment ===")
    print(f"Python: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # 检查虚拟环境
    if "venv_test" not in sys.executable:
        print("⚠️  Warning: Not running in venv_test virtual environment")
        return
    
    # 读取PIM文件
    pim_file = project_root / "examples" / "user_management.md"
    if not pim_file.exists():
        print(f"❌ PIM file not found: {pim_file}")
        return
    
    pim_content = pim_file.read_text(encoding='utf-8')
    print(f"✅ Loaded PIM file: {pim_file}")
    
    # 配置编译器
    output_dir = project_root / "output" / "venv_compile" / "react_agent_direct"
    config = CompilerConfig(
        pim_file=str(pim_file),
        generator_type="react-agent",
        target_platform="fastapi",
        output_dir=str(output_dir),
        max_iterations=20,
        use_parallel=False  # 使用React Agent模式以测试工具
    )
    
    print(f"\nConfiguration:")
    print(f"  Generator: {config.generator_type}")
    print(f"  Platform: {config.target_platform}")
    print(f"  Output: {config.output_dir}")
    print(f"  Max iterations: {config.max_iterations}")
    
    # 创建编译器
    try:
        compiler = CompilerFactory.create_compiler(config)
        print("✅ Compiler created successfully")
        
        # 执行编译
        print("\n🚀 Starting compilation...")
        start_time = time.time()
        
        result = compiler.compile()
        
        elapsed_time = time.time() - start_time
        
        if result and result.get("success"):
            print(f"\n✅ Compilation successful in {elapsed_time:.2f}s")
            print(f"Output directory: {output_dir}")
            
            # 列出生成的文件
            if output_dir.exists():
                py_files = list(output_dir.rglob("*.py"))
                print(f"\nGenerated {len(py_files)} Python files:")
                for f in py_files[:10]:  # 显示前10个
                    print(f"  - {f.relative_to(output_dir)}")
                if len(py_files) > 10:
                    print(f"  ... and {len(py_files) - 10} more")
        else:
            print(f"\n❌ Compilation failed after {elapsed_time:.2f}s")
            if result:
                print(f"Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()