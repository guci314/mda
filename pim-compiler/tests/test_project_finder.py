"""测试项目目录查找功能"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.compiler.core.pure_gemini_compiler import PureGeminiCompiler
from src.compiler.config import CompilerConfig


class TestProjectFinder:
    """测试项目目录查找"""
    
    @pytest.fixture
    def compiler(self):
        """创建编译器实例"""
        config = CompilerConfig()
        return PureGeminiCompiler(config)
    
    def test_find_project_directory_direct(self, compiler, tmp_path):
        """测试直接在 code_dir 下的项目结构"""
        # 创建直接结构
        (tmp_path / "tests").mkdir()
        (tmp_path / "app").mkdir()
        (tmp_path / "main.py").touch()
        
        result = compiler._find_project_directory(tmp_path)
        assert result == tmp_path
        
    def test_find_project_directory_nested(self, compiler, tmp_path):
        """测试嵌套的项目结构"""
        # 创建嵌套结构
        project_dir = tmp_path / "hello-world-service"
        project_dir.mkdir()
        (project_dir / "tests").mkdir()
        (project_dir / "app").mkdir()
        (project_dir / "main.py").touch()
        
        result = compiler._find_project_directory(tmp_path)
        assert result == project_dir
        
    def test_find_project_directory_not_found(self, compiler, tmp_path):
        """测试找不到项目目录的情况"""
        # 不创建任何项目结构
        result = compiler._find_project_directory(tmp_path)
        assert result is None
        
    def test_find_project_directory_multiple_subdirs(self, compiler, tmp_path):
        """测试多个子目录的情况，应该返回第一个找到的"""
        # 创建多个项目目录
        for i in range(3):
            project_dir = tmp_path / f"project-{i}"
            project_dir.mkdir()
            (project_dir / "tests").mkdir()
            (project_dir / "app").mkdir()
            
        result = compiler._find_project_directory(tmp_path)
        assert result is not None
        assert result.name.startswith("project-")
        
    def test_run_tests_with_nested_structure(self, compiler, tmp_path):
        """测试嵌套结构下的测试运行"""
        # 创建嵌套的项目结构
        project_dir = tmp_path / "my-service"
        project_dir.mkdir()
        test_dir = project_dir / "tests"
        test_dir.mkdir()
        
        # 创建一个简单的测试文件
        test_file = test_dir / "test_example.py"
        test_file.write_text("""
def test_example():
    assert True
""")
        
        # 运行测试
        passed, error = compiler._run_tests(project_dir)
        assert passed is True
        assert error is None