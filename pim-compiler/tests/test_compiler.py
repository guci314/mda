"""Test PIM Compiler with real DeepSeek and Gemini CLI"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 加载项目根目录的 .env 文件
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file}")

from compiler.core.compiler_config import CompilerConfig
from compiler.transformers.deepseek_compiler import DeepSeekCompiler


def check_prerequisites():
    """检查测试先决条件"""
    print("检查测试环境...")
    
    # 检查 DeepSeek API key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 错误: 未设置 DEEPSEEK_API_KEY 环境变量")
        print("   请运行: export DEEPSEEK_API_KEY=your-api-key")
        return False
    
    # 检查 Gemini API key
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  警告: 未设置 GEMINI_API_KEY，将跳过自动修复功能")
        print("   建议运行: export GEMINI_API_KEY=your-api-key")
    
    # 检查必要的工具
    tools = {
        "black": "Python 代码格式化",
        "flake8": "Python 代码检查",
        "pytest": "Python 测试运行"
    }
    
    missing_tools = []
    for tool, description in tools.items():
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            print(f"✓ {tool} 已安装 ({description})")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(f"{tool} - {description}")
    
    if missing_tools:
        print("\n⚠️  警告: 以下工具未安装，部分功能可能无法使用:")
        for tool in missing_tools:
            print(f"   - {tool}")
        print("   建议安装: pip install black flake8 pytest")
    
    # 检查 Gemini CLI（可选）
    try:
        subprocess.run(["gemini", "--version"], capture_output=True, check=True)
        print("✓ Gemini CLI 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  警告: Gemini CLI 未安装，自动修复功能将不可用")
        print("   请参考 Gemini 文档安装 CLI 工具")
    
    print()
    return True


def test_compile_user_crud():
    """测试编译用户管理 CRUD 系统"""
    print("=" * 80)
    print("测试：编译用户管理 CRUD 系统")
    print("=" * 80)
    
    # 使用临时目录作为输出
    with tempfile.TemporaryDirectory() as tmpdir:
        # 配置编译器
        config = CompilerConfig(
            output_dir=Path(tmpdir),
            enable_cache=False,  # 测试时禁用缓存
            verbose=True,
            generate_code=True,  # 生成代码
            enable_lint=True,    # 启用 lint
            enable_unit_tests=True,  # 生成单元测试
            run_tests=True,      # 运行测试
            target_platform="fastapi"  # 使用 FastAPI 平台
        )
        
        # 创建编译器
        print("\n1. 初始化编译器...")
        try:
            compiler = DeepSeekCompiler(config)
            print("✓ 编译器创建成功")
        except Exception as e:
            print(f"✗ 编译器创建失败: {e}")
            return False
        
        # 编译 PIM 文件
        pim_file = Path(__file__).parent.parent / "examples" / "simple_user_crud.md"
        if not pim_file.exists():
            print(f"✗ PIM 文件不存在: {pim_file}")
            return False
        
        print(f"\n2. 编译 PIM 文件: {pim_file.name}")
        print("   目标平台: FastAPI")
        print("   输出目录:", tmpdir)
        
        print("\n开始编译...")
        start_time = datetime.now()
        
        # 添加进度监控
        import threading
        stop_progress = threading.Event()
        
        def show_progress():
            """显示进度"""
            elapsed = 0
            while not stop_progress.is_set():
                elapsed += 1
                print(f"\r   编译中... ({elapsed}秒)", end="", flush=True)
                stop_progress.wait(1)
        
        progress_thread = threading.Thread(target=show_progress)
        progress_thread.start()
        
        try:
            result = compiler.compile(pim_file)
        finally:
            stop_progress.set()
            progress_thread.join()
            print()  # 换行
        
        compile_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n3. 编译结果:")
        print(f"   耗时: {compile_time:.2f} 秒")
        
        if result.success:
            print("✓ 编译成功!")
            
            # 显示 PSM 文件
            if result.psm_file and result.psm_file.exists():
                print(f"\n4. 生成的 PSM 文件: {result.psm_file}")
                with open(result.psm_file, 'r', encoding='utf-8') as f:
                    psm_content = f.read()
                print("\nPSM 内容预览:")
                print("-" * 80)
                print(psm_content[:1000] + "..." if len(psm_content) > 1000 else psm_content)
                print("-" * 80)
            
            # 显示生成的代码文件
            if result.metadata.get("code_files"):
                print(f"\n5. 生成的代码文件:")
                for code_file in result.metadata["code_files"]:
                    print(f"   - {code_file}")
                    
                # 显示一个代码文件的内容
                if result.metadata["code_files"]:
                    first_file = Path(result.metadata["code_files"][0])
                    if first_file.exists():
                        print(f"\n代码文件预览 ({first_file.name}):")
                        print("-" * 80)
                        with open(first_file, 'r', encoding='utf-8') as f:
                            code_content = f.read()
                        print(code_content[:1000] + "..." if len(code_content) > 1000 else code_content)
                        print("-" * 80)
            
            # 检查测试结果
            test_files = [f for f in result.metadata.get("code_files", []) if 'test_' in Path(f).name]
            if test_files:
                print(f"\n6. 生成的测试文件:")
                for test_file in test_files:
                    print(f"   - {test_file}")
            
            return True
        else:
            print("✗ 编译失败!")
            print("\n错误信息:")
            for error in result.errors:
                print(f"  - {error}")
            
            if result.warnings:
                print("\n警告信息:")
                for warning in result.warnings:
                    print(f"  - {warning}")
            
            return False


def test_different_platforms():
    """测试不同平台的编译"""
    platforms = ["fastapi", "django", "flask"]
    
    print("\n" + "=" * 80)
    print("测试：多平台编译")
    print("=" * 80)
    
    for platform in platforms:
        print(f"\n测试平台: {platform}")
        print("-" * 40)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = CompilerConfig(
                output_dir=Path(tmpdir),
                enable_cache=False,
                verbose=False,  # 减少输出
                generate_code=False,  # 只生成 PSM
                target_platform=platform
            )
            
            try:
                compiler = DeepSeekCompiler(config)
                pim_file = Path(__file__).parent.parent / "examples" / "simple_user_crud.md"
                
                result = compiler.compile(pim_file)
                
                if result.success:
                    print(f"✓ {platform} 平台编译成功")
                    if result.psm_file:
                        print(f"  PSM 文件: {result.psm_file.name}")
                else:
                    print(f"✗ {platform} 平台编译失败")
                    
            except Exception as e:
                print(f"✗ {platform} 平台测试出错: {e}")


def main():
    """主测试函数"""
    print("PIM 编译器集成测试")
    print("=" * 80)
    print("使用真实的 DeepSeek API 和 Gemini CLI\n")
    
    # 检查先决条件
    if not check_prerequisites():
        print("\n测试中止：缺少必要的环境配置")
        return 1
    
    # 运行测试
    test_results = []
    
    # 测试1：完整的编译流程
    print("\n" + "=" * 80)
    success = test_compile_user_crud()
    test_results.append(("用户管理 CRUD 编译", success))
    
    # 测试2：多平台编译
    if success:  # 只有第一个测试成功才运行
        test_different_platforms()
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    for test_name, success in test_results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    # 提示
    print("\n提示:")
    print("- 如需查看更详细的输出，请设置 config.debug = True")
    print("- 生成的代码会自动进行 lint 检查和测试")
    print("- 如果安装了 Gemini CLI，错误会自动修复")
    
    return 0 if all(result[1] for result in test_results) else 1


if __name__ == "__main__":
    sys.exit(main())