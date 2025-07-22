#!/usr/bin/env python3
"""简单测试PIM编译器"""
import os
import sys
from pathlib import Path
import shutil

# 添加编译器到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compiler import PureGeminiCompiler, CompilerConfig
import logging

logging.basicConfig(level=logging.DEBUG)

# 清理输出目录
output_dir = Path("test_simple_output")
if output_dir.exists():
    shutil.rmtree(output_dir)

# 配置编译器
config = CompilerConfig(
    output_dir=output_dir,
    target_platform="fastapi",
    enable_cache=False,
    verbose=True
)

# 编译
pim_file = Path(__file__).parent.parent.parent / "hello_world_pim.md"
print(f"\n编译: {pim_file}")

compiler = PureGeminiCompiler(config)
result = compiler.compile(pim_file)

print(f"\n结果: {'成功' if result.success else '失败'}")
if result.error:
    print(f"错误: {result.error}")
    
print(f"\n生成的文件:")
if output_dir.exists():
    for f in output_dir.rglob("*"):
        if f.is_file():
            print(f"  {f.relative_to(output_dir)}")