#!/usr/bin/env python3
"""测试改进后的 Gemini CLI 修复流程"""

import os
import sys
import tempfile
import shutil
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

print("\n测试改进后的 Gemini CLI 修复流程")
print("=" * 60)

# 创建测试目录
test_dir = Path("./test_fix_output")
if test_dir.exists():
    shutil.rmtree(test_dir)
test_dir.mkdir()

print(f"\n创建测试目录: {test_dir}")

# 创建一个有错误的 Python 文件
error_code = '''from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")  # 错误：应该用 pattern
    email: EmailStr  # 需要 email-validator
    name: str
    
    # 这是一个非常长的注释行，超过了79个字符的限制，会导致 flake8 报错 E501 line too long

def create_user(username, email, name):
    """创建用户"""
    user = User(username=username, email=email, name=name)
    return undefined_variable  # 错误：未定义的变量
'''

# 创建测试文件
test_file = test_dir / "user_model.py"
with open(test_file, 'w') as f:
    f.write(error_code)

print(f"\n创建测试文件: {test_file}")
print("文件内容包含以下错误：")
print("1. 使用了过时的 'regex' 参数")
print("2. 缺少 email-validator 依赖")
print("3. 有一行超过 79 字符")
print("4. 使用了未定义的变量")

# 创建一个简单的测试文件
test_code = '''import pytest
from user_model import User, create_user

def test_create_user():
    """测试创建用户"""
    user = create_user("john_doe", "john@example.com", "John Doe")
    assert user.username == "john_doe"
    assert user.email == "john@example.com"
    assert user.name == "John Doe"

def test_invalid_username():
    """测试无效的用户名"""
    with pytest.raises(ValueError):
        User(username="123invalid", email="test@example.com", name="Test")
'''

test_file_test = test_dir / "test_user_model.py"
with open(test_file_test, 'w') as f:
    f.write(test_code)

print(f"\n创建测试文件: {test_file_test}")

# 配置编译器
config = CompilerConfig(
    output_dir=test_dir,
    enable_cache=False,
    verbose=True,
    generate_code=False,  # 不生成新代码
    enable_lint=True,
    auto_fix_lint=True,
    enable_unit_tests=True,
    run_tests=True,
    auto_fix_tests=True,
    target_platform="fastapi"
)

print("\n配置:")
print(f"- 启用 lint 检查: {config.enable_lint}")
print(f"- 自动修复 lint: {config.auto_fix_lint}")
print(f"- 运行测试: {config.run_tests}")
print(f"- 自动修复测试: {config.auto_fix_tests}")

# 创建编译器实例
print("\n创建编译器实例...")
compiler = DeepSeekCompiler(config)

# 测试 lint 修复
print("\n" + "=" * 60)
print("测试 1: Lint 修复")
print("=" * 60)

print("\n运行 lint 检查和修复...")
compiler._lint_and_fix_code([str(test_file)])

print("\n检查修复后的文件...")
if test_file.exists():
    with open(test_file, 'r') as f:
        fixed_content = f.read()
    print("\n修复后的代码片段:")
    print("-" * 40)
    # 只显示前几行
    lines = fixed_content.split('\n')[:10]
    for i, line in enumerate(lines, 1):
        print(f"{i:3d} | {line}")
    print("-" * 40)

# 测试 pytest 修复
print("\n" + "=" * 60)
print("测试 2: Pytest 修复")
print("=" * 60)

print("\n运行测试...")
compiler._run_and_fix_tests([str(test_file_test)])

print("\n测试完成！")
print("\n清理测试目录...")
# shutil.rmtree(test_dir)  # 暂时保留以便检查结果
print(f"测试目录保留在: {test_dir}")
print("\n提示：可以手动检查生成的文件和修复结果")