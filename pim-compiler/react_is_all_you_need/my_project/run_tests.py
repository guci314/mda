#!/usr/bin/env python3
"""运行测试的主脚本"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

# 清理环境
for f in ["blog.db", "test.db"]:
    if os.path.exists(f):
        os.remove(f)

# 设置内存数据库
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# 导入应用
from main import app

class TestRunner:
    def __init__(self):
        self.client = TestClient(app)
        self.test_category = {
            "name": "测试分类",
            "description": "这是一个测试分类的描述"
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=== 开始运行测试 ===")
        
        tests = [
            self.test_health_check,
            self.test_create_category,
            self.test_get_categories,
            self.test_get_category_by_id,
            self.test_update_category,
            self.test_delete_category
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                test()
                passed += 1
                print(f"✅ {test.__name__} 通过")
            except Exception as e:
                failed += 1
                print(f"❌ {test.__name__} 失败: {e}")
        
        print(f"\n=== 测试结果 ===")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"总计: {passed + failed}")
        
        return failed == 0
    
    def test_health_check(self):
        """测试健康检查"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_create_category(self):
        """测试创建分类"""
        response = self.client.post("/api/v1/categories/", json=self.test_category)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == self.test_category["name"]
        assert data["description"] == self.test_category["description"]
        assert "id" in data
        self.category_id = data["id"]
    
    def test_get_categories(self):
        """测试获取分类列表"""
        # 确保有数据
        self.test_create_category()
        
        response = self.client.get("/api/v1/categories/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_category_by_id(self):
        """测试根据ID获取分类"""
        # 确保有数据
        self.test_create_category()
        
        response = self.client.get(f"/api/v1/categories/{self.category_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.category_id
    
    def test_update_category(self):
        """测试更新分类"""
        # 确保有数据
        self.test_create_category()
        
        updated_data = {
            "name": "更新后的分类名",
            "description": "更新后的描述"
        }
        response = self.client.put(f"/api/v1/categories/{self.category_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == updated_data["name"]
    
    def test_delete_category(self):
        """测试删除分类"""
        # 确保有数据
        self.test_create_category()
        
        response = self.client.delete(f"/api/v1/categories/{self.category_id}")
        assert response.status_code == 200
        
        # 验证已删除
        response = self.client.get(f"/api/v1/categories/{self.category_id}")
        assert response.status_code == 404


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)