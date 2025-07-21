#!/usr/bin/env python3
"""简单测试 Gemini CLI 修复代码"""

import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)

# 创建测试文件
test_code = '''from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z]")  # 应该用 pattern
'''

test_file = Path("test_error.py")
with open(test_file, 'w') as f:
    f.write(test_code)

print(f"创建测试文件: {test_file}")

# 准备环境
env = os.environ.copy()

# 只保留 GEMINI_API_KEY，移除 GOOGLE_API_KEY
if "GOOGLE_API_KEY" in env:
    del env["GOOGLE_API_KEY"]

# 构建命令
cmd = [
    "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini",
    "-m", "gemini-2.0-flash-exp",
    "-p", "修复 test_error.py 中的 Pydantic 错误：将 regex 改为 pattern"
]

print("\n执行命令...")
print(f"命令: {' '.join(cmd[:4])}...")

# 执行
try:
    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print(f"\n返回码: {result.returncode}")
    
    if result.stdout:
        print("\n输出:")
        print(result.stdout[:500])
    
    if result.stderr:
        print("\n错误:")
        print(result.stderr[:500])
        
    # 检查文件
    print("\n检查文件内容:")
    with open(test_file, 'r') as f:
        print(f.read())
        
except subprocess.TimeoutExpired:
    print("超时！")
except Exception as e:
    print(f"错误: {e}")
finally:
    # 清理
    if test_file.exists():
        test_file.unlink()
        print("\n已清理测试文件")