#!/usr/bin/env python3
"""PIM编译器的简单测试"""
import os
import sys
from pathlib import Path
import shutil
import pytest
import logging

# 添加编译器到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compiler import PureGeminiCompiler, CompilerConfig


@pytest.fixture
def output_dir():
    """创建并返回测试输出目录"""
    output_path = Path("test_simple_output")
    # 清理已存在的输出目录
    if output_path.exists():
        shutil.rmtree(output_path)
    yield output_path
    # 测试后清理（可选）
    # if output_path.exists():
    #     shutil.rmtree(output_path)


@pytest.fixture
def compiler_config(output_dir):
    """创建编译器配置"""
    return CompilerConfig(
        output_dir=output_dir,
        target_platform="fastapi",
        enable_cache=False,
        verbose=True
    )


@pytest.fixture
def pim_file():
    """获取测试用的PIM文件路径"""
    file_path = Path(__file__).parent.parent.parent / "hello_world_pim.md"
    if not file_path.exists():
        pytest.skip(f"测试文件不存在: {file_path}")
    return file_path


@pytest.fixture
def compiler(compiler_config):
    """创建编译器实例"""
    return PureGeminiCompiler(compiler_config)


class TestSimpleCompilation:
    """简单编译测试"""
    
    def test_compiler_initialization(self, compiler, compiler_config):
        """测试编译器初始化"""
        assert compiler is not None
        assert compiler.config == compiler_config
    
    def test_pim_file_exists(self, pim_file):
        """测试PIM文件是否存在"""
        assert pim_file.exists()
        assert pim_file.suffix == ".md"
    
    def test_compile_hello_world(self, compiler, pim_file, output_dir, caplog):
        """测试编译Hello World PIM文件"""
        # 设置日志级别以捕获调试信息
        with caplog.at_level(logging.DEBUG):
            # 执行编译
            result = compiler.compile(pim_file)
            
            # 验证编译结果
            assert result is not None
            assert result.success, f"编译失败: {result.error}"
            
            # 验证输出目录被创建
            assert output_dir.exists()
            
            # 验证生成了文件
            generated_files = list(output_dir.rglob("*"))
            assert len(generated_files) > 0, "没有生成任何文件"
            
            # 打印生成的文件列表（用于调试）
            print("\n生成的文件:")
            for f in generated_files:
                if f.is_file():
                    print(f"  {f.relative_to(output_dir)}")
    
    def test_compile_with_error_handling(self, compiler):
        """测试编译不存在的文件时的错误处理"""
        non_existent_file = Path("non_existent_file.md")
        result = compiler.compile(non_existent_file)
        
        assert not result.success
        assert result.error is not None
        assert "not found" in result.error.lower() or "不存在" in result.error
    
    def test_compile_user_management_with_tests(self, compiler, output_dir, caplog):
        """测试编译包含测试定义的用户管理PIM文件"""
        # 获取测试文件路径
        pim_file = Path(__file__).parent.parent / "examples" / "user_management_with_tests.md"
        
        # 确保文件存在
        assert pim_file.exists(), f"测试文件不存在: {pim_file}"
        
        # 设置日志级别以捕获调试信息
        with caplog.at_level(logging.DEBUG):
            # 执行编译
            result = compiler.compile(pim_file)
            
            # 验证编译结果
            assert result is not None
            assert result.success, f"编译失败: {result.error}"
            
            # 验证输出目录被创建
            assert output_dir.exists()
            
            # 验证生成了文件
            generated_files = list(output_dir.rglob("*"))
            assert len(generated_files) > 0, "没有生成任何文件"
            
            # 打印生成的文件列表（用于调试）
            print("\n生成的文件:")
            for f in generated_files:
                if f.is_file():
                    print(f"  {f.relative_to(output_dir)}")
            
            # 检查是否生成了测试相关文件
            test_files = [f for f in generated_files if "test" in str(f).lower()]
            if test_files:
                print("\n测试相关文件:")
                for f in test_files:
                    if f.is_file():
                        print(f"  {f.relative_to(output_dir)}")
    


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])