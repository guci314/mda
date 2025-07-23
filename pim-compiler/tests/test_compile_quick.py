"""快速编译测试（禁用测试运行）"""

import pytest
from pathlib import Path

from src.compiler.core.pure_gemini_compiler import PureGeminiCompiler
from src.compiler.config import CompilerConfig


class TestQuickCompile:
    """快速编译测试"""
    
    def test_compile_without_tests(self, tmp_path):
        """测试禁用测试运行的编译"""
        # 使用已存在的 PIM 文件
        pim_file = Path("/home/guci/aiProjects/mda/hello_world_pim.md")
        if not pim_file.exists():
            # 创建一个简单的测试 PIM
            pim_file = tmp_path / "test_pim.md"
            pim_file.write_text("""# 平台无关模型 (PIM): Hello World Service

## 领域信息
- **领域名称**: hello-world
- **版本**: 1.0.0
- **描述**: 一个简单的 Hello World 服务

## 业务实体
无

## 业务服务
### HelloService
- **描述**: 提供问候服务
- **方法**:
  - sayHello(): 返回问候消息
    - 业务规则: greeting_rule

## 业务规则
- **greeting_rule**: 始终返回 "Hello World!"
""")
        
        # 配置：禁用测试运行
        config = CompilerConfig(
            output_dir=tmp_path / "output",
            enable_lint=False,
            auto_test=False  # 禁用测试运行
        )
        
        # 创建编译器并编译
        compiler = PureGeminiCompiler(config)
        result = compiler.compile(pim_file)
        
        # 验证编译成功
        assert result.success, f"编译失败: {result.error}"
        assert result.psm_file is not None
        assert result.code_dir is not None
        assert result.test_results is None  # 应该没有测试结果
        
        # 验证生成的文件
        assert result.psm_file.exists()
        assert result.code_dir.exists()
        
        # 查找项目目录
        project_dir = compiler._find_project_directory(result.code_dir)
        if project_dir:
            print(f"找到项目目录: {project_dir}")
            # 列出项目结构
            for item in project_dir.rglob("*"):
                if item.is_file():
                    print(f"  {item.relative_to(project_dir)}")