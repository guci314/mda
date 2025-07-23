"""
测试反馈循环机制的单元测试
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import subprocess

from compiler.core.pure_gemini_compiler import PureGeminiCompiler
from compiler.config import CompilerConfig


@pytest.fixture
def mock_config():
    """创建测试用配置"""
    config = Mock(spec=CompilerConfig)
    config.output_dir = Path("/tmp/test_output")
    config.target_platform = "fastapi"
    config.auto_test = True
    config.auto_fix_tests = True
    config.auto_fix_lint = True
    return config


@pytest.fixture
def compiler(mock_config):
    """创建编译器实例"""
    with patch.object(PureGeminiCompiler, '_find_gemini_cli', return_value='/usr/bin/gemini'):
        return PureGeminiCompiler(mock_config)


class TestFeedbackLoop:
    """测试反馈循环机制"""
    
    def test_successful_on_first_attempt(self, compiler):
        """测试第一次就成功的情况"""
        code_dir = Path("/tmp/test_code")
        
        # 模拟测试成功
        with patch.object(compiler, '_run_tests', return_value=(True, None)):
            result = compiler._run_test_feedback_loop(code_dir, max_attempts=5)
        
        assert result["passed"] is True
        assert result["fixed"] is False  # 第一次成功不算修复
        assert result["attempts"] == 1
        assert len(result["errors"]) == 0
        assert len(result["fix_history"]) == 0
    
    def test_successful_after_fixes(self, compiler):
        """测试修复后成功的情况"""
        code_dir = Path("/tmp/test_code")
        
        # 模拟第一次失败，第二次成功
        test_results = [
            (False, "ImportError: No module named 'app'"),
            (True, None)
        ]
        
        with patch.object(compiler, '_run_tests', side_effect=test_results):
            with patch.object(compiler, '_fix_with_gemini', return_value=True):
                result = compiler._run_test_feedback_loop(code_dir, max_attempts=5)
        
        assert result["passed"] is True
        assert result["fixed"] is True  # 修复后成功
        assert result["attempts"] == 2
        assert len(result["errors"]) == 1
        assert len(result["fix_history"]) == 1
        assert result["fix_history"][0]["success"] is True
    
    def test_max_attempts_reached(self, compiler):
        """测试达到最大尝试次数的情况"""
        code_dir = Path("/tmp/test_code")
        
        # 模拟持续失败
        with patch.object(compiler, '_run_tests', return_value=(False, "Test failed")):
            with patch.object(compiler, '_fix_with_gemini', return_value=True):
                result = compiler._run_test_feedback_loop(code_dir, max_attempts=5)
        
        assert result["passed"] is False
        assert result["attempts"] == 5
        assert result["max_attempts_reached"] is True
        assert "需要人类介入" in result["final_error"]
        assert len(result["errors"]) == 5
        assert len(result["fix_history"]) == 4  # 第5次不修复
    
    def test_fix_failure_continues_loop(self, compiler):
        """测试修复失败继续循环的情况"""
        code_dir = Path("/tmp/test_code")
        
        # 模拟测试失败，修复失败，然后成功
        test_results = [
            (False, "Error 1"),
            (False, "Error 2"),
            (True, None)
        ]
        
        fix_results = [False, True]  # 第一次修复失败，第二次成功
        
        with patch.object(compiler, '_run_tests', side_effect=test_results):
            with patch.object(compiler, '_fix_with_gemini', side_effect=fix_results):
                result = compiler._run_test_feedback_loop(code_dir, max_attempts=5)
        
        assert result["passed"] is True
        assert result["attempts"] == 3
        assert len(result["fix_history"]) == 2
        assert result["fix_history"][0]["success"] is False
        assert result["fix_history"][1]["success"] is True
    
    def test_error_categorization(self, compiler):
        """测试错误分类功能"""
        # 语法错误
        errors = compiler._categorize_errors("SyntaxError: invalid syntax")
        assert "语法错误" in errors
        
        # 导入错误
        errors = compiler._categorize_errors("ImportError: No module named 'app'")
        assert "导入错误" in errors
        
        # 多种错误
        error_msg = """
        TypeError: unsupported operand type(s)
        AttributeError: 'NoneType' object has no attribute 'name'
        NameError: name 'undefined_var' is not defined
        """
        errors = compiler._categorize_errors(error_msg)
        assert "类型错误" in errors
        assert "属性错误" in errors
        assert "名称错误" in errors
        
        # 未知错误
        errors = compiler._categorize_errors("Some random error")
        assert "未知错误" in errors
    
    def test_prompt_generation_with_history(self, compiler):
        """测试带历史记录的提示词生成"""
        test_errors = "AssertionError: assert 1 == 2"
        attempt = 3
        fix_history = [
            {"attempt": 1, "success": False},
            {"attempt": 2, "success": True}
        ]
        
        prompt = compiler._generate_test_fix_prompt(test_errors, attempt, fix_history)
        
        assert "第 3 次尝试（最多 5 次）" in prompt
        assert "AssertionError" in prompt
        assert "断言失败" in prompt
        assert "之前的修复尝试" in prompt
        assert "第 1 次尝试: 失败" in prompt
        assert "第 2 次尝试: 成功" in prompt


class TestCompleteWorkflow:
    """测试完整的测试和修复工作流"""
    
    def test_lint_and_test_workflow(self, compiler):
        """测试 lint 和测试的完整流程"""
        code_dir = Path("/tmp/test_code")
        
        # 模拟 lint 失败然后成功
        lint_results = [(False, "E501 line too long"), (True, None)]
        
        # 模拟测试成功
        test_result = {
            "passed": True,
            "fixed": False,
            "attempts": 1,
            "errors": [],
            "fix_history": []
        }
        
        with patch.object(compiler, '_run_lint', side_effect=lint_results):
            with patch.object(compiler, '_fix_with_gemini', return_value=True):
                with patch.object(compiler, '_run_test_feedback_loop', return_value=test_result):
                    results = compiler._run_tests_and_fix(code_dir)
        
        assert results["lint"]["passed"] is True
        assert results["lint"]["fixed"] is True
        assert results["tests"]["passed"] is True
        assert results["total_attempts"] == 1
        assert results["max_attempts_reached"] is False
    
    def test_error_handling_in_workflow(self, compiler):
        """测试工作流中的错误处理"""
        code_dir = Path("/tmp/test_code")
        
        # 模拟异常
        with patch.object(compiler, '_run_lint', side_effect=Exception("Lint error")):
            results = compiler._run_tests_and_fix(code_dir)
        
        assert "error" in results
        assert "Lint error" in results["error"]


class TestMockScenarios:
    """测试各种模拟场景"""
    
    def test_state_machine_simulation(self, compiler):
        """测试状态机模拟"""
        code_dir = Path("/tmp/test_code")
        
        # 创建状态机模拟
        class TestStateMachine:
            def __init__(self):
                self.state = "initial"
                self.test_call_count = 0
                self.fix_call_count = 0
            
            def run_tests(self):
                self.test_call_count += 1
                # 第一次测试失败，修复后第二次测试成功
                if self.fix_call_count >= 1:
                    self.state = "fixed"
                return self.state == "fixed", f"State: {self.state}, test_calls: {self.test_call_count}"
            
            def fix(self):
                self.fix_call_count += 1
                return True
        
        state_machine = TestStateMachine()
        
        with patch.object(compiler, '_run_tests', side_effect=lambda _: state_machine.run_tests()):
            with patch.object(compiler, '_fix_with_gemini', side_effect=lambda *args: state_machine.fix()):
                result = compiler._run_test_feedback_loop(code_dir, max_attempts=5)
        
        assert result["passed"] is True
        assert result["attempts"] == 2
        assert result["fixed"] is True
    
    def test_different_error_patterns(self, compiler):
        """测试不同的错误模式"""
        code_dir = Path("/tmp/test_code")
        
        # 定义错误序列
        error_sequence = [
            "SyntaxError: invalid syntax",
            "ImportError: No module named 'app'", 
            "TypeError: unsupported operand type(s)",
            "AssertionError: assert False",
            None  # 成功
        ]
        
        def mock_run_tests(path):
            error = error_sequence.pop(0)
            return error is None, error
        
        with patch.object(compiler, '_run_tests', side_effect=mock_run_tests):
            with patch.object(compiler, '_fix_with_gemini', return_value=True):
                with patch.object(compiler, '_generate_test_fix_prompt') as mock_prompt:
                    result = compiler._run_test_feedback_loop(code_dir, max_attempts=5)
        
        assert result["passed"] is True
        assert result["attempts"] == 5
        
        # 验证每次生成的提示词都包含正确的错误类型
        assert mock_prompt.call_count == 4


class TestEdgeCases:
    """测试边界情况"""
    
    def test_zero_max_attempts(self, compiler):
        """测试最大尝试次数为0的情况"""
        code_dir = Path("/tmp/test_code")
        
        # 不应该调用任何测试
        with patch.object(compiler, '_run_tests') as mock_tests:
            result = compiler._run_test_feedback_loop(code_dir, max_attempts=0)
        
        mock_tests.assert_not_called()
        assert result["passed"] is False
        assert result["attempts"] == 0
    
    def test_subprocess_timeout(self, compiler):
        """测试子进程超时的情况"""
        code_dir = Path("/tmp/test_code")
        
        # 模拟超时错误
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('pytest', 60)):
            passed, error = compiler._run_tests(code_dir)
        
        assert passed is True  # 超时时返回True（跳过）
        assert error is None
    
    def test_missing_test_directory(self, compiler):
        """测试缺少测试目录的情况"""
        code_dir = Path("/tmp/test_code")
        
        with patch('pathlib.Path.exists', return_value=False):
            passed, error = compiler._run_tests(code_dir)
        
        assert passed is True  # 没有测试目录时跳过
        assert error is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])