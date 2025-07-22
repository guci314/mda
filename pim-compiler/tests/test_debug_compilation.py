#!/usr/bin/env python3
"""
调试 Hello World PIM 的编译过程 - 查看 Gemini CLI 输出
"""
import os
import sys
from pathlib import Path
import shutil
import logging
import subprocess

# 添加编译器到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 设置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_gemini_cli_directly():
    """直接测试 Gemini CLI 命令"""
    
    # 检查 Gemini CLI
    gemini_path = shutil.which("gemini")
    if not gemini_path:
        logger.error("Gemini CLI not found!")
        return
    
    logger.info(f"Found Gemini CLI at: {gemini_path}")
    
    # 准备测试目录
    test_dir = Path("test_debug_output")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # 复制 PIM 文件
    pim_file = Path(__file__).parent.parent.parent / "hello_world_pim.md"
    shutil.copy(pim_file, test_dir / "hello_world_pim.md")
    
    # 创建简单的提示文件
    prompt_file = test_dir / "code_gen_prompt.txt"
    with open(prompt_file, 'w') as f:
        f.write("""你是一个专业的 fastapi 开发工程师。

请根据提供的 hello_world_pim.md 文件生成完整的 FastAPI 代码实现。

在当前目录下创建以下文件：
1. main.py - FastAPI 应用的入口点
2. requirements.txt - Python 依赖

main.py 应包含：
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"message": "Hello World!"}
```

请生成这些文件。
""")
    
    # 运行 Gemini CLI
    logger.info("Running Gemini CLI...")
    cmd = [
        gemini_path,
        "run",
        str(prompt_file),
        "-m", "gemini-2.0-flash-exp"
    ]
    
    logger.info(f"Command: {' '.join(cmd)}")
    
    # 在测试目录中运行
    result = subprocess.run(
        cmd,
        cwd=str(test_dir),
        capture_output=True,
        text=True
    )
    
    logger.info(f"Return code: {result.returncode}")
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
                logger.info(f"  内容预览:\n{f.read()[:200]}...")


def test_with_psm():
    """使用 PSM 测试代码生成"""
    
    # 准备测试目录
    test_dir = Path("test_with_psm")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # 创建目录结构
    (test_dir / "pim").mkdir()
    (test_dir / "psm").mkdir()
    (test_dir / "generated").mkdir()
    (test_dir / "generated" / "hello_world_pim").mkdir()
    
    # 复制文件
    pim_file = Path(__file__).parent.parent.parent / "hello_world_pim.md"
    shutil.copy(pim_file, test_dir / "pim" / "hello_world_pim.md")
    
    # 从之前的编译结果复制 PSM
    psm_source = Path("/home/guci/aiProjects/mda/pim-engine/classpath/hello_world_pim/psm/hello_world_pim_psm.md")
    if psm_source.exists():
        shutil.copy(psm_source, test_dir / "psm" / "hello_world_pim_psm.md")
    else:
        logger.error("PSM file not found!")
        return
    
    # 创建代码生成提示
    prompt_file = test_dir / "code_gen_prompt.txt"
    with open(prompt_file, 'w') as f:
        f.write("""你是一个专业的 fastapi 开发工程师，精通 FastAPI 框架。

我有一个平台特定模型（PSM）文件，位于：psm/hello_world_pim_psm.md

请根据这个 PSM 文件生成完整的 fastapi 代码实现。

要求：
1. 仔细阅读 PSM 文件，理解所有技术细节
2. 在 generated/hello_world_pim/ 目录下创建完整的项目结构
3. 必须生成以下核心文件：
   - main.py（应用程序入口点）
   - requirements.txt（Python 依赖）
   - README.md（项目说明文档）

特别注意：main.py 必须是项目的入口点，能够启动整个应用程序。

请生成这些文件。
""")
    
    # 运行 Gemini CLI
    logger.info("Running Gemini CLI with PSM...")
    cmd = [
        shutil.which("gemini"),
        "run",
        str(prompt_file),
        "-m", "gemini-2.0-flash-exp"
    ]
    
    result = subprocess.run(
        cmd,
        cwd=str(test_dir),
        capture_output=True,
        text=True
    )
    
    logger.info(f"Return code: {result.returncode}")
    logger.info(f"STDOUT (first 1000 chars):\n{result.stdout[:1000]}")
    
    # 检查生成的文件
    logger.info("\n=== 检查生成的文件 ===")
    generated_dir = test_dir / "generated" / "hello_world_pim"
    if generated_dir.exists():
        for root, dirs, files in os.walk(generated_dir):
            level = root.replace(str(generated_dir), '').count(os.sep)
            indent = ' ' * 2 * level
            logger.info(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                logger.info(f"{subindent}{file}")
    
    # 检查 main.py
    main_py = generated_dir / "main.py"
    if main_py.exists():
        logger.info("\n✓ main.py 生成成功！")
    else:
        logger.error("\n✗ main.py 未生成")
        # 检查其他位置
        for py_file in test_dir.rglob("*.py"):
            logger.info(f"  找到 Python 文件: {py_file.relative_to(test_dir)}")


if __name__ == "__main__":
    logger.info("=== 测试 1: 直接测试 Gemini CLI ===")
    test_gemini_cli_directly()
    
    logger.info("\n\n=== 测试 2: 使用 PSM 测试代码生成 ===")
    test_with_psm()