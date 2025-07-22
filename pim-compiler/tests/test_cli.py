"""
测试 CLI 工具
"""
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO


class TestCLI:
    """测试命令行界面"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_pim_file(self, temp_dir):
        """创建示例 PIM 文件"""
        pim_file = temp_dir / "test_model.md"
        pim_file.write_text("""# 测试模型

## 业务描述
测试用的简单模型。

## 业务实体
### 用户
- 姓名：字符串
- 邮箱：字符串（唯一）
""")
        return pim_file
    
    def run_cli(self, args):
        """运行 CLI 并捕获输出"""
        # 保存原始 argv
        original_argv = sys.argv
        
        # 捕获输出
        captured_output = StringIO()
        
        try:
            # 设置新的 argv
            sys.argv = ["pim-compiler"] + args
            
            # 导入并运行 main
            with patch('sys.stdout', captured_output):
                with patch('sys.stderr', captured_output):
                    # 动态导入以避免循环导入
                    import sys
                    sys.path.insert(0, str(Path(__file__).parent.parent))
                    from cli.main import main
                    
                    try:
                        main()
                        exit_code = 0
                    except SystemExit as e:
                        exit_code = e.code if e.code is not None else 0
                    except Exception as e:
                        exit_code = 1
                        print(f"Error: {e}", file=captured_output)
            
            return exit_code, captured_output.getvalue()
        finally:
            # 恢复原始 argv
            sys.argv = original_argv
    
    def test_help_option(self):
        """测试帮助选项"""
        exit_code, output = self.run_cli(["--help"])
        
        assert exit_code == 0
        assert "PIM Compiler" in output
        assert "将平台无关模型转换为可执行代码" in output
        assert "--output" in output
        assert "--platform" in output
    
    def test_version_option(self):
        """测试版本选项"""
        exit_code, output = self.run_cli(["--version"])
        
        assert exit_code == 0
        assert "3.0.0" in output
    
    def test_missing_pim_file(self):
        """测试缺少 PIM 文件参数"""
        exit_code, output = self.run_cli([])
        
        assert exit_code != 0
        assert "required" in output.lower() or "错误" in output
    
    def test_nonexistent_pim_file(self):
        """测试不存在的 PIM 文件"""
        exit_code, output = self.run_cli(["nonexistent.md"])
        
        assert exit_code == 1
        assert "不存在" in output or "not exist" in output.lower()
    
    @patch('compiler.compiler_factory.CompilerFactory.create_compiler')
    def test_compile_success(self, mock_create_compiler, sample_pim_file, temp_dir):
        """测试编译成功"""
        # 创建模拟编译器
        mock_compiler = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.psm_file = temp_dir / "psm" / "test_psm.md"
        mock_result.code_dir = temp_dir / "generated" / "test"
        mock_result.compilation_time = 5.2
        mock_result.statistics = {
            'total_files': 10,
            'python_files': 7,
            'psm_generation_time': 2.1,
            'code_generation_time': 3.1
        }
        mock_result.test_results = None
        mock_result.error = None
        
        mock_compiler.compile.return_value = mock_result
        mock_create_compiler.return_value = mock_compiler
        
        # 运行 CLI
        exit_code, output = self.run_cli([str(sample_pim_file)])
        
        assert exit_code == 0
        assert "编译成功" in output
        assert "生成的文件" in output
        assert "总编译时间" in output
    
    @patch('compiler.compiler_factory.CompilerFactory.create_compiler')
    def test_compile_failure(self, mock_create_compiler, sample_pim_file):
        """测试编译失败"""
        # 创建模拟编译器
        mock_compiler = MagicMock()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "测试错误信息"
        
        mock_compiler.compile.return_value = mock_result
        mock_create_compiler.return_value = mock_compiler
        
        # 运行 CLI
        exit_code, output = self.run_cli([str(sample_pim_file)])
        
        assert exit_code == 1
        assert "编译失败" in output
        assert "测试错误信息" in output
    
    def test_platform_option(self, sample_pim_file):
        """测试平台选项"""
        with patch('compiler.compiler_factory.CompilerFactory.create_compiler') as mock_create:
            mock_compiler = MagicMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_compiler.compile.return_value = mock_result
            mock_create.return_value = mock_compiler
            
            # 测试不同平台
            for platform in ["fastapi", "django", "flask"]:
                exit_code, output = self.run_cli([
                    str(sample_pim_file),
                    "--platform", platform
                ])
                
                # 验证配置被正确传递
                call_args = mock_create.call_args[0][0]
                assert call_args.target_platform == platform
    
    def test_output_option(self, sample_pim_file, temp_dir):
        """测试输出目录选项"""
        output_dir = temp_dir / "custom_output"
        
        with patch('compiler.compiler_factory.CompilerFactory.create_compiler') as mock_create:
            mock_compiler = MagicMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_compiler.compile.return_value = mock_result
            mock_create.return_value = mock_compiler
            
            exit_code, output = self.run_cli([
                str(sample_pim_file),
                "--output", str(output_dir)
            ])
            
            # 验证配置被正确传递
            call_args = mock_create.call_args[0][0]
            assert call_args.output_dir == output_dir
    
    def test_no_test_option(self, sample_pim_file):
        """测试跳过测试选项"""
        with patch('compiler.compiler_factory.CompilerFactory.create_compiler') as mock_create:
            mock_compiler = MagicMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_compiler.compile.return_value = mock_result
            mock_create.return_value = mock_compiler
            
            exit_code, output = self.run_cli([
                str(sample_pim_file),
                "--no-test"
            ])
            
            # 验证配置被正确传递
            call_args = mock_create.call_args[0][0]
            assert call_args.auto_test is False
    
    def test_verbose_option(self, sample_pim_file):
        """测试详细输出选项"""
        with patch('compiler.compiler_factory.CompilerFactory.create_compiler') as mock_create:
            mock_compiler = MagicMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_compiler.compile.return_value = mock_result
            mock_create.return_value = mock_compiler
            
            exit_code, output = self.run_cli([
                str(sample_pim_file),
                "--verbose"
            ])
            
            # 验证配置被正确传递
            call_args = mock_create.call_args[0][0]
            assert call_args.verbose is True
    
    def test_keyboard_interrupt(self, sample_pim_file):
        """测试键盘中断处理"""
        with patch('compiler.compiler_factory.CompilerFactory.create_compiler') as mock_create:
            mock_compiler = MagicMock()
            mock_compiler.compile.side_effect = KeyboardInterrupt()
            mock_create.return_value = mock_compiler
            
            exit_code, output = self.run_cli([str(sample_pim_file)])
            
            assert exit_code == 130
            assert "中断" in output