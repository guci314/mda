"""
测试编译器配置模块
"""
import os
import sys
import tempfile
import pytest
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compiler.config import CompilerConfig


class TestCompilerConfig:
    """测试编译器配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = CompilerConfig()
        assert config.target_platform == "fastapi"
        assert config.output_dir == Path("./output")
        assert config.auto_test is True
        assert config.auto_fix_lint is True
        assert config.auto_fix_tests is True
        assert config.verbose is True  # 默认为 True
    
    def test_custom_config(self):
        """测试自定义配置"""
        custom_output = Path("/tmp/test_output")
        config = CompilerConfig(
            target_platform="django",
            output_dir=custom_output,
            auto_test=False,
            verbose=True
        )
        assert config.target_platform == "django"
        assert config.output_dir == custom_output
        assert config.auto_test is False
        assert config.verbose is True
    
    def test_gemini_model_from_env(self):
        """测试从环境变量读取 Gemini 模型"""
        # 保存原始环境变量
        original_model = os.environ.get("GEMINI_MODEL")
        
        # 设置测试环境变量
        os.environ["GEMINI_MODEL"] = "gemini-2.5-pro"
        config = CompilerConfig()
        assert config.gemini_model == "gemini-2.5-pro"
        
        # 恢复原始环境变量
        if original_model:
            os.environ["GEMINI_MODEL"] = original_model
        else:
            os.environ.pop("GEMINI_MODEL", None)
    
    def test_supported_platforms(self):
        """测试支持的平台"""
        supported = ["fastapi", "django", "flask", "spring", "express"]
        for platform in supported:
            config = CompilerConfig(target_platform=platform)
            assert config.target_platform == platform
    
    def test_invalid_platform_allowed(self):
        """测试无效平台（当前允许任何值）"""
        # 注意：当前实现允许任何平台值，未来可能需要验证
        config = CompilerConfig(target_platform="invalid_platform")
        assert config.target_platform == "invalid_platform"
    
    def test_output_dir_creation(self):
        """测试输出目录处理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output"
            config = CompilerConfig(output_dir=output_path)
            assert config.output_dir == output_path
            # 注意：配置本身不创建目录，这由编译器处理


if __name__ == "__main__":
    # 直接运行此文件时使用 pytest
    pytest.main([__file__, "-v"])