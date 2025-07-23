"""测试改进的代码生成提示词"""

import pytest
from pathlib import Path
import shutil

from src.compiler.core.pure_gemini_compiler import PureGeminiCompiler
from src.compiler.config import CompilerConfig


class TestImprovedPrompt:
    """测试改进的提示词是否生成更完整的代码"""
    
    def test_generate_complete_fastapi_service(self, tmp_path):
        """测试生成完整的 FastAPI 微服务"""
        # 创建测试 PIM 文件
        pim_file = tmp_path / "test_service_pim.md"
        pim_file.write_text("""# 平台无关模型 (PIM): 测试服务

## 领域信息
- **领域名称**: test-service
- **版本**: 1.0.0
- **描述**: 用于测试完整代码生成的服务

## 业务实体
### TestEntity
- **描述**: 测试实体
- **属性**:
  - id: 唯一标识符
  - name: 名称（必填）
  - description: 描述（可选）
  - created_at: 创建时间
  - updated_at: 更新时间

## 业务服务
### TestService
- **描述**: 测试服务
- **方法**:
  - create(data: TestEntity): 创建实体
  - get(id): 获取实体
  - list(): 列出所有实体
  - update(id, data: TestEntity): 更新实体
  - delete(id): 删除实体

## 业务规则
- name_required: 名称不能为空
- unique_name: 名称必须唯一
""")
        
        # 配置
        config = CompilerConfig(
            output_dir=tmp_path / "output",
            enable_lint=False,
            auto_test=False  # 先不运行测试，只检查生成的文件
        )
        
        # 创建编译器并编译
        compiler = PureGeminiCompiler(config)
        result = compiler.compile(pim_file)
        
        # 验证编译成功
        assert result.success, f"编译失败: {result.error}"
        assert result.code_dir is not None
        
        # 检查必需的文件是否都被生成
        required_files = [
            "main.py",
            "requirements.txt",
            "README.md",
            ".env.example",
            ".gitignore",
            "app/__init__.py",
            "app/main.py",
            "app/core/__init__.py",
            "app/core/config.py",
            "app/api/__init__.py",
            "app/api/v1/__init__.py",
            "app/api/v1/api.py",
            "app/api/v1/endpoints/__init__.py",
            "app/models/__init__.py",
            "app/schemas/__init__.py",
            "app/services/__init__.py",
            "tests/__init__.py",
            "tests/conftest.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = result.code_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        # 打印调试信息
        if missing_files:
            print(f"\n缺少的文件: {missing_files}")
            print(f"\n实际生成的文件:")
            for f in sorted(result.code_dir.rglob("*")):
                if f.is_file() and "__pycache__" not in str(f):
                    print(f"  {f.relative_to(result.code_dir)}")
        
        # 验证所有必需文件都被生成
        assert len(missing_files) == 0, f"缺少必需的文件: {missing_files}"
        
        # 检查关键文件的内容
        main_py = result.code_dir / "main.py"
        assert main_py.exists()
        main_content = main_py.read_text()
        assert "uvicorn" in main_content
        assert "app.main:app" in main_content
        
        app_main_py = result.code_dir / "app" / "main.py"
        assert app_main_py.exists()
        app_main_content = app_main_py.read_text()
        assert "FastAPI" in app_main_content
        assert "CORSMiddleware" in app_main_content
        assert "api_router" in app_main_content
        
        # 检查是否生成了实体相关的文件
        assert (result.code_dir / "app" / "models").exists()
        assert (result.code_dir / "app" / "schemas").exists()
        assert (result.code_dir / "app" / "api" / "v1" / "endpoints").exists()
        
        print(f"\n✅ 成功生成完整的 FastAPI 微服务结构！")
        print(f"生成的文件总数: {len(list(result.code_dir.rglob('*.py')))}")