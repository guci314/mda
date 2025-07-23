#!/usr/bin/env python3
"""编译单个 PIM 文件"""
import os
import sys
from pathlib import Path
import logging
import time

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from compiler.config import CompilerConfig
from compiler.core.pure_gemini_compiler import PureGeminiCompiler

def main():
    if len(sys.argv) < 2:
        print("Usage: python compile_pim.py <pim_file>")
        sys.exit(1)
    
    pim_file = Path(sys.argv[1])
    if not pim_file.exists():
        print(f"Error: PIM file not found: {pim_file}")
        sys.exit(1)
    
    # 配置
    output_dir = Path("compiled_output") / pim_file.stem
    config = CompilerConfig(
        output_dir=output_dir,
        target_platform="fastapi",
        auto_test=True,
        enable_lint=False,  # 暂时禁用lint
        auto_fix_tests=False,  # 暂时禁用自动修复
        generate_tests=True,
        verbose=True
    )
    
    # 创建编译器
    compiler = PureGeminiCompiler(config)
    
    # 执行编译
    print("="*80)
    print(f"编译 PIM 文件: {pim_file}")
    print(f"目标平台: {config.target_platform}")
    print(f"输出目录: {config.output_dir}")
    print("="*80)
    
    start_time = time.time()
    result = compiler.compile(pim_file)
    
    if result and result.success:
        print("\n" + "="*80)
        print("✅ 编译成功！")
        print("="*80)
        
        # 基本信息
        if result.statistics:
            print(f"\n📁 生成的文件:")
            print(f"   总文件数: {result.statistics.get('total_files', 0)}")
            print(f"   Python文件: {result.statistics.get('python_files', 0)}")
        
        # 编译时间
        if result.compilation_time:
            minutes = int(result.compilation_time // 60)
            seconds = int(result.compilation_time % 60)
            print(f"\n⏱️  编译时间: {minutes}分{seconds}秒")
        
        # PSM 和代码目录
        print(f"\n📄 PSM文件: {result.psm_file}")
        print(f"📂 代码目录: {result.code_dir}")
        
        # 应用运行结果
        if result.app_results:
            print(f"\n🚀 应用运行:")
            if result.app_results.get('success'):
                print(f"   状态: ✅ 成功启动")
                print(f"   端口: {result.app_results.get('port')}")
                
                # REST 端点测试结果
                if result.app_results.get('rest_tests'):
                    rest = result.app_results['rest_tests']
                    print(f"\n🌐 REST API 测试:")
                    print(f"   测试端点数: {rest.get('endpoints_tested')}")
                    print(f"   通过端点数: {rest.get('endpoints_passed')}")
                    print(f"   成功率: {rest.get('endpoints_passed', 0) / max(rest.get('endpoints_tested', 1), 1) * 100:.0f}%")
            else:
                print(f"   状态: ❌ 启动失败")
                if result.app_results.get('errors'):
                    print(f"   错误: {', '.join(result.app_results['errors'])}")
        
        # 总耗时
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"\n⏱️  总耗时: {minutes}分{seconds}秒")
        
        print(f"\n✨ 提示: 生成的代码位于 {result.code_dir}")
        
        # 如果应用还在运行，提示如何停止
        if result.app_results and result.app_results.get('success'):
            print(f"\n💡 应用正在端口 {result.app_results.get('port')} 上运行")
            print("   停止应用: pkill -f 'uvicorn.*port 8100'")
    else:
        print("\n" + "="*80)
        print("❌ 编译失败！")
        print("="*80)
        if result and result.error:
            print(f"错误: {result.error}")
        
        # 总耗时
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"\n⏱️  总耗时: {minutes}分{seconds}秒")
        
        sys.exit(1)

if __name__ == "__main__":
    main()