"""测试 PIM 和 PSM 文件放在项目根目录"""

import pytest
from pathlib import Path

from src.compiler.core.pure_gemini_compiler import PureGeminiCompiler
from src.compiler.config import CompilerConfig


class TestPimPsmInRoot:
    """测试 PIM 和 PSM 文件在项目根目录的效果"""
    
    def test_pim_psm_in_project_root(self, tmp_path):
        """测试 PIM 和 PSM 文件是否正确放置在项目根目录"""
        # 创建测试 PIM 文件
        pim_file = tmp_path / "simple_service_pim.md"
        pim_file.write_text("""# 平台无关模型 (PIM): 简单服务

## 领域信息
- **领域名称**: simple-service
- **版本**: 1.0.0
- **描述**: 测试 PIM/PSM 在项目根目录

## 业务实体
### Item
- **描述**: 项目
- **属性**:
  - id: 唯一标识符
  - name: 名称（必填）
  - description: 描述

## 业务服务
### ItemService
- **描述**: 项目服务
- **方法**:
  - getItem(id): 获取项目
  - listItems(): 列出所有项目

## 业务规则
- name_required: 名称不能为空
""")
        
        # 配置
        config = CompilerConfig(
            output_dir=tmp_path / "output",
            enable_lint=False,
            auto_test=False  # 暂时不运行测试
        )
        
        # 创建编译器并编译
        compiler = PureGeminiCompiler(config)
        result = compiler.compile(pim_file)
        
        # 验证编译成功
        assert result.success, f"编译失败: {result.error}"
        assert result.code_dir is not None
        
        # 检查项目根目录结构
        project_root = result.code_dir
        print(f"\n项目根目录: {project_root}")
        
        # 验证 PIM 和 PSM 文件在项目根目录
        pim_in_root = project_root / pim_file.name
        psm_in_root = project_root / f"{pim_file.stem}_psm.md"
        
        assert pim_in_root.exists(), f"PIM 文件未在项目根目录: {pim_in_root}"
        assert psm_in_root.exists(), f"PSM 文件未在项目根目录: {psm_in_root}"
        
        # 打印项目根目录的文件
        print("\n项目根目录文件:")
        for file in sorted(project_root.iterdir()):
            if file.is_file():
                print(f"  - {file.name}")
        
        # 检查生成的代码文件
        expected_files = ["main.py", "requirements.txt"]
        for file_name in expected_files:
            file_path = project_root / file_name
            if not file_path.exists():
                print(f"\n警告: 缺少文件 {file_name}")
        
        print(f"\n✅ PIM 和 PSM 文件成功放置在项目根目录！")