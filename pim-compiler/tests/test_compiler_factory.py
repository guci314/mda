"""
测试编译器工厂
"""
import sys
import pytest
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compiler.config import CompilerConfig
from compiler.compiler_factory import CompilerFactory
from compiler.core.pure_gemini_compiler import PureGeminiCompiler


class TestCompilerFactory:
    """测试编译器工厂"""
    
    def test_create_default_compiler(self):
        """测试创建默认编译器"""
        config = CompilerConfig()
        compiler = CompilerFactory.create_compiler(config)
        
        assert isinstance(compiler, PureGeminiCompiler)
        assert compiler.config == config
    
    def test_create_compiler_with_config(self):
        """测试使用自定义配置创建编译器"""
        config = CompilerConfig(
            target_platform="django",
            auto_test=False,
            verbose=True
        )
        compiler = CompilerFactory.create_compiler(config)
        
        assert isinstance(compiler, PureGeminiCompiler)
        assert compiler.config.target_platform == "django"
        assert compiler.config.auto_test is False
        assert compiler.config.verbose is True
    
    def test_compiler_type_selection(self):
        """测试编译器类型选择（当前只有一种）"""
        # 未来可能支持多种编译器类型
        config = CompilerConfig()
        compiler = CompilerFactory.create_compiler(config)
        
        # 当前总是返回 PureGeminiCompiler
        assert type(compiler).__name__ == "PureGeminiCompiler"
    
    def test_factory_method_signature(self):
        """测试工厂方法签名"""
        # 确保工厂方法存在且可调用
        assert hasattr(CompilerFactory, 'create_compiler')
        assert callable(CompilerFactory.create_compiler)
        
        # 测试可以不传参数（使用默认配置）
        compiler = CompilerFactory.create_compiler()
        assert isinstance(compiler, PureGeminiCompiler)
        
        # 测试可以传入 None
        compiler = CompilerFactory.create_compiler(None)
        assert isinstance(compiler, PureGeminiCompiler)


if __name__ == "__main__":
    # 直接运行此文件时使用 pytest
    pytest.main([__file__, "-v"])