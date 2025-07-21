#!/usr/bin/env python3
"""测试 Gemini CLI 的正确调用方式"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file}")

print("\n测试 Gemini CLI 的不同调用方式")
print("=" * 60)

# 准备环境变量
env = os.environ.copy()

# 设置代理
proxy_host = os.getenv("PROXY_HOST", "127.0.0.1")
proxy_port = os.getenv("PROXY_PORT", "7890")
if proxy_host and proxy_port:
    proxy_url = f"http://{proxy_host}:{proxy_port}"
    env["HTTP_PROXY"] = proxy_url
    env["HTTPS_PROXY"] = proxy_url

# API key 设置
if "GOOGLE_AI_STUDIO_KEY" in env and "GEMINI_API_KEY" not in env:
    env["GEMINI_API_KEY"] = env["GOOGLE_AI_STUDIO_KEY"]

# Gemini CLI 路径
gemini_cli_path = "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini"
if not os.path.exists(gemini_cli_path):
    gemini_cli_path = "gemini"

model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# 测试1：通过标准输入传递内容
print("\n测试1：通过标准输入传递内容")
print("-" * 40)

code_with_error = '''from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")
'''

prompt = "修复这段代码中的 Pydantic 错误（regex 应该改为 pattern）"

# 创建临时文件存储代码
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(code_with_error)
    temp_file = f.name

print(f"临时文件: {temp_file}")

try:
    # 尝试通过标准输入传递
    cmd = [gemini_cli_path, "-m", model, "-p", f"{prompt}\n\n代码文件内容:\n{code_with_error}"]
    
    print(f"执行命令（带代码内容）...")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=30
    )
    
    print(f"返回码: {result.returncode}")
    if result.stdout:
        print("输出预览:")
        print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        
except subprocess.TimeoutExpired:
    print("命令超时（30秒）")
except Exception as e:
    print(f"错误: {e}")
finally:
    if os.path.exists(temp_file):
        os.unlink(temp_file)

# 测试2：简单的非交互式调用
print("\n\n测试2：简单的非交互式调用")
print("-" * 40)

simple_prompt = "请说 'Hello World'"

try:
    cmd = [gemini_cli_path, "-m", model, "-p", simple_prompt]
    
    print(f"执行简单命令...")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=30
    )
    
    print(f"返回码: {result.returncode}")
    if result.stdout:
        print("输出:")
        print(result.stdout)
    if result.stderr:
        print("错误:")
        print(result.stderr)
        
except subprocess.TimeoutExpired:
    print("命令超时（30秒）")
except Exception as e:
    print(f"错误: {e}")

# 测试3：检查 Gemini CLI 版本
print("\n\n测试3：检查 Gemini CLI")
print("-" * 40)

try:
    # 尝试获取版本信息
    cmd = [gemini_cli_path, "--version"]
    
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=5
    )
    
    print(f"返回码: {result.returncode}")
    if result.stdout:
        print("输出:")
        print(result.stdout)
    if result.stderr:
        print("错误:")
        print(result.stderr)
        
except Exception as e:
    print(f"错误: {e}")

print("\n测试完成")