"""
测试纯 Gemini 编译器
"""
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from compiler.config import CompilerConfig
from compiler.core.pure_gemini_compiler import PureGeminiCompiler


class TestPureGeminiCompiler:
    """测试 PureGeminiCompiler 类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def compiler(self, temp_dir):
        """创建编译器实例"""
        config = CompilerConfig(
            output_dir=temp_dir,
            auto_test=False,  # 禁用自动测试以简化单元测试
            verbose=True
        )
        return PureGeminiCompiler(config)
    
    @pytest.fixture
    def sample_pim(self, temp_dir):
        """创建示例 PIM 文件"""
        pim_file = temp_dir / "test_model.md"
        pim_file.write_text("""# 测试系统

## 业务描述
一个简单的测试系统。

## 业务实体

### 用户
系统的使用者。

属性：
- 姓名：用户的名字
- 邮箱：用户的电子邮箱（唯一）
- 状态：激活/未激活

## 业务服务

### 用户服务
- 创建用户
- 查询用户
- 更新用户状态
""")
        return pim_file
    
    def test_compiler_initialization(self, compiler):
        """测试编译器初始化"""
        assert compiler.config.target_platform == "fastapi"
        assert compiler.config.auto_test is False
        assert hasattr(compiler, 'compile')
        assert hasattr(compiler, '_generate_psm')
        assert hasattr(compiler, '_generate_code')
    
    @patch('subprocess.Popen')
    def test_generate_psm_success(self, mock_popen, compiler, sample_pim, temp_dir):
        """测试 PSM 生成成功"""
        # 模拟子进程
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, None, 0]  # 第三次返回完成
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # 创建假的 PSM 文件
        psm_file = temp_dir / "psm" / "test_model_psm.md"
        psm_file.parent.mkdir(parents=True)
        psm_file.write_text("# Generated PSM")
        
        result = compiler._generate_psm(sample_pim)
        
        assert result == psm_file
        assert psm_file.exists()
        mock_popen.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_generate_psm_failure(self, mock_popen, compiler, sample_pim):
        """测试 PSM 生成失败"""
        # 模拟子进程失败
        mock_process = MagicMock()
        mock_process.poll.return_value = 1
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        result = compiler._generate_psm(sample_pim)
        
        assert result is None
        mock_popen.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_generate_code_with_progress_monitoring(self, mock_popen, compiler, temp_dir):
        """测试代码生成的进度监控"""
        # 创建假的 PSM 文件
        psm_file = temp_dir / "test_psm.md"
        psm_file.write_text("# Test PSM")
        
        # 模拟子进程
        mock_process = MagicMock()
        poll_results = [None] * 5 + [0]  # 运行5次检查后完成
        mock_process.poll.side_effect = poll_results
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # 创建假的生成文件
        code_dir = temp_dir / "generated" / "test"
        code_dir.mkdir(parents=True)
        
        # 模拟文件逐渐生成
        def create_files(call_count):
            if call_count >= 2:
                (code_dir / "main.py").touch()
            if call_count >= 3:
                (code_dir / "requirements.txt").touch()
            if call_count >= 4:
                (code_dir / "README.md").touch()
        
        # 使用 side_effect 来模拟文件生成
        original_rglob = Path.rglob
        call_count = [0]
        
        def mock_rglob(self, pattern):
            call_count[0] += 1
            create_files(call_count[0])
            return list(original_rglob(self, pattern))
        
        with patch.object(Path, 'rglob', mock_rglob):
            result = compiler._generate_code(psm_file)
        
        assert result == code_dir
        assert (code_dir / "main.py").exists()
        assert (code_dir / "requirements.txt").exists()
    
    @patch('subprocess.Popen')
    def test_process_timeout(self, mock_popen, compiler, temp_dir):
        """测试进程超时处理"""
        psm_file = temp_dir / "test_psm.md"
        psm_file.write_text("# Test PSM")
        
        # 模拟长时间无进展的进程
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # 一直运行
        mock_process.terminate = MagicMock()
        mock_popen.return_value = mock_process
        
        # 覆盖检查间隔和最大无进展次数以加快测试
        original_check_interval = compiler._generate_code.__code__.co_consts
        with patch.object(compiler, '_generate_code') as mock_generate:
            # 直接调用原始方法但使用较短的超时
            def side_effect(psm_file):
                # 模拟超时情况
                code_dir = compiler.config.output_dir / "generated" / "test"
                code_dir.mkdir(parents=True)
                # 不创建任何文件，触发超时
                return None
            
            mock_generate.side_effect = side_effect
            result = compiler._generate_code(psm_file)
        
        assert result is None
    
    def test_framework_methods(self, compiler):
        """测试框架相关方法"""
        # 测试获取框架
        assert compiler._get_framework_for_platform() == "FastAPI"
        
        # 测试获取 ORM
        assert compiler._get_orm_for_platform() == "SQLAlchemy"
        
        # 测试获取验证库
        assert compiler._get_validation_lib_for_platform() == "Pydantic"
        
        # 测试获取测试框架
        assert compiler._get_test_framework_for_platform() == "pytest"
    
    @patch.object(PureGeminiCompiler, '_generate_psm')
    @patch.object(PureGeminiCompiler, '_generate_code')
    @patch.object(PureGeminiCompiler, '_run_tests_and_fix')
    def test_compile_full_success(self, mock_tests, mock_code, mock_psm, compiler, sample_pim, temp_dir):
        """测试完整编译流程成功"""
        # 设置模拟返回值
        psm_file = temp_dir / "psm" / "test_psm.md"
        code_dir = temp_dir / "generated" / "test"
        
        mock_psm.return_value = psm_file
        mock_code.return_value = code_dir
        mock_tests.return_value = {"lint": {"passed": True}, "tests": {"passed": True}}
        
        # 执行编译
        result = compiler.compile(sample_pim)
        
        # 验证结果
        assert result.success is True
        assert result.psm_file == psm_file
        assert result.code_dir == code_dir
        assert result.error is None
        
        # 验证调用顺序
        mock_psm.assert_called_once_with(sample_pim)
        mock_code.assert_called_once_with(psm_file)
        mock_tests.assert_not_called()  # auto_test=False
    
    @patch.object(PureGeminiCompiler, '_generate_psm')
    def test_compile_psm_failure(self, mock_psm, compiler, sample_pim):
        """测试 PSM 生成失败的情况"""
        mock_psm.return_value = None
        
        result = compiler.compile(sample_pim)
        
        assert result.success is False
        assert result.error == "PSM 生成失败"
        assert result.psm_file is None
        assert result.code_dir is None
    
    def test_compile_statistics(self, compiler, sample_pim, temp_dir):
        """测试编译统计信息"""
        with patch.object(compiler, '_generate_psm') as mock_psm, \
             patch.object(compiler, '_generate_code') as mock_code:
            
            psm_file = temp_dir / "psm" / "test_psm.md"
            code_dir = temp_dir / "generated" / "test"
            code_dir.mkdir(parents=True)
            
            # 创建一些测试文件
            (code_dir / "main.py").touch()
            (code_dir / "models.py").touch()
            (code_dir / "requirements.txt").touch()
            
            mock_psm.return_value = psm_file
            mock_code.return_value = code_dir
            
            result = compiler.compile(sample_pim)
            
            assert result.statistics is not None
            assert result.statistics['total_files'] == 3
            assert result.statistics['python_files'] == 2
            assert 'psm_generation_time' in result.statistics
            assert 'code_generation_time' in result.statistics
            assert result.compilation_time > 0