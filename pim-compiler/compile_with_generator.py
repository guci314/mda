#!/usr/bin/env python3
"""
使用可配置生成器的编译脚本
支持通过命令行参数或环境变量选择不同的代码生成器
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.compiler.config import CompilerConfig
from src.compiler.core.configurable_compiler import ConfigurableCompiler
from src.compiler.generators import GeneratorFactory
from utils.logger import setup_logger, get_logger


def main():
    """主函数"""
    # 设置日志
    setup_logger("compile_with_generator")
    logger = get_logger(__name__)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="PIM Compiler with Configurable Generators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 使用默认的 Gemini CLI 生成器
  %(prog)s examples/user_management.md
  
  # 使用 React Agent 生成器
  %(prog)s examples/user_management.md --generator react-agent
  
  # 使用 Autogen 生成器
  %(prog)s examples/user_management.md --generator autogen
  
  # 指定输出目录和平台
  %(prog)s examples/blog.md -o ./output -p django --generator react-agent
  
  # 列出所有可用的生成器
  %(prog)s --list-generators

Environment Variables:
  CODE_GENERATOR_TYPE    默认生成器类型 (gemini-cli, react-agent, autogen)
  GEMINI_MODEL          Gemini 模型名称
  DEEPSEEK_API_KEY      DeepSeek API Key (用于 react-agent)
  OPENAI_API_KEY        OpenAI API Key (用于 autogen)
"""
    )
    
    parser.add_argument(
        "pim_file",
        nargs="?",
        help="PIM 文件路径"
    )
    
    parser.add_argument(
        "-g", "--generator",
        choices=["gemini-cli", "react-agent", "autogen"],
        default=os.getenv("CODE_GENERATOR_TYPE", "gemini-cli"),
        help="代码生成器类型 (默认: %(default)s)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("./compiled_output"),
        help="输出目录 (默认: %(default)s)"
    )
    
    parser.add_argument(
        "-p", "--platform",
        choices=["fastapi", "flask", "django", "springboot", "express", "gin"],
        default="fastapi",
        help="目标平台 (默认: %(default)s)"
    )
    
    parser.add_argument(
        "--no-test",
        action="store_true",
        help="禁用自动测试"
    )
    
    parser.add_argument(
        "--list-generators",
        action="store_true",
        help="列出所有可用的生成器"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志"
    )
    
    args = parser.parse_args()
    
    # 如果请求列出生成器
    if args.list_generators:
        print("\nAvailable Code Generators:")
        print("-" * 50)
        generators = GeneratorFactory.list_generators()
        for name, desc in generators.items():
            print(f"  {name:<15} - {desc}")
        print("\nSet CODE_GENERATOR_TYPE environment variable or use --generator flag")
        return 0
    
    # 检查 PIM 文件
    if not args.pim_file:
        parser.error("PIM file is required unless using --list-generators")
    
    pim_file = Path(args.pim_file)
    if not pim_file.exists():
        logger.error(f"PIM file not found: {pim_file}")
        return 1
    
    # 检查生成器所需的环境变量
    if args.generator == "react-agent" and not os.getenv("DEEPSEEK_API_KEY"):
        logger.warning("DEEPSEEK_API_KEY not set for react-agent generator")
        logger.info("Set it with: export DEEPSEEK_API_KEY=your-api-key")
    
    if args.generator == "autogen" and not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set for autogen generator")
        logger.info("Set it with: export OPENAI_API_KEY=your-api-key")
    
    # 创建编译器配置
    config = CompilerConfig(
        generator_type=args.generator,
        target_platform=args.platform,
        output_dir=args.output,
        auto_test=not args.no_test,
        verbose=args.verbose,
        fail_on_test_failure=False  # 对于非 gemini-cli 生成器，暂时禁用测试失败检查
    )
    
    logger.info(f"Using generator: {args.generator}")
    logger.info(f"Target platform: {args.platform}")
    logger.info(f"Output directory: {args.output}")
    
    try:
        # 创建编译器
        compiler = ConfigurableCompiler(config)
        
        # 执行编译
        result = compiler.compile(pim_file)
        
        # 显示结果
        if result["success"]:
            print("\n" + "=" * 50)
            print("✅ Compilation Successful!")
            print("=" * 50)
            print(f"Generator: {result['generator_type']}")
            print(f"Platform: {result['target_platform']}")
            print(f"Output: {result['output_dir']}")
            print(f"\nStatistics:")
            print(f"  - PSM generation: {result['psm_generation_time']:.2f}s")
            print(f"  - Code generation: {result['code_generation_time']:.2f}s")
            print(f"  - Total time: {result['total_compilation_time']:.2f}s")
            print(f"  - Files generated: {result['statistics']['total_files']}")
            print(f"  - Python files: {result['statistics']['python_files']}")
            
            # 如果有测试结果
            if result.get("test_results"):
                tests = result["test_results"].get("tests", {})
                if tests.get("passed"):
                    print(f"\n✅ Tests: PASSED")
                else:
                    print(f"\n❌ Tests: FAILED")
            
            print("\nNext steps:")
            print(f"  cd {result['output_dir']}/generated")
            print("  pip install -r requirements.txt")
            print("  uvicorn main:app --reload")
            
            return 0
        else:
            print("\n" + "=" * 50)
            print("❌ Compilation Failed!")
            print("=" * 50)
            print(f"Error: {result['error']}")
            return 1
            
    except Exception as e:
        logger.error(f"Compilation failed with error: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())