"""
反馈循环测试的 fixtures 和 mocks
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import List, Tuple, Optional, Dict, Any
import tempfile
import shutil


class MockGeminiCLI:
    """模拟 Gemini CLI 的行为"""
    
    def __init__(self, fix_success_rate: float = 0.8):
        self.fix_success_rate = fix_success_rate
        self.call_count = 0
        self.call_history = []
    
    def execute(self, prompt: str, work_dir: Path, **kwargs) -> bool:
        """模拟执行 Gemini CLI"""
        self.call_count += 1
        self.call_history.append({
            "prompt": prompt[:100],  # 只保存前100个字符
            "work_dir": str(work_dir),
            "kwargs": kwargs
        })
        
        # 根据成功率决定是否成功
        import random
        return random.random() < self.fix_success_rate


class TestErrorGenerator:
    """生成各种类型的测试错误"""
    
    @staticmethod
    def syntax_error() -> str:
        return """
  File "app/models.py", line 45
    def get_user(id: int)
                         ^
SyntaxError: invalid syntax
"""
    
    @staticmethod
    def import_error() -> str:
        return """
ImportError: cannot import name 'BaseModel' from 'pydantic' (/usr/local/lib/python3.9/site-packages/pydantic/__init__.py)
"""
    
    @staticmethod
    def assertion_error() -> str:
        return """
tests/test_user.py::test_create_user FAILED
    def test_create_user():
        user = create_user("test@example.com", "password")
>       assert user.email == "test@example.com"
E       AssertionError: assert 'test@exampl.com' == 'test@example.com'
"""
    
    @staticmethod
    def type_error() -> str:
        return """
TypeError: unsupported operand type(s) for +: 'int' and 'str'
"""
    
    @staticmethod
    def mixed_errors() -> str:
        """生成混合错误信息"""
        return """
==================== FAILURES ====================
_____ test_user_creation _____

    def test_user_creation():
>       user = User(email="invalid-email")
E       ValidationError: 1 validation error for User
E       email
E         value is not a valid email address

tests/test_models.py:15: ValidationError

_____ test_database_connection _____

    def test_database_connection():
>       db = connect_database()
E       ConnectionError: Unable to connect to database

tests/test_db.py:8: ConnectionError

==================== 2 failed, 3 passed in 0.45s ====================
"""


class TestScenarioBuilder:
    """构建不同的测试场景"""
    
    @staticmethod
    def build_gradual_fix_scenario() -> List[Tuple[bool, Optional[str]]]:
        """逐步修复的场景：错误越来越少"""
        return [
            (False, TestErrorGenerator.mixed_errors()),
            (False, TestErrorGenerator.assertion_error()),
            (False, TestErrorGenerator.type_error()),
            (True, None)
        ]
    
    @staticmethod
    def build_persistent_error_scenario() -> List[Tuple[bool, Optional[str]]]:
        """持续错误的场景：某个错误无法修复"""
        error = TestErrorGenerator.import_error()
        return [(False, error) for _ in range(10)]  # 总是相同的错误
    
    @staticmethod
    def build_flaky_test_scenario() -> List[Tuple[bool, Optional[str]]]:
        """不稳定测试场景：随机成功或失败"""
        import random
        results = []
        for i in range(10):
            if random.random() < 0.3:  # 30% 概率成功
                results.append((True, None))
            else:
                results.append((False, TestErrorGenerator.assertion_error()))
        return results


@pytest.fixture
def temp_code_directory():
    """创建临时代码目录"""
    temp_dir = tempfile.mkdtemp(prefix="test_feedback_")
    
    # 创建基本的项目结构
    (Path(temp_dir) / "app").mkdir()
    (Path(temp_dir) / "tests").mkdir()
    
    # 创建一些示例文件
    (Path(temp_dir) / "app" / "__init__.py").touch()
    (Path(temp_dir) / "app" / "models.py").write_text("""
from pydantic import BaseModel

class User(BaseModel):
    email: str
    name: str
""")
    
    (Path(temp_dir) / "tests" / "__init__.py").touch()
    (Path(temp_dir) / "tests" / "test_models.py").write_text("""
import pytest
from app.models import User

def test_user_creation():
    user = User(email="test@example.com", name="Test User")
    assert user.email == "test@example.com"
""")
    
    yield Path(temp_dir)
    
    # 清理
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_subprocess_run():
    """模拟 subprocess.run"""
    def _mock_run(cmd, **kwargs):
        result = Mock()
        
        # 根据命令决定返回值
        if "pytest" in cmd:
            # 模拟 pytest 输出
            result.returncode = 1
            result.stdout = TestErrorGenerator.mixed_errors()
            result.stderr = ""
        elif "flake8" in cmd:
            # 模拟 flake8 输出
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
        else:
            result.returncode = 0
            result.stdout = "Command executed successfully"
            result.stderr = ""
        
        return result
    
    return _mock_run


@pytest.fixture
def feedback_loop_state_machine():
    """创建一个状态机来模拟反馈循环"""
    class FeedbackLoopStateMachine:
        def __init__(self):
            self.states = ["initial_errors", "partial_fix", "almost_fixed", "fixed"]
            self.current_state_index = 0
            self.transition_count = 0
        
        def get_test_result(self) -> Tuple[bool, Optional[str]]:
            """根据当前状态返回测试结果"""
            state = self.states[self.current_state_index]
            
            if state == "initial_errors":
                return False, TestErrorGenerator.mixed_errors()
            elif state == "partial_fix":
                return False, TestErrorGenerator.assertion_error()
            elif state == "almost_fixed":
                return False, TestErrorGenerator.type_error()
            elif state == "fixed":
                return True, None
            
            return False, "Unknown state"
        
        def apply_fix(self) -> bool:
            """应用修复并转换状态"""
            self.transition_count += 1
            
            # 每次修复有机会前进到下一个状态
            if self.current_state_index < len(self.states) - 1:
                self.current_state_index += 1
                return True
            
            return False
        
        def reset(self):
            """重置状态机"""
            self.current_state_index = 0
            self.transition_count = 0
    
    return FeedbackLoopStateMachine()


class MockCompilationEnvironment:
    """模拟完整的编译环境"""
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.gemini_cli = MockGeminiCLI()
        self.test_scenarios = {}
        self.current_scenario = None
    
    def add_scenario(self, name: str, test_results: List[Tuple[bool, Optional[str]]]):
        """添加测试场景"""
        self.test_scenarios[name] = test_results
    
    def use_scenario(self, name: str):
        """使用特定场景"""
        if name in self.test_scenarios:
            self.current_scenario = iter(self.test_scenarios[name])
    
    def run_tests(self) -> Tuple[bool, Optional[str]]:
        """运行测试（使用当前场景）"""
        if self.current_scenario:
            try:
                return next(self.current_scenario)
            except StopIteration:
                return True, None  # 场景结束，返回成功
        
        # 默认返回失败
        return False, "No scenario configured"


@pytest.fixture
def compilation_environment(temp_code_directory):
    """创建完整的编译环境"""
    env = MockCompilationEnvironment(temp_code_directory)
    
    # 添加预定义场景
    env.add_scenario("gradual_fix", TestScenarioBuilder.build_gradual_fix_scenario())
    env.add_scenario("persistent_error", TestScenarioBuilder.build_persistent_error_scenario())
    env.add_scenario("flaky_tests", TestScenarioBuilder.build_flaky_test_scenario())
    
    return env


# 辅助函数
def create_mock_compiler_with_scenario(scenario: str = "gradual_fix") -> Mock:
    """创建带有特定场景的模拟编译器"""
    compiler = Mock()
    env = MockCompilationEnvironment(Path("/tmp/test"))
    env.use_scenario(scenario)
    
    compiler._run_tests = Mock(side_effect=lambda _: env.run_tests())
    compiler._fix_with_gemini = Mock(return_value=True)
    compiler._categorize_errors = Mock(side_effect=lambda e: ["测试错误"])
    compiler._generate_test_fix_prompt = Mock(return_value="Fix the test errors")
    
    return compiler


def assert_feedback_loop_metrics(result: Dict[str, Any], 
                               expected_attempts: int,
                               expected_success: bool,
                               expected_fixes: int = None):
    """断言反馈循环的指标"""
    assert result["attempts"] == expected_attempts
    assert result["passed"] == expected_success
    
    if expected_fixes is not None:
        assert len(result["fix_history"]) == expected_fixes
    
    if not expected_success and expected_attempts >= 5:
        assert result.get("max_attempts_reached") is True