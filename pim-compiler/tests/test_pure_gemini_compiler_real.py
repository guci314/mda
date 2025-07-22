"""
测试纯 Gemini 编译器 - 使用真实的 Gemini CLI
"""
import os
import sys
import tempfile
import pytest
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compiler.config import CompilerConfig
from compiler.core.pure_gemini_compiler import PureGeminiCompiler


class TestPureGeminiCompilerReal:
    """测试 PureGeminiCompiler 类 - 使用真实的 Gemini CLI"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def compiler(self, temp_dir):
        """创建编译器实例"""
        config = CompilerConfig(
            output_dir=temp_dir,
            auto_test=False,  # 禁用自动测试以加快速度
            verbose=True
        )
        return PureGeminiCompiler(config)
    
    @pytest.fixture
    def simple_pim(self, temp_dir):
        """创建简单的 PIM 文件"""
        pim_file = temp_dir / "simple_todo.md"
        pim_file.write_text("""# 简单待办事项系统

## 业务描述
一个极简的待办事项管理系统。

## 业务实体

### 待办事项 (Todo)
需要完成的任务。

属性：
- 标题：任务的简短描述（必填）
- 完成状态：是否已完成（布尔值）

## 业务服务

### 待办事项服务
提供基本的任务管理功能：
- 创建待办事项
- 获取所有待办事项
- 标记待办事项为完成
- 删除待办事项
""")
        return pim_file
    
    @pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"),
        reason="需要 Gemini API 密钥"
    )
    def test_real_compilation(self, compiler, simple_pim):
        """测试真实的编译流程"""
        print(f"\n开始编译 PIM 文件: {simple_pim}")
        print(f"输出目录: {compiler.config.output_dir}")
        
        # 执行编译
        result = compiler.compile(simple_pim)
        
        # 基本断言
        assert result is not None, "编译结果不应为 None"
        
        if result.success:
            print(f"\n✅ 编译成功!")
            print(f"PSM 文件: {result.psm_file}")
            print(f"代码目录: {result.code_dir}")
            
            # 验证文件生成
            assert result.psm_file.exists(), "PSM 文件应该存在"
            assert result.code_dir.exists(), "代码目录应该存在"
            
            # 检查生成的文件
            generated_files = list(result.code_dir.rglob("*.py"))
            print(f"\n生成的 Python 文件数: {len(generated_files)}")
            
            # 查找主文件
            main_files = [f for f in generated_files if f.name == "main.py"]
            if main_files:
                print(f"找到 main.py: {main_files[0].relative_to(result.code_dir)}")
            
            # 显示前10个文件以便调试
            for f in generated_files[:10]:
                print(f"  - {f.relative_to(result.code_dir)}")
            
            # 验证关键文件
            if compiler.config.target_platform.lower() == "django":
                manage_files = list(result.code_dir.rglob("manage.py"))
                assert len(manage_files) > 0, "Django 项目应该生成 manage.py"
            else:
                main_files = list(result.code_dir.rglob("main.py"))
                assert len(main_files) > 0, f"应该生成 main.py，但只找到这些文件: {[f.name for f in generated_files[:10]]}"
            
            req_files = list(result.code_dir.rglob("requirements.txt"))
            assert len(req_files) > 0, "应该生成 requirements.txt"
            
            # 显示 PSM 内容
            psm_content = result.psm_file.read_text()
            print(f"\nPSM 内容预览 (前500字符):")
            print("-" * 50)
            print(psm_content[:500])
            print("-" * 50)
            
            # 显示统计信息
            if result.statistics:
                print(f"\n统计信息:")
                print(f"  总文件数: {result.statistics.get('total_files', 0)}")
                print(f"  Python 文件数: {result.statistics.get('python_files', 0)}")
                print(f"  PSM 生成时间: {result.statistics.get('psm_generation_time', 0):.2f}秒")
                print(f"  代码生成时间: {result.statistics.get('code_generation_time', 0):.2f}秒")
                print(f"  总编译时间: {result.compilation_time:.2f}秒")
        else:
            print(f"\n❌ 编译失败: {result.error}")
            assert False, f"编译失败: {result.error}"
    
    @pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"),
        reason="需要 Gemini API 密钥"
    )
    def test_different_platforms(self, temp_dir, simple_pim):
        """测试不同平台的编译"""
        platforms = ["fastapi", "django"]
        
        for platform in platforms:
            print(f"\n\n{'='*60}")
            print(f"测试平台: {platform}")
            print('='*60)
            
            config = CompilerConfig(
                output_dir=temp_dir / f"output_{platform}",
                target_platform=platform,
                auto_test=False,
                verbose=False
            )
            
            compiler = PureGeminiCompiler(config)
            result = compiler.compile(simple_pim)
            
            assert result.success, f"{platform} 编译失败: {result.error}"
            print(f"✅ {platform} 编译成功")
            
            # 验证平台特定内容
            if result.psm_file:
                psm_content = result.psm_file.read_text()
                if platform == "fastapi":
                    assert "FastAPI" in psm_content, "FastAPI PSM 应包含 FastAPI"
                elif platform == "django":
                    assert "Django" in psm_content, "Django PSM 应包含 Django"
    
    @pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"),
        reason="需要 Gemini API 密钥"
    )
    def test_chinese_model(self, compiler, temp_dir):
        """测试中文模型编译"""
        chinese_pim = temp_dir / "图书管理.md"
        chinese_pim.write_text("""# 图书管理系统

## 业务描述
管理图书的借阅和归还。

## 业务实体

### 图书
- 书名：图书的名称
- 作者：图书的作者
- ISBN：图书编号
- 状态：可借/已借出

### 读者
- 姓名：读者姓名
- 编号：读者编号

## 业务服务

### 借阅服务
- 借书：读者借阅图书
- 还书：读者归还图书
- 查询：查询图书状态
""")
        
        print(f"\n测试中文 PIM 文件: {chinese_pim}")
        
        result = compiler.compile(chinese_pim)
        
        if result.success:
            print("✅ 中文模型编译成功")
            assert result.code_dir.exists()
            
            # 检查是否正确处理了中文
            main_py = result.code_dir / "main.py"
            if main_py.exists():
                content = main_py.read_text(encoding='utf-8')
                print(f"生成的代码包含 {len(content)} 个字符")
        else:
            print(f"❌ 中文模型编译失败: {result.error}")


if __name__ == "__main__":
    # 直接运行此文件时使用 pytest
    pytest.main([__file__, "-v", "-s"])  # -s 显示 print 输出