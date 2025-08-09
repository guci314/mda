#!/usr/bin/env python3
"""
图书借阅系统项目检查脚本
"""
import os
import sys
import importlib.util
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if file_path.exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (缺失)")
        return False


def check_python_file(file_path, description):
    """检查Python文件语法"""
    if not file_path.exists():
        print(f"❌ {description}: {file_path} (缺失)")
        return False
    
    try:
        spec = importlib.util.spec_from_file_location("module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {description}: {file_path}")
        return True
    except Exception as e:
        print(f"❌ {description}: {file_path} (语法错误: {e})")
        return False


def check_project_structure():
    """检查项目结构"""
    print("📁 检查项目结构...")
    
    required_files = [
        (project_root / "main.py", "主应用文件"),
        (project_root / "requirements.txt", "依赖文件"),
        (project_root / "README.md", "说明文档"),
        (project_root / "run.py", "启动脚本"),
        (project_root / "test.py", "测试脚本"),
    ]
    
    required_dirs = [
        (project_root / "app", "应用目录"),
        (project_root / "tests", "测试目录"),
    ]
    
    app_files = [
        (project_root / "app" / "__init__.py", "应用包初始化"),
        (project_root / "app" / "database.py", "数据库配置"),
        (project_root / "app" / "dependencies.py", "依赖注入"),
        (project_root / "app" / "models" / "database.py", "数据库模型"),
        (project_root / "app" / "models" / "pydantic.py", "Pydantic模型"),
        (project_root / "app" / "models" / "enums.py", "枚举定义"),
        (project_root / "app" / "routers" / "books.py", "图书路由"),
        (project_root / "app" / "routers" / "readers.py", "读者路由"),
        (project_root / "app" / "routers" / "borrows.py", "借阅路由"),
        (project_root / "app" / "routers" / "reservations.py", "预约路由"),
        (project_root / "app" / "services" / "book_service.py", "图书服务"),
        (project_root / "app" / "services" / "reader_service.py", "读者服务"),
        (project_root / "app" / "services" / "borrow_service.py", "借阅服务"),
        (project_root / "app" / "services" / "reservation_service.py", "预约服务"),
        (project_root / "app" / "repositories" / "book_repository.py", "图书仓储"),
        (project_root / "app" / "repositories" / "reader_repository.py", "读者仓储"),
        (project_root / "app" / "repositories" / "borrow_repository.py", "借阅仓储"),
        (project_root / "app" / "repositories" / "reservation_repository.py", "预约仓储"),
    ]
    
    test_files = [
        (project_root / "tests" / "conftest.py", "测试配置"),
        (project_root / "tests" / "test_main.py", "主应用测试"),
        (project_root / "tests" / "test_books.py", "图书测试"),
        (project_root / "tests" / "test_readers.py", "读者测试"),
        (project_root / "tests" / "test_borrows.py", "借阅测试"),
        (project_root / "tests" / "test_reservations.py", "预约测试"),
    ]
    
    all_passed = True
    
    # 检查基本文件和目录
    for file_path, description in required_files + required_dirs:
        if not check_file_exists(file_path, description):
            all_passed = False
    
    # 检查应用文件
    print("\n📦 检查应用文件...")
    for file_path, description in app_files:
        if not check_file_exists(file_path, description):
            all_passed = False
    
    # 检查测试文件
    print("\n🧪 检查测试文件...")
    for file_path, description in test_files:
        if not check_file_exists(file_path, description):
            all_passed = False
    
    return all_passed


def check_python_syntax():
    """检查Python文件语法"""
    print("\n🐍 检查Python语法...")
    
    python_files = [
        (project_root / "main.py", "主应用"),
        (project_root / "run.py", "启动脚本"),
        (project_root / "app" / "database.py", "数据库配置"),
        (project_root / "app" / "dependencies.py", "依赖注入"),
    ]
    
    all_passed = True
    for file_path, description in python_files:
        if not check_python_file(file_path, description):
            all_passed = False
    
    return all_passed


def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'pytest',
        'httpx',
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安装)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 请安装缺失的包: pip install {' '.join(missing_packages)}")
        return False
    
    return True


def main():
    """主函数"""
    print("🔍 图书借阅系统项目检查")
    print("=" * 50)
    
    structure_ok = check_project_structure()
    syntax_ok = check_python_syntax()
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 50)
    
    if structure_ok and syntax_ok and deps_ok:
        print("✅ 项目检查通过，可以运行！")
        print("\n🚀 启动命令:")
        print("  python run.py")
        print("\n🧪 测试命令:")
        print("  python test.py")
        return True
    else:
        print("❌ 项目检查失败，请修复上述问题")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)