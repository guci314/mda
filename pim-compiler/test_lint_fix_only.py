#!/usr/bin/env python3
"""只测试 lint 修复功能"""

import os
import sys
import shutil
import subprocess
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
from compiler.core.base_compiler import BaseCompiler

# 创建测试编译器
class TestCompiler(BaseCompiler):
    def _transform_pim_to_psm(self, pim_content: str, source_file: Path):
        return None
    
    def _generate_code_from_psm(self, psm_content: str, psm_file: Path):
        return []

print("\n测试 Lint 修复功能")
print("=" * 60)

# 创建测试目录
test_dir = Path("./test_lint_only")
if test_dir.exists():
    shutil.rmtree(test_dir)
test_dir.mkdir()

print(f"\n1. 创建测试目录: {test_dir}")

# 创建有 lint 错误的 Python 文件
error_code = '''from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")  # 应该用 pattern
    name: str
    
    # 这是一个非常长的注释行，超过了79个字符的限制，会导致 flake8 报错 E501 line too long，这个注释真的很长

def create_user(username, name):
    """创建用户"""
    user = User(username=username, name=name)  # F841: 未使用的变量
    return undefined_variable  # F821: 未定义的变量
'''

test_file = test_dir / "user_model.py"
with open(test_file, 'w') as f:
    f.write(error_code)

print(f"\n2. 创建测试文件: {test_file}")
print("包含的 lint 错误：")
print("   - 使用了过时的 'regex' 参数")
print("   - E501: 行太长")
print("   - F841: 未使用的变量")
print("   - F821: 未定义的变量")

# 先运行 flake8 获取错误
print("\n3. 运行 flake8 检查...")
result = subprocess.run(
    ['flake8', str(test_file)],
    capture_output=True,
    text=True
)

if result.stdout:
    print("\n发现的错误:")
    print("-" * 60)
    print(result.stdout)
    print("-" * 60)

# 创建编译器配置
config = CompilerConfig(
    output_dir=test_dir,
    enable_cache=False,
    verbose=True,
    auto_fix_lint=True
)

# 创建编译器实例
compiler = TestCompiler(config)

print("\n4. 调用 _fix_with_gemini 修复 lint 错误...")
try:
    # 直接调用修复方法
    success = compiler._fix_with_gemini(
        str(test_file), 
        result.stdout, 
        'python lint'
    )
    
    if success:
        print("✓ Gemini CLI 执行成功")
    else:
        print("✗ Gemini CLI 执行失败")
        
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()

# 检查修复后的文件
print("\n5. 检查修复后的文件...")
if test_file.exists():
    with open(test_file, 'r') as f:
        fixed_content = f.read()
    
    print("\n修复后的代码:")
    print("=" * 60)
    print(fixed_content)
    print("=" * 60)
    
    # 再次运行 flake8
    print("\n6. 再次运行 flake8 验证...")
    result = subprocess.run(
        ['flake8', str(test_file)],
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print("\n仍有错误:")
        print("-" * 60)
        print(result.stdout)
        print("-" * 60)
    else:
        print("\n✓ 所有 lint 错误已修复！")

# 测试 lint_python 方法
print("\n7. 测试 _lint_python 方法...")
compiler._lint_python(str(test_file))

print(f"\n测试完成！")
print(f"测试目录保留在: {test_dir}")