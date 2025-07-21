#!/usr/bin/env python3
"""测试 pytest 修复功能 - 修正版"""

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

print("\n测试 Pytest 修复功能 V2")
print("=" * 60)

# 创建测试目录
test_dir = Path("./test_pytest_fix_v2")
if test_dir.exists():
    shutil.rmtree(test_dir)
test_dir.mkdir()

print(f"\n1. 创建测试目录: {test_dir}")

# 创建有问题的代码文件
code_with_error = '''from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")  # 错误：应该用 pattern
    email: EmailStr  # 需要 email-validator
    name: str
    
def create_user(username: str, email: str, name: str) -> User:
    """创建用户"""
    return User(username=username, email=email, name=name)
'''

code_file = test_dir / "user_model.py"
with open(code_file, 'w') as f:
    f.write(code_with_error)

# 创建测试文件
test_code = '''import pytest
from user_model import User, create_user

def test_create_user():
    """测试创建用户"""
    user = create_user("john_doe", "john@example.com", "John Doe")
    assert user.username == "john_doe"
    assert user.email == "john@example.com"
    assert user.name == "John Doe"

def test_invalid_email():
    """测试无效邮箱"""
    with pytest.raises(ValueError):
        create_user("john_doe", "invalid-email", "John Doe")
        
def test_invalid_username():
    """测试无效用户名"""
    with pytest.raises(ValueError):
        User(username="123invalid", email="test@example.com", name="Test")
'''

test_file = test_dir / "test_user_model.py"
with open(test_file, 'w') as f:
    f.write(test_code)

print(f"\n2. 创建文件:")
print(f"   - 代码文件: {code_file}")
print(f"   - 测试文件: {test_file}")

# 先运行 pytest 获取真实的错误（使用正确的路径）
print("\n3. 运行 pytest 获取真实错误...")
os.chdir(test_dir)  # 切换到测试目录
result = subprocess.run(
    ['python', '-m', 'pytest', 'test_user_model.py', '-v'],
    capture_output=True,
    text=True
)
os.chdir('..')  # 返回上级目录

print("\n错误信息:")
print("-" * 60)
if result.returncode != 0:
    print("返回码:", result.returncode)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("标准错误:")
        print(result.stderr)
else:
    print("测试已通过（不应该发生）")
print("-" * 60)

# 创建编译器配置
config = CompilerConfig(
    output_dir=test_dir,
    enable_cache=False,
    verbose=True,
    auto_fix_tests=True
)

# 创建编译器实例
compiler = TestCompiler(config)

print("\n4. 调用 _fix_with_gemini 修复 pytest 错误...")
try:
    # 使用完整的错误信息
    error_msg = result.stdout + "\n" + result.stderr if result.stderr else result.stdout
    
    # 调用修复方法（注意这里传递测试文件路径）
    success = compiler._fix_with_gemini(
        str(test_file), 
        error_msg, 
        'pytest failures'
    )
    
    if success:
        print("✓ Gemini CLI 执行成功")
    else:
        print("✗ Gemini CLI 执行失败")
        
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()

# 检查修复结果
print("\n5. 检查修复结果...")

# 检查 requirements.txt
req_file = test_dir / "requirements.txt"
if req_file.exists():
    print(f"\n✓ 找到 requirements.txt:")
    with open(req_file, 'r') as f:
        print("-" * 40)
        print(f.read())
        print("-" * 40)
    
    # 安装依赖
    print("\n安装依赖...")
    install_result = subprocess.run(
        ['pip', 'install', '-r', str(req_file), '--quiet'],
        capture_output=True,
        text=True
    )
    if install_result.returncode == 0:
        print("✓ 依赖安装成功")
    else:
        print("✗ 依赖安装失败")

# 检查代码文件是否被修复
print("\n6. 检查代码文件...")
with open(code_file, 'r') as f:
    fixed_code = f.read()

# 检查是否将 regex 改为了 pattern
if 'pattern=' in fixed_code and 'regex=' not in fixed_code:
    print("✓ 已将 'regex' 改为 'pattern'")
else:
    print("✗ 'regex' 参数未修复")

print("\n修复后的代码:")
print("=" * 60)
print(fixed_code)
print("=" * 60)

# 再次运行测试
print("\n7. 再次运行 pytest...")
os.chdir(test_dir)
final_result = subprocess.run(
    ['python', '-m', 'pytest', 'test_user_model.py', '-v'],
    capture_output=True,
    text=True
)
os.chdir('..')

if final_result.returncode == 0:
    print("\n✓ 所有测试通过！")
    print(final_result.stdout)
else:
    print("\n测试结果:")
    print("-" * 60)
    print(final_result.stdout)
    if final_result.stderr:
        print("错误:")
        print(final_result.stderr)
    print("-" * 60)

# 显示测试摘要
print("\n8. 测试摘要:")
print(f"   - requirements.txt 创建: {'✓' if req_file.exists() else '✗'}")
print(f"   - regex 改为 pattern: {'✓' if 'pattern=' in fixed_code else '✗'}")
print(f"   - 测试通过: {'✓' if final_result.returncode == 0 else '✗'}")

print(f"\n测试完成！")
print(f"测试目录: {test_dir}")