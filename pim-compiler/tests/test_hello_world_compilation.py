#!/usr/bin/env python3
"""
测试 Hello World PIM 的编译过程
"""
import os
import sys
from pathlib import Path
import shutil
import logging

# 添加编译器到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compiler import PureGeminiCompiler, CompilerConfig

# 设置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_hello_world_compilation():
    """测试编译 Hello World PIM"""
    
    # 准备测试
    hello_world_pim = Path(__file__).parent.parent.parent / "hello_world_pim.md"
    output_dir = Path("test_output")
    
    # 清理之前的输出
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # 配置编译器
    config = CompilerConfig(
        gemini_api_key=os.getenv("GOOGLE_AI_STUDIO_KEY", ""),
        output_dir=str(output_dir),
        target_platform="fastapi",
        enable_cache=False,  # 禁用缓存以确保重新生成
        verbose=True,
        auto_test=False,  # 暂时禁用自动测试
        generate_tests=True,
        generate_docs=True
    )
    
    logger.info(f"开始编译 {hello_world_pim}")
    logger.info(f"输出目录: {output_dir}")
    
    # 创建编译器实例
    compiler = PureGeminiCompiler(config)
    
    # 执行编译
    result = compiler.compile(hello_world_pim)
    
    logger.info(f"编译完成: success={result.success}")
    if result.error:
        logger.error(f"编译错误: {result.error}")
    
    # 检查生成的文件
    logger.info("\n=== 生成的文件 ===")
    for root, dirs, files in os.walk(output_dir):
        level = root.replace(str(output_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        logger.info(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            logger.info(f"{subindent}{file}")
    
    # 检查关键文件
    generated_dir = output_dir / "generated" / "hello_world_pim"
    logger.info(f"\n检查生成目录: {generated_dir}")
    logger.info(f"目录是否存在: {generated_dir.exists()}")
    
    if generated_dir.exists():
        # 列出所有Python文件
        py_files = list(generated_dir.rglob("*.py"))
        logger.info(f"\n找到的Python文件数量: {len(py_files)}")
        for py_file in py_files:
            logger.info(f"  - {py_file.relative_to(output_dir)}")
        
        # 检查main.py
        main_py = generated_dir / "app" / "main.py"
        logger.info(f"\nmain.py 是否存在: {main_py.exists()}")
        
        if not main_py.exists():
            # 检查其他可能的位置
            possible_locations = [
                generated_dir / "main.py",
                generated_dir / "src" / "main.py",
                generated_dir / "hello_world_pim" / "main.py",
            ]
            for loc in possible_locations:
                logger.info(f"检查 {loc.relative_to(output_dir)}: {loc.exists()}")
    
    # 查看PSM内容的一部分
    psm_file = output_dir / "psm" / "hello_world_pim_psm.md"
    if psm_file.exists():
        logger.info(f"\nPSM文件存在: {psm_file}")
        with open(psm_file, 'r') as f:
            lines = f.readlines()
            logger.info(f"PSM文件行数: {len(lines)}")
    
    return result


if __name__ == "__main__":
    logger.info("开始测试 Hello World PIM 编译")
    result = test_hello_world_compilation()
    logger.info(f"\n测试完成，编译成功: {result.success}")