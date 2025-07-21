#!/usr/bin/env python3
"""直接测试 Gemini CLI 在项目目录中的调用"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file}")

# 创建测试目录和文件
test_dir = Path("./test_gemini_fix")
test_dir.mkdir(exist_ok=True)

# 创建有错误的文件
error_file = test_dir / "error_code.py"
with open(error_file, 'w') as f:
    f.write('''from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., regex="^[a-zA-Z][a-zA-Z0-9_]*$")  # 应该用 pattern
    
def test():
    return undefined_var  # 未定义的变量
''')

print(f"\n创建测试文件: {error_file}")

# 测试 Gemini CLI
print("\n测试 Gemini CLI 调用...")

# 保存当前目录
original_dir = os.getcwd()

try:
    # 切换到测试目录
    os.chdir(test_dir)
    print(f"切换到目录: {os.getcwd()}")
    
    # 准备环境变量
    env = os.environ.copy()
    
    # 设置代理
    proxy_host = os.getenv("PROXY_HOST", "127.0.0.1")
    proxy_port = os.getenv("PROXY_PORT", "7890")
    if proxy_host and proxy_port:
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        env["HTTP_PROXY"] = proxy_url
        env["HTTPS_PROXY"] = proxy_url
        print(f"使用代理: {proxy_url}")
    
    # API key 设置
    if "GOOGLE_AI_STUDIO_KEY" in env and "GEMINI_API_KEY" not in env:
        env["GEMINI_API_KEY"] = env["GOOGLE_AI_STUDIO_KEY"]
    
    # 检查 API key
    if "GEMINI_API_KEY" in env:
        print(f"✓ 找到 GEMINI_API_KEY: {env['GEMINI_API_KEY'][:10]}...")
    else:
        print("❌ 未找到 GEMINI_API_KEY")
    
    # Gemini CLI 路径
    gemini_cli_path = "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini"
    if not os.path.exists(gemini_cli_path):
        gemini_cli_path = "gemini"
        print("使用系统 PATH 中的 gemini")
    else:
        print(f"使用 Gemini CLI: {gemini_cli_path}")
    
    # 构建提示
    prompt = """查看 error_code.py 文件，发现以下问题：
1. 使用了过时的 'regex' 参数（应该用 'pattern'）
2. 使用了未定义的变量 undefined_var

请修复这些错误。"""
    
    # 构建命令
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    cmd = [gemini_cli_path, "-m", model, "-p", prompt]
    
    print(f"\n执行命令: {' '.join(cmd[:4])}...")
    print(f"模型: {model}")
    
    # 执行命令
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=60
    )
    
    print(f"\n返回码: {result.returncode}")
    
    if result.stdout:
        print("\n标准输出:")
        print("-" * 60)
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        print("-" * 60)
    
    if result.stderr:
        print("\n错误输出:")
        print("-" * 60)
        print(result.stderr)
        print("-" * 60)
    
    # 检查文件是否被修改
    print("\n检查文件内容...")
    with open("error_code.py", 'r') as f:
        content = f.read()
    print("文件内容:")
    print("-" * 60)
    print(content)
    print("-" * 60)
    
finally:
    # 恢复目录
    os.chdir(original_dir)
    print(f"\n恢复到原始目录: {os.getcwd()}")