#!/usr/bin/env python3
"""
简单的应用测试
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_app_import():
    """测试应用导入"""
    try:
        from main import app
        print("✅ 主应用导入成功")
        return True
    except Exception as e:
        print(f"❌ 主应用导入失败: {e}")
        return False


async def test_database_init():
    """测试数据库初始化"""
    try:
        from app.database import create_tables
        await create_tables()
        print("✅ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


async def test_basic_endpoints():
    """测试基本端点"""
    try:
        from httpx import AsyncClient
        from main import app
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 测试根路径
            response = await client.get("/")
            assert response.status_code == 200
            print("✅ 根路径测试通过")
            
            # 测试健康检查
            response = await client.get("/health")
            assert response.status_code == 200
            print("✅ 健康检查测试通过")
            
            # 测试API信息
            response = await client.get("/api/info")
            assert response.status_code == 200
            print("✅ API信息测试通过")
            
        return True
    except Exception as e:
        print(f"❌ 端点测试失败: {e}")
        return False


async def main():
    """主函数"""
    print("🧪 运行简单应用测试...")
    print("=" * 40)
    
    tests = [
        test_app_import(),
        test_database_init(),
        test_basic_endpoints()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    success_count = sum(1 for result in results if result is True)
    total_count = len(results)
    
    print("=" * 40)
    print(f"测试结果: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("✅ 所有测试通过！应用可以正常运行")
        return True
    else:
        print("❌ 部分测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)