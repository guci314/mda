#!/usr/bin/env python3
"""
修复路径问题的测试
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


def test_with_fixed_prompt():
    """测试修改后的提示以确保文件生成在正确位置"""
    
    # 准备测试
    hello_world_pim = Path(__file__).parent.parent.parent / "hello_world_pim.md"
    output_dir = Path("test_fixed_output")
    
    # 清理之前的输出
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # 配置编译器
    config = CompilerConfig(
        gemini_api_key=os.getenv("GOOGLE_AI_STUDIO_KEY", ""),
        output_dir=str(output_dir),
        target_platform="fastapi",
        enable_cache=False,
        verbose=True,
        auto_test=False,
        generate_tests=False,  # 暂时关闭测试生成
        generate_docs=False    # 暂时关闭文档生成
    )
    
    logger.info(f"开始编译 {hello_world_pim}")
    logger.info(f"输出目录: {output_dir}")
    
    # 创建编译器实例
    compiler = PureGeminiCompiler(config)
    
    # 在执行前记录工作目录结构
    logger.info("\n=== 编译前的目录结构 ===")
    log_directory_structure(output_dir)
    
    # 执行编译
    result = compiler.compile(hello_world_pim)
    
    logger.info(f"\n编译完成: success={result.success}")
    if result.error:
        logger.error(f"编译错误: {result.error}")
    
    # 记录编译后的目录结构
    logger.info("\n=== 编译后的目录结构 ===")
    log_directory_structure(output_dir)
    
    # 检查所有可能的位置
    logger.info("\n=== 查找所有 Python 文件 ===")
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_dir)
                logger.info(f"  找到 Python 文件: {rel_path}")
                if file == "main.py":
                    logger.info(f"  ✓ main.py 位置: {rel_path}")
    
    # 检查特定位置
    possible_main_locations = [
        output_dir / "generated" / "hello_world_pim" / "main.py",
        output_dir / "generated" / "hello_world_pim" / "app" / "main.py",
        output_dir / "main.py",
        output_dir / "hello_world_pim" / "main.py",
    ]
    
    logger.info("\n=== 检查可能的 main.py 位置 ===")
    for location in possible_main_locations:
        exists = location.exists()
        logger.info(f"  {location.relative_to(output_dir)}: {'✓ 存在' if exists else '✗ 不存在'}")
    
    return result


def log_directory_structure(path: Path, indent=0):
    """递归记录目录结构"""
    if not path.exists():
        logger.info(f"{'  ' * indent}{path.name}/ (不存在)")
        return
    
    items = list(path.iterdir())
    logger.info(f"{'  ' * indent}{path.name}/ ({len(items)} 项)")
    
    for item in sorted(items):
        if item.is_dir():
            log_directory_structure(item, indent + 1)
        else:
            size = item.stat().st_size
            logger.info(f"{'  ' * (indent + 1)}{item.name} ({size} 字节)")


if __name__ == "__main__":
    logger.info("开始路径修复测试")
    result = test_with_fixed_prompt()
    logger.info(f"\n测试完成，编译成功: {result.success}")