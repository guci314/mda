#!/usr/bin/env python3
"""
项目完整性验证脚本
"""
import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (缺失)")
        return False

def check_directory_exists(dir_path, description):
    """检查目录是否存在"""
    if os.path.isdir(dir_path):
        print(f"✓ {description}: {dir_path}")
        return True
    else:
        print(f"✗ {description}: {dir_path} (缺失)")
        return False

def main():
    """主验证函数"""
    print("=" * 60)
    print("图书借阅系统 FastAPI 应用 - 项目完整性验证")
    print("=" * 60)
    
    all_good = True
    
    # 核心文件检查
    print("\n1. 核心文件检查:")
    core_files = [
        ("main.py", "主应用文件"),
        ("requirements.txt", "依赖文件"),
        ("start_server.py", "启动脚本"),
        ("pytest.ini", "pytest配置"),
        ("pyproject.toml", "项目配置"),
        ("README.md", "项目说明"),
        ("PROJECT_SUMMARY.md", "项目总结")
    ]
    
    for file_path, desc in core_files:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # 目录结构检查
    print("\n2. 目录结构检查:")
    directories = [
        ("app", "应用目录"),
        ("app/models", "模型目录"),
        ("app/repositories", "仓库目录"),
        ("app/services", "服务目录"),
        ("app/routers", "路由目录"),
        ("tests", "测试目录")
    ]
    
    for dir_path, desc in directories:
        if not check_directory_exists(dir_path, desc):
            all_good = False
    
    # 应用模块检查
    print("\n3. 应用模块检查:")
    app_files = [
        ("app/__init__.py", "应用初始化"),
        ("app/database.py", "数据库配置"),
        ("app/dependencies.py", "依赖注入"),
        ("app/enums.py", "枚举定义"),
        ("app/models/database.py", "数据库模型"),
        ("app/models/pydantic.py", "Pydantic模型")
    ]
    
    for file_path, desc in app_files:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # 路由模块检查
    print("\n4. 路由模块检查:")
    router_files = [
        ("app/routers/books.py", "图书路由"),
        ("app/routers/readers.py", "读者路由"),
        ("app/routers/borrows.py", "借阅路由"),
        ("app/routers/reservations.py", "预约路由")
    ]
    
    for file_path, desc in router_files:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # 服务模块检查
    print("\n5. 服务模块检查:")
    service_files = [
        ("app/services/book_service.py", "图书服务"),
        ("app/services/reader_service.py", "读者服务"),
        ("app/services/borrow_service.py", "借阅服务"),
        ("app/services/reservation_service.py", "预约服务")
    ]
    
    for file_path, desc in service_files:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # 仓库模块检查
    print("\n6. 仓库模块检查:")
    repo_files = [
        ("app/repositories/book_repository.py", "图书仓库"),
        ("app/repositories/reader_repository.py", "读者仓库"),
        ("app/repositories/borrow_repository.py", "借阅仓库"),
        ("app/repositories/reservation_repository.py", "预约仓库")
    ]
    
    for file_path, desc in repo_files:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # 测试文件检查
    print("\n7. 测试文件检查:")
    test_files = [
        ("tests/conftest.py", "测试配置"),
        ("tests/test_simple.py", "简单测试"),
        ("tests/test_main.py", "主应用测试"),
        ("tests/test_books.py", "图书测试"),
        ("tests/test_readers.py", "读者测试"),
        ("tests/test_borrows.py", "借阅测试"),
        ("tests/test_reservations.py", "预约测试")
    ]
    
    for file_path, desc in test_files:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # 导入测试
    print("\n8. 模块导入测试:")
    try:
        from main import app
        print("✓ 主应用模块导入成功")
    except Exception as e:
        print(f"✗ 主应用模块导入失败: {e}")
        all_good = False
    
    try:
        from app.models.database import Base
        print("✓ 数据库模型导入成功")
    except Exception as e:
        print(f"✗ 数据库模型导入失败: {e}")
        all_good = False
    
    # 统计信息
    print("\n9. 项目统计:")
    py_files = list(Path(".").rglob("*.py"))
    print(f"✓ Python文件总数: {len(py_files)}")
    
    test_files_count = len(list(Path("tests").glob("test_*.py")))
    print(f"✓ 测试文件数量: {test_files_count}")
    
    # 最终结果
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 项目验证通过！所有必要文件都已存在。")
        print("\n快速开始:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 启动服务: python start_server.py")
        print("3. 运行测试: pytest tests/test_simple.py -v")
        print("4. 访问文档: http://localhost:8000/docs")
        return 0
    else:
        print("❌ 项目验证失败！存在缺失文件。")
        return 1

if __name__ == "__main__":
    sys.exit(main())