"""
反馈循环的集成测试
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, Mock
import subprocess

from compiler.core.pure_gemini_compiler import PureGeminiCompiler
from compiler.config import CompilerConfig


@pytest.fixture
def real_test_environment():
    """创建真实的测试环境"""
    temp_dir = tempfile.mkdtemp(prefix="feedback_loop_integration_")
    code_dir = Path(temp_dir) / "generated" / "test_project"
    code_dir.mkdir(parents=True)
    
    # 创建一个有错误的项目
    (code_dir / "app").mkdir()
    (code_dir / "tests").mkdir()
    
    # 创建有语法错误的代码
    (code_dir / "app" / "__init__.py").touch()
    (code_dir / "app" / "models.py").write_text("""
from pydantic import BaseModel

class User(BaseModel):
    email: str
    name: str
    
    def get_display_name(self)  # 缺少冒号，语法错误
        return f"{self.name} <{self.email}>"
""")
    
    # 创建会失败的测试
    (code_dir / "tests" / "__init__.py").touch()
    (code_dir / "tests" / "test_models.py").write_text("""
import pytest
from app.models import User

def test_user_creation():
    user = User(email="test@example.com", name="Test User")
    assert user.email == "test@example.com"
    assert user.name == "Test User"

def test_display_name():
    user = User(email="test@example.com", name="Test User")
    assert user.get_display_name() == "Test User <test@example.com>"
""")
    
    # 创建 requirements.txt
    (code_dir / "requirements.txt").write_text("""
pydantic>=2.0.0
pytest>=7.0.0
""")
    
    yield code_dir
    
    # 清理
    shutil.rmtree(temp_dir)


class TestFeedbackLoopIntegration:
    """集成测试反馈循环功能"""
    
    def test_syntax_error_fix_simulation(self, real_test_environment):
        """测试修复语法错误的场景"""
        config = CompilerConfig(
            output_dir=real_test_environment.parent.parent,
            target_platform="fastapi",
            auto_test=True,
            auto_fix_tests=True
        )
        
        compiler = PureGeminiCompiler(config)
        
        # 模拟不同阶段的测试结果
        test_results = [
            # 第一次：语法错误
            (False, """
  File "app/models.py", line 8
    def get_display_name(self)
                              ^
SyntaxError: invalid syntax
"""),
            # 第二次：修复后测试通过
            (True, None)
        ]
        
        # 模拟 Gemini 修复代码
        def mock_fix_with_gemini(code_dir, error_msg, error_type):
            if "SyntaxError" in error_msg:
                # 修复语法错误
                models_file = code_dir / "app" / "models.py"
                content = models_file.read_text()
                fixed_content = content.replace(
                    "def get_display_name(self)",
                    "def get_display_name(self):"
                )
                models_file.write_text(fixed_content)
                return True
            return False
        
        with patch.object(compiler, '_run_tests', side_effect=test_results):
            with patch.object(compiler, '_fix_with_gemini', side_effect=mock_fix_with_gemini):
                result = compiler._run_test_feedback_loop(real_test_environment, max_attempts=5)
        
        assert result["passed"] is True
        assert result["fixed"] is True
        assert result["attempts"] == 2
        assert len(result["errors"]) == 1
        assert "SyntaxError" in result["errors"][0]["errors"]
    
    def test_import_error_fix_simulation(self):
        """测试修复导入错误的场景"""
        temp_dir = tempfile.mkdtemp(prefix="import_error_test_")
        code_dir = Path(temp_dir) / "project"
        code_dir.mkdir(parents=True)
        
        try:
            # 创建有导入错误的代码
            (code_dir / "app").mkdir()
            (code_dir / "tests").mkdir()
            
            (code_dir / "app" / "__init__.py").touch()
            (code_dir / "app" / "services.py").write_text("""
from app.models import User  # models.py 不存在

def create_user(email: str, name: str) -> User:
    return User(email=email, name=name)
""")
            
            (code_dir / "tests" / "__init__.py").touch()
            (code_dir / "tests" / "test_services.py").write_text("""
from app.services import create_user

def test_create_user():
    user = create_user("test@example.com", "Test")
    assert user.email == "test@example.com"
""")
            
            config = CompilerConfig(
                output_dir=temp_dir,
                target_platform="fastapi",
                auto_test=True,
                auto_fix_tests=True
            )
            
            compiler = PureGeminiCompiler(config)
            
            # 模拟测试结果
            test_results = [
                # 第一次：导入错误
                (False, "ImportError: cannot import name 'User' from 'app.models'"),
                # 第二次：创建文件后通过
                (True, None)
            ]
            
            # 模拟修复
            def mock_fix_import_error(code_dir, error_msg, error_type):
                if "ImportError" in error_msg and "app.models" in error_msg:
                    # 创建缺失的 models.py
                    (code_dir / "app" / "models.py").write_text("""
from pydantic import BaseModel

class User(BaseModel):
    email: str
    name: str
""")
                    return True
                return False
            
            with patch.object(compiler, '_run_tests', side_effect=test_results):
                with patch.object(compiler, '_fix_with_gemini', side_effect=mock_fix_import_error):
                    result = compiler._run_test_feedback_loop(code_dir, max_attempts=5)
            
            assert result["passed"] is True
            assert result["fixed"] is True
            assert result["attempts"] == 2
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_progressive_fix_scenario(self):
        """测试逐步修复多个错误的场景"""
        temp_dir = tempfile.mkdtemp(prefix="progressive_fix_test_")
        code_dir = Path(temp_dir) / "project"
        code_dir.mkdir(parents=True)
        
        try:
            # 创建包含多个错误的项目
            (code_dir / "app").mkdir()
            (code_dir / "tests").mkdir()
            (code_dir / "app" / "__init__.py").touch()
            (code_dir / "tests" / "__init__.py").touch()
            
            config = CompilerConfig(
                output_dir=temp_dir,
                target_platform="fastapi",
                auto_test=True,
                auto_fix_tests=True
            )
            
            compiler = PureGeminiCompiler(config)
            
            # 错误序列：逐步减少
            error_sequence = [
                """
FAILED tests/test_api.py::test_create_user - ImportError: No module named 'app'
FAILED tests/test_models.py::test_user_validation - AttributeError: 'User' object has no attribute 'validate'
FAILED tests/test_services.py::test_user_service - TypeError: create_user() takes 1 positional argument but 2 were given
""",
                """
FAILED tests/test_models.py::test_user_validation - AttributeError: 'User' object has no attribute 'validate'
FAILED tests/test_services.py::test_user_service - TypeError: create_user() takes 1 positional argument but 2 were given
""",
                """
FAILED tests/test_services.py::test_user_service - TypeError: create_user() takes 1 positional argument but 2 were given
""",
                None  # 全部修复
            ]
            
            def mock_run_tests(_):
                error = error_sequence.pop(0)
                return error is None, error
            
            # 记录修复历史
            fix_calls = []
            
            def mock_fix(code_dir, error_msg, error_type):
                fix_calls.append(error_msg[:50])  # 记录错误信息前50个字符
                return True
            
            with patch.object(compiler, '_run_tests', side_effect=mock_run_tests):
                with patch.object(compiler, '_fix_with_gemini', side_effect=mock_fix):
                    result = compiler._run_test_feedback_loop(code_dir, max_attempts=5)
            
            assert result["passed"] is True
            assert result["fixed"] is True
            assert result["attempts"] == 4
            assert len(result["errors"]) == 3
            assert len(result["fix_history"]) == 3
            assert len(fix_calls) == 3
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_max_attempts_scenario(self):
        """测试达到最大尝试次数的场景"""
        config = CompilerConfig(
            output_dir=Path("/tmp"),
            target_platform="fastapi",
            auto_test=True,
            auto_fix_tests=True
        )
        
        compiler = PureGeminiCompiler(config)
        
        # 始终返回相同的错误
        persistent_error = "AssertionError: This error cannot be fixed automatically"
        
        with patch.object(compiler, '_run_tests', return_value=(False, persistent_error)):
            with patch.object(compiler, '_fix_with_gemini', return_value=True):
                result = compiler._run_test_feedback_loop(Path("/tmp/test"), max_attempts=3)
        
        assert result["passed"] is False
        assert result["attempts"] == 3
        assert result["max_attempts_reached"] is True
        assert "需要人类介入" in result["final_error"]
        assert len(result["errors"]) == 3
        assert len(result["fix_history"]) == 2  # 最后一次不修复


if __name__ == "__main__":
    pytest.main([__file__, "-v"])