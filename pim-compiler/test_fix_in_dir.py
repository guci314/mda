#!/usr/bin/env python3
"""测试在项目目录中调用 Gemini CLI 修复代码"""

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

print("\n测试在项目目录中调用 Gemini CLI")
print("=" * 60)

# 创建测试目录
test_dir = Path("./test_fix_dir")
if test_dir.exists():
    shutil.rmtree(test_dir)
test_dir.mkdir()

print(f"\n1. 创建测试目录: {test_dir}")

# 创建有错误的 Python 文件
error_code = '''from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")  # 应该用 pattern
    email: EmailStr
    name: str
    
    # 这是一个非常长的注释行，超过了79个字符的限制，会导致 flake8 报错 E501 line too long

def create_user(username, email, name):
    """创建用户"""
    user = User(username=username, email=email, name=name)  # F841: 未使用的变量
    return undefined_variable  # F821: 未定义的变量
'''

test_file = test_dir / "user_model.py"
with open(test_file, 'w') as f:
    f.write(error_code)

print(f"\n2. 创建测试文件: {test_file}")

# 先运行 flake8 获取错误
print("\n3. 运行 flake8 检查错误...")
result = subprocess.run(
    ['flake8', str(test_file)],
    capture_output=True,
    text=True
)

if result.stdout:
    print("发现的错误:")
    print("-" * 40)
    print(result.stdout)
    print("-" * 40)

# 创建编译器配置
config = CompilerConfig(
    output_dir=test_dir,
    enable_cache=False,
    verbose=True,
    auto_fix_lint=True
)

# 创建编译器实例
compiler = TestCompiler(config)

print("\n4. 调用 Gemini CLI 修复...")
try:
    # 直接调用修复方法
    success = compiler._fix_with_gemini(str(test_file), result.stdout, 'python lint')
    
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
    
    print("修复后的代码:")
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
        print("仍有错误:")
        print(result.stdout)
    else:
        print("✓ 所有 lint 错误已修复！")

# 检查是否生成了 requirements.txt
req_file = test_dir / "requirements.txt"
if req_file.exists():
    print(f"\n7. 发现 requirements.txt:")
    with open(req_file, 'r') as f:
        print(f.read())

print("\n测试完成")
print(f"测试目录: {test_dir}")