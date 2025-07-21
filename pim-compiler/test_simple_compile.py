#!/usr/bin/env python3
"""简单的编译测试"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 加载环境变量
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file}")

from compiler.core.compiler_config import CompilerConfig
from compiler.transformers.deepseek_compiler import DeepSeekCompiler

# 创建简单的 PIM 内容
simple_pim = """# 简单用户系统

## 业务实体
### 用户
- ID（自动生成）
- 用户名（必填）
- 邮箱（必填）

## 业务服务
### 用户服务
1. 创建用户：输入用户名和邮箱，返回新用户
2. 查询用户：根据ID查询用户信息
"""

# 创建临时 PIM 文件
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
    f.write(simple_pim)
    pim_file = Path(f.name)

try:
    # 配置编译器（禁用缓存和额外功能）
    config = CompilerConfig(
        output_dir=Path("./test_output"),
        enable_cache=False,
        verbose=True,
        generate_code=False,  # 只生成 PSM
        enable_lint=False,
        enable_unit_tests=False,
        run_tests=False,
        target_platform="fastapi",
        llm_temperature=0.3  # 降低温度使输出更稳定
    )
    
    print("\n创建编译器...")
    compiler = DeepSeekCompiler(config)
    
    print("\n开始编译...")
    result = compiler.compile(pim_file)
    
    if result.success:
        print(f"\n✓ 编译成功!")
        print(f"PSM 文件: {result.psm_file}")
        
        if result.psm_file and result.psm_file.exists():
            print("\nPSM 内容:")
            print("-" * 60)
            with open(result.psm_file, 'r', encoding='utf-8') as f:
                print(f.read())
            print("-" * 60)
    else:
        print(f"\n✗ 编译失败!")
        for error in result.errors:
            print(f"  - {error}")
            
finally:
    # 清理临时文件
    if pim_file.exists():
        pim_file.unlink()