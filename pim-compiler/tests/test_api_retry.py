"""测试 API 500 错误重试机制"""

import pytest
from unittest.mock import patch, MagicMock
import subprocess
from pathlib import Path

from src.compiler.core.pure_gemini_compiler import PureGeminiCompiler
from src.compiler.config import CompilerConfig


class TestAPIRetry:
    """测试 API 重试机制"""
    
    @pytest.fixture
    def compiler(self, tmp_path):
        """创建编译器实例"""
        config = CompilerConfig()
        with patch.object(PureGeminiCompiler, '_find_gemini_cli', return_value='/usr/bin/gemini'):
            return PureGeminiCompiler(config)
    
    def test_api_500_error_retry(self, compiler, tmp_path):
        """测试 API 500 错误时的重试机制"""
        # 准备测试数据
        work_dir = tmp_path
        prompt = "test prompt"
        
        # 模拟 subprocess.run 的返回值
        # 第一次和第二次返回 API 500 错误，第三次成功
        mock_results = [
            # 第一次：API 500 错误
            MagicMock(
                returncode=1,
                stderr='API Error: got status: INTERNAL. {"error":{"code":500,"message":"An internal error has occurred."}}',
                stdout=""
            ),
            # 第二次：API 500 错误
            MagicMock(
                returncode=1,
                stderr='API Error: got status: INTERNAL. {"error":{"code":500,"message":"An internal error has occurred."}}',
                stdout=""
            ),
            # 第三次：成功
            MagicMock(
                returncode=0,
                stderr="",
                stdout="Success"
            )
        ]
        
        with patch('subprocess.run', side_effect=mock_results) as mock_run:
            # 执行方法
            result = compiler._execute_gemini_cli(prompt, work_dir)
            
            # 验证结果
            assert result is True
            # 验证调用了3次
            assert mock_run.call_count == 3
            
    def test_api_500_error_all_retries_fail(self, compiler, tmp_path):
        """测试所有重试都失败的情况"""
        work_dir = tmp_path
        prompt = "test prompt"
        
        # 模拟所有调用都返回 API 500 错误
        mock_result = MagicMock(
            returncode=1,
            stderr='API Error: got status: INTERNAL. {"error":{"code":500,"message":"An internal error has occurred."}}',
            stdout=""
        )
        
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            # 执行方法
            result = compiler._execute_gemini_cli(prompt, work_dir)
            
            # 验证结果
            assert result is False
            # 验证调用了3次（最大重试次数）
            assert mock_run.call_count == 3
            
    def test_non_api_error_no_retry(self, compiler, tmp_path):
        """测试非 API 错误时不进行重试"""
        work_dir = tmp_path
        prompt = "test prompt"
        
        # 模拟其他类型的错误
        mock_result = MagicMock(
            returncode=1,
            stderr="Some other error",
            stdout=""
        )
        
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            # 执行方法
            result = compiler._execute_gemini_cli(prompt, work_dir)
            
            # 验证结果
            assert result is False
            # 验证只调用了1次（没有重试）
            assert mock_run.call_count == 1
            
    def test_timeout_error_no_retry(self, compiler, tmp_path):
        """测试超时错误时不进行重试"""
        work_dir = tmp_path
        prompt = "test prompt"
        
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('cmd', 300)) as mock_run:
            # 执行方法
            result = compiler._execute_gemini_cli(prompt, work_dir)
            
            # 验证结果
            assert result is False
            # 验证只调用了1次（没有重试）
            assert mock_run.call_count == 1
            
    def test_is_api_500_error_detection(self, compiler):
        """测试 API 500 错误检测方法"""
        # 测试各种 API 500 错误模式
        api_500_errors = [
            'API Error: got status: INTERNAL. {"error":{"code":500,"message":"An internal error has occurred."}}',
            'status: INTERNAL',
            '"code":500',
            'Internal error has occurred',
            'API Error: got status: INTERNAL'
        ]
        
        for error_text in api_500_errors:
            assert compiler._is_api_500_error(error_text) is True
            
        # 测试非 API 500 错误
        non_api_errors = [
            "Connection timeout",
            "File not found",
            "Invalid syntax",
            ""
        ]
        
        for error_text in non_api_errors:
            assert compiler._is_api_500_error(error_text) is False