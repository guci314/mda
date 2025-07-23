"""测试绝对路径日志输出"""

import pytest
from pathlib import Path
import logging

from src.compiler.core.pure_gemini_compiler import PureGeminiCompiler
from src.compiler.config import CompilerConfig


def test_absolute_path_logging(tmp_path, caplog):
    """测试是否记录绝对路径"""
    # 创建测试 PIM 文件
    pim_file = tmp_path / "test_pim.md"
    pim_file.write_text("""# 测试 PIM

## 领域信息
- **领域名称**: test-domain
- **版本**: 1.0.0

## 业务实体
无

## 业务服务
### TestService
- **方法**: test()
""")
    
    # 配置
    config = CompilerConfig(
        output_dir=tmp_path / "output",
        enable_lint=False,
        auto_test=False  # 禁用测试以加快速度
    )
    
    # 创建编译器
    compiler = PureGeminiCompiler(config)
    
    # 设置日志级别
    caplog.set_level(logging.INFO)
    
    # 编译（只生成 PSM）
    result = compiler.compile(pim_file)
    
    # 检查日志中的绝对路径
    log_text = caplog.text
    
    # 检查 PSM 生成日志
    assert "PSM GENERATION DETAILS:" in log_text
    assert "PIM source file (absolute):" in log_text
    assert "Expected PSM output (absolute):" in log_text
    assert "Working directory (absolute):" in log_text
    assert "PSM parent directory (absolute):" in log_text
    
    # 检查 Gemini CLI 工作目录日志
    assert "Gemini CLI working directory (absolute):" in log_text
    
    # 打印日志以便查看
    print("\n" + "=" * 60)
    print("CAPTURED LOGS (Absolute Paths):")
    print("=" * 60)
    # 只打印包含路径的行
    for line in log_text.split('\n'):
        if 'absolute' in line.lower() or 'directory' in line.lower():
            print(line)
    print("=" * 60)