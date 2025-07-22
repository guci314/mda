"""
集成测试 - 测试完整的编译流程
注意：这些测试需要有效的 Gemini API 密钥
"""
import os
import tempfile
import pytest
from pathlib import Path
from compiler.config import CompilerConfig
from compiler.compiler_factory import CompilerFactory


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"),
    reason="需要 Gemini API 密钥进行集成测试"
)
class TestIntegration:
    """集成测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def simple_pim(self, temp_dir):
        """创建简单的 PIM 文件"""
        pim_file = temp_dir / "todo.md"
        pim_file.write_text("""# 待办事项管理系统

## 业务描述
一个简单的任务管理系统，用于跟踪待办事项。

## 业务实体

### 待办事项 (Todo)
用户需要完成的任务。

属性：
- 标题：任务的简短描述（必填）
- 描述：详细说明（可选）
- 状态：待办/完成
- 创建时间：任务创建的时间
- 完成时间：任务完成的时间

## 业务服务

### 待办事项服务
提供待办事项的管理功能：
- 创建待办事项：添加新的任务
- 更新待办事项：修改任务信息
- 完成待办事项：标记任务为完成
- 删除待办事项：删除不需要的任务
- 查询待办事项：获取任务列表，支持按状态筛选

## 业务规则
1. 任务标题不能为空
2. 已完成的任务不能再次标记为完成
3. 删除任务需要确认
""")
        return pim_file
    
    @pytest.mark.slow
    def test_compile_simple_model(self, simple_pim, temp_dir):
        """测试编译简单模型"""
        # 创建编译器配置
        config = CompilerConfig(
            output_dir=temp_dir / "output",
            target_platform="fastapi",
            auto_test=False,  # 跳过自动测试以加快速度
            verbose=True
        )
        
        # 创建编译器
        compiler = CompilerFactory.create_compiler(config)
        
        # 执行编译
        result = compiler.compile(simple_pim)
        
        # 验证结果
        assert result.success is True, f"编译失败: {result.error}"
        assert result.psm_file is not None
        assert result.psm_file.exists()
        assert result.code_dir is not None
        assert result.code_dir.exists()
        
        # 验证生成的文件
        assert (result.code_dir / "main.py").exists()
        assert (result.code_dir / "requirements.txt").exists()
        
        # 验证 PSM 内容
        psm_content = result.psm_file.read_text()
        assert "FastAPI" in psm_content
        assert "SQLAlchemy" in psm_content
        assert "Todo" in psm_content
    
    @pytest.mark.slow
    def test_compile_with_different_platforms(self, simple_pim, temp_dir):
        """测试不同平台的编译"""
        platforms = ["fastapi", "django"]
        
        for platform in platforms:
            output_dir = temp_dir / f"output_{platform}"
            config = CompilerConfig(
                output_dir=output_dir,
                target_platform=platform,
                auto_test=False,
                verbose=False
            )
            
            compiler = CompilerFactory.create_compiler(config)
            result = compiler.compile(simple_pim)
            
            assert result.success is True, f"{platform} 编译失败: {result.error}"
            
            # 验证平台特定内容
            psm_content = result.psm_file.read_text()
            if platform == "fastapi":
                assert "FastAPI" in psm_content
            elif platform == "django":
                assert "Django" in psm_content
    
    def test_compile_invalid_pim(self, temp_dir):
        """测试编译无效的 PIM 文件"""
        # 创建空文件
        invalid_pim = temp_dir / "empty.md"
        invalid_pim.write_text("")
        
        config = CompilerConfig(
            output_dir=temp_dir / "output",
            auto_test=False
        )
        
        compiler = CompilerFactory.create_compiler(config)
        result = compiler.compile(invalid_pim)
        
        # 空文件也可能生成某些内容，主要测试不崩溃
        assert result is not None
    
    @pytest.mark.slow
    def test_compile_chinese_model(self, temp_dir):
        """测试编译中文模型"""
        chinese_pim = temp_dir / "图书管理.md"
        chinese_pim.write_text("""# 图书管理系统

## 业务描述
管理图书馆的图书借阅业务。

## 业务实体

### 图书
图书馆中的书籍。

属性：
- 书名：图书的名称
- 作者：图书的作者
- ISBN：国际标准书号
- 状态：可借/已借出

### 读者
借阅图书的人员。

属性：
- 姓名：读者的姓名
- 借书证号：唯一标识
- 联系电话：联系方式

## 业务服务

### 借阅服务
- 借书：读者借阅图书
- 还书：读者归还图书
- 查询：查询图书状态
""")
        
        config = CompilerConfig(
            output_dir=temp_dir / "output",
            auto_test=False,
            verbose=True
        )
        
        compiler = CompilerFactory.create_compiler(config)
        result = compiler.compile(chinese_pim)
        
        assert result.success is True, f"编译失败: {result.error}"
        assert result.code_dir.exists()
        
        # 验证中文内容被正确处理
        main_py = result.code_dir / "main.py"
        if main_py.exists():
            content = main_py.read_text(encoding='utf-8')
            # 应该包含 API 相关代码
            assert "api" in content.lower() or "route" in content.lower()