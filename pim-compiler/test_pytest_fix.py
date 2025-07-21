#!/usr/bin/env python3
"""测试 pytest 修复功能"""

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

print("\n测试 Pytest 修复功能")
print("=" * 60)

# 创建测试目录
test_dir = Path("./test_pytest_fix")
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
print("\n   包含的问题:")
print("   - Pydantic 使用了过时的 'regex' 参数")
print("   - EmailStr 需要 email-validator 依赖")

# 先运行 pytest 获取错误
print("\n3. 运行 pytest 获取错误信息...")
result = subprocess.run(
    ['python', '-m', 'pytest', str(test_file), '-v'],
    capture_output=True,
    text=True,
    cwd=test_dir
)

print("\n错误信息:")
print("-" * 60)
if result.stdout:
    print(result.stdout)
if result.stderr:
    print(result.stderr)
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
    # 提取主要错误信息
    error_msg = result.stdout if result.stdout else result.stderr
    
    # 直接调用修复方法
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

# 检查是否创建了 requirements.txt
req_file = test_dir / "requirements.txt"
print("\n5. 检查 requirements.txt...")
if req_file.exists():
    print(f"✓ 找到 requirements.txt:")
    with open(req_file, 'r') as f:
        print("-" * 40)
        print(f.read())
        print("-" * 40)
else:
    print("✗ 未找到 requirements.txt")

# 检查修复后的代码文件
print("\n6. 检查修复后的代码文件...")
if code_file.exists():
    with open(code_file, 'r') as f:
        fixed_code = f.read()
    
    print("\n代码文件 (user_model.py):")
    print("=" * 60)
    print(fixed_code)
    print("=" * 60)

# 如果有 requirements.txt，尝试安装依赖
if req_file.exists():
    print("\n7. 安装依赖...")
    install_result = subprocess.run(
        ['pip', 'install', '-r', 'requirements.txt'],
        capture_output=True,
        text=True,
        cwd=test_dir
    )
    if install_result.returncode == 0:
        print("✓ 依赖安装成功")
    else:
        print("✗ 依赖安装失败")
        if install_result.stderr:
            print(install_result.stderr)

# 再次运行 pytest
print("\n8. 再次运行 pytest 验证修复...")
result = subprocess.run(
    ['python', '-m', 'pytest', str(test_file), '-v'],
    capture_output=True,
    text=True,
    cwd=test_dir
)

if result.returncode == 0:
    print("\n✓ 所有测试通过！")
    print(result.stdout)
else:
    print("\n✗ 仍有测试失败:")
    print("-" * 60)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    print("-" * 60)

print(f"\n测试完成！")
print(f"测试目录保留在: {test_dir}")