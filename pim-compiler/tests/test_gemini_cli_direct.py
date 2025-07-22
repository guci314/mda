#!/usr/bin/env python3
"""
直接测试 Gemini CLI 生成代码
"""
import os
import sys
from pathlib import Path
import shutil
import logging
import subprocess
import time

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_gemini_cli_simple():
    """测试 Gemini CLI 生成简单的 main.py"""
    
    # 准备测试目录
    test_dir = Path("test_gemini_simple")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # 简单的提示
    prompt = """请在当前目录创建一个 main.py 文件，内容如下：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"message": "Hello World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

请创建这个文件。"""
    
    # 运行 Gemini CLI
    logger.info("Running Gemini CLI with simple prompt...")
    cmd = [
        shutil.which("gemini"),
        "-m", "gemini-2.0-flash-exp",
        "-p", prompt,
        "-y"  # 自动确认
    ]
    
    logger.info(f"Command: {' '.join(cmd)}")
    logger.info(f"Working directory: {test_dir}")
    
    # 执行命令
    start_time = time.time()
    result = subprocess.run(
        cmd,
        cwd=str(test_dir),
        capture_output=True,
        text=True,
        timeout=60
    )
    
    execution_time = time.time() - start_time
    logger.info(f"Execution time: {execution_time:.2f}s")
    logger.info(f"Return code: {result.returncode}")
    
    if result.stdout:
        logger.info(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        logger.error(f"STDERR:\n{result.stderr}")
    
    # 检查生成的文件
    logger.info("\n=== 检查生成的文件 ===")
    for file in test_dir.iterdir():
        logger.info(f"  {file.name}")
        if file.name == "main.py":
            logger.info("  ✓ main.py 生成成功！")
            with open(file, 'r') as f:
                content = f.read()
                logger.info(f"  内容预览:\n{content[:200]}...")
                logger.info(f"  文件大小: {len(content)} 字节")


def test_with_psm_structure():
    """使用目录结构测试"""
    
    # 准备测试目录
    test_dir = Path("test_with_structure")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # 创建目录结构
    (test_dir / "generated").mkdir()
    (test_dir / "generated" / "hello_world").mkdir()
    
    # 提示
    prompt = """请在 generated/hello_world/ 目录下创建以下文件：

1. main.py - FastAPI 应用入口，包含一个 /hello 端点返回 {"message": "Hello World!"}
2. requirements.txt - 包含 fastapi 和 uvicorn

请创建这些文件。"""
    
    # 运行 Gemini CLI
    logger.info("\nRunning Gemini CLI with directory structure...")
    cmd = [
        shutil.which("gemini"),
        "-m", "gemini-2.0-flash-exp",
        "-p", prompt,
        "-y"
    ]
    
    result = subprocess.run(
        cmd,
        cwd=str(test_dir),
        capture_output=True,
        text=True,
        timeout=60
    )
    
    logger.info(f"Return code: {result.returncode}")
    
    # 检查生成的文件
    logger.info("\n=== 检查生成的文件 ===")
    generated_dir = test_dir / "generated" / "hello_world"
    if generated_dir.exists():
        for file in generated_dir.iterdir():
            logger.info(f"  {file.name}")
            if file.name == "main.py":
                logger.info("  ✓ main.py 生成成功！")
    else:
        logger.error("Generated directory not found!")
        # 列出所有文件
        for root, dirs, files in os.walk(test_dir):
            level = root.replace(str(test_dir), '').count(os.sep)
            indent = ' ' * 2 * level
            logger.info(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                logger.info(f"{subindent}{file}")


if __name__ == "__main__":
    logger.info("=== 测试 1: 简单生成 main.py ===")
    test_gemini_cli_simple()
    
    logger.info("\n\n=== 测试 2: 带目录结构的生成 ===")
    test_with_psm_structure()