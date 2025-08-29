#!/usr/bin/env python3
"""调试测试问题的脚本"""

import sys
import traceback

def test_imports():
    """测试导入问题"""
    try:
        from main import app
        print("✅ 成功导入main.py")
        
        from fastapi.testclient import TestClient
        print("✅ 成功导入TestClient")
        
        client = TestClient(app)
        print("✅ 成功创建TestClient")
        
        # 测试根路径
        response = client.get("/")
        print(f"✅ 根路径响应: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        # 测试健康检查
        response = client.get("/health")
        print(f"✅ 健康检查响应: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()