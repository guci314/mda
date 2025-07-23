"""测试日志输出功能"""

import pytest
from pathlib import Path
import tempfile

from src.compiler.core.pure_gemini_compiler import PureGeminiCompiler
from src.compiler.config import CompilerConfig


def test_find_project_with_logging(tmp_path, caplog):
    """测试项目查找的日志输出"""
    # 创建嵌套的项目结构
    project_dir = tmp_path / "my-service"
    project_dir.mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "app").mkdir()
    (project_dir / "main.py").touch()
    
    # 创建编译器
    config = CompilerConfig()
    compiler = PureGeminiCompiler(config)
    
    # 启用日志捕获
    import logging
    caplog.set_level(logging.INFO)
    
    # 运行测试方法
    passed, error = compiler._run_tests(tmp_path)
    
    # 检查日志输出
    assert "TEST EXECUTION DETAILS:" in caplog.text
    assert f"Code directory: {tmp_path}" in caplog.text
    assert f"Found project directory: {project_dir}" in caplog.text
    assert f"Using test location: {project_dir / 'tests'}" in caplog.text
    
    # 打印日志以便查看
    print("\n" + "=" * 60)
    print("CAPTURED LOGS:")
    print(caplog.text)
    print("=" * 60)