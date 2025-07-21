#!/usr/bin/env python3
"""测试 Gemini CLI 修复功能"""

import os
import sys
import tempfile
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

# 创建有错误的 Python 代码
error_code = '''from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")  # 这会导致错误
    email: str
    
def get_user():
    return undefined_variable  # 未定义的变量
'''

# 保存到临时文件
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(error_code)
    test_file = f.name

print(f"创建测试文件: {test_file}")
print("原始代码:")
print("-" * 60)
print(error_code)
print("-" * 60)

# 导入基础编译器
from compiler.core.base_compiler import BaseCompiler
from compiler.core.compiler_config import CompilerConfig

# 创建一个简单的测试编译器
class TestCompiler(BaseCompiler):
    def _transform_pim_to_psm(self, pim_content: str, source_file: Path):
        return None
    
    def _generate_code_from_psm(self, psm_content: str, psm_file: Path):
        return []

# 创建编译器实例
config = CompilerConfig(
    verbose=True,
    output_dir=Path("./test_output")  # 使用当前目录
)
compiler = TestCompiler(config)

# 测试 Gemini 修复
error_msg = """test.py:4:32: F821 undefined name 'regex'
test.py:8:12: F821 undefined name 'undefined_variable'"""

print("\n调用 Gemini CLI 修复...")
try:
    compiler._fix_with_gemini(test_file, error_msg, "python lint")
    
    # 读取修复后的代码
    with open(test_file, 'r') as f:
        fixed_code = f.read()
    
    print("\n修复后的代码:")
    print("-" * 60)
    print(fixed_code)
    print("-" * 60)
    
except Exception as e:
    print(f"\n修复失败: {e}")
    import traceback
    traceback.print_exc()

finally:
    # 清理临时文件
    if os.path.exists(test_file):
        os.unlink(test_file)
        print(f"\n已清理临时文件: {test_file}")