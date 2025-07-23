"""测试编译过程中的 API 重试机制"""

import pytest
from unittest.mock import patch, MagicMock, call
import subprocess
from pathlib import Path

from src.compiler.core.pure_gemini_compiler import PureGeminiCompiler
from src.compiler.config import CompilerConfig


class TestCompileWithRetry:
    """测试编译过程中的 API 重试"""
    
    def test_psm_generation_with_api_retry(self, tmp_path):
        """测试 PSM 生成时的 API 重试"""
        # 创建测试 PIM 文件
        pim_file = tmp_path / "test.md"
        pim_file.write_text("# Test PIM\n\nThis is a test.")
        
        # 创建输出目录
        output_dir = tmp_path / "output"
        
        # 配置
        config = CompilerConfig(enable_lint=False)
        
        # 模拟 subprocess 调用
        # 第一次：API 500 错误
        # 第二次：成功
        mock_results = [
            # 第一次 PSM 生成：API 500 错误
            MagicMock(
                returncode=1,
                stderr='API Error: got status: INTERNAL. {"error":{"code":500,"message":"An internal error has occurred."}}',
                stdout=""
            ),
            # 第二次 PSM 生成：成功
            MagicMock(
                returncode=0,
                stderr="",
                stdout="PSM generated successfully"
            )
        ]
        
        with patch('subprocess.run', side_effect=mock_results) as mock_run:
            with patch.object(PureGeminiCompiler, '_find_gemini_cli', return_value='/usr/bin/gemini'):
                # 创建编译器
                compiler = PureGeminiCompiler(config)
                
                # 模拟 PSM 文件生成
                def create_psm_file(*args, **kwargs):
                    # 在第二次调用后创建 PSM 文件
                    if mock_run.call_count == 2:
                        psm_dir = output_dir / "psm"
                        psm_dir.mkdir(parents=True, exist_ok=True)
                        psm_file = psm_dir / "test_psm.md"
                        psm_file.write_text("# Test PSM\n\nGenerated PSM content.")
                    return mock_results[mock_run.call_count - 1]
                
                mock_run.side_effect = create_psm_file
                
                # 修改配置输出目录
                compiler.config.output_dir = output_dir
                
                # 执行编译（只生成 PSM）
                with patch.object(compiler, '_generate_code', return_value=True):
                    with patch.object(compiler, '_run_tests_and_fix', return_value={"passed": True}):
                        result = compiler.compile(pim_file)
                
                # 验证结果
                assert mock_run.call_count == 2  # 第一次失败，第二次成功
                
    def test_code_generation_with_api_retry(self, tmp_path):
        """测试代码生成时的 API 重试"""
        # 创建测试 PIM 文件和 PSM 文件
        pim_file = tmp_path / "test.md"
        pim_file.write_text("# Test PIM\n\nThis is a test.")
        
        output_dir = tmp_path / "output"
        psm_dir = output_dir / "psm"
        psm_dir.mkdir(parents=True, exist_ok=True)
        psm_file = psm_dir / "test_psm.md"
        psm_file.write_text("# Test PSM\n\nTest PSM content.")
        
        # 配置
        config = CompilerConfig(enable_lint=False)
        
        # 模拟代码生成的 subprocess 调用
        # 使用 Popen 模拟监控进度的情况
        class MockPopen:
            def __init__(self, *args, **kwargs):
                self.returncode = None
                self.call_count = getattr(MockPopen, 'call_count', 0) + 1
                MockPopen.call_count = self.call_count
                
            def poll(self):
                if self.call_count == 1:
                    # 第一次：API 500 错误
                    self.returncode = 1
                else:
                    # 第二次：成功
                    self.returncode = 0
                return self.returncode
                
            def communicate(self):
                if self.call_count == 1:
                    return "", 'API Error: got status: INTERNAL. {"error":{"code":500}}'
                else:
                    return "Success", ""
                    
            def terminate(self):
                pass
                
            def kill(self):
                pass
        
        MockPopen.call_count = 0
        
        with patch('subprocess.Popen', MockPopen):
            with patch.object(PureGeminiCompiler, '_find_gemini_cli', return_value='/usr/bin/gemini'):
                # 创建编译器
                compiler = PureGeminiCompiler(config)
                
                # 模拟代码文件生成
                def create_code_files(*args, **kwargs):
                    if MockPopen.call_count == 2:
                        code_dir = output_dir / "generated" / "test"
                        code_dir.mkdir(parents=True, exist_ok=True)
                        (code_dir / "main.py").write_text("print('Hello')")
                    
                with patch.object(compiler, '_check_key_files', side_effect=create_code_files):
                    # 执行代码生成
                    result = compiler._generate_code(psm_file, output_dir / "generated" / "test")
                
                # 验证进行了重试
                assert MockPopen.call_count == 2