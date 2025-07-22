#!/usr/bin/env python3
"""测试模型加载和卸载功能"""

import requests
import time
import json
import os

# 禁用代理
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

BASE_URL = "http://localhost:8000"

def check_status():
    """检查引擎状态"""
    resp = requests.get(f"{BASE_URL}/engine/status")
    status = resp.json()
    loaded_models = [m['name'] for m in status.get('loaded_models', [])]
    print(f"当前已加载模型: {loaded_models}")
    return loaded_models

def check_api_docs():
    """检查 API 文档中的模型数量"""
    resp = requests.get(f"{BASE_URL}/openapi.json")
    openapi = resp.json()
    
    # 统计图书管理系统的 API 路径
    library_apis = []
    for path in openapi.get('paths', {}):
        if '图书' in path or 'library' in path.lower():
            library_apis.append(path)
    
    print(f"API 文档中图书管理系统的端点数: {len(library_apis)}")
    return library_apis

def load_model(model_name):
    """加载模型"""
    print(f"\n正在加载模型: {model_name}")
    resp = requests.post(f"{BASE_URL}/engine/models/load", params={"model_name": model_name})
    print(f"响应状态码: {resp.status_code}")
    print(f"响应内容: {resp.text}")
    return resp.status_code == 200

def unload_model(model_name):
    """卸载模型"""
    print(f"\n正在卸载模型: {model_name}")
    resp = requests.delete(f"{BASE_URL}/engine/models/{model_name}")
    print(f"响应状态码: {resp.status_code}")
    print(f"响应内容: {resp.text}")
    return resp.status_code == 200

def main():
    print("=== 测试模型加载和卸载功能 ===\n")
    
    # 1. 初始状态
    print("1. 初始状态:")
    loaded_models = check_status()
    api_count = check_api_docs()
    
    # 2. 尝试加载图书管理系统
    if "图书管理系统" not in loaded_models:
        if load_model("图书管理系统"):
            time.sleep(2)  # 等待加载完成
            print("\n2. 加载后状态:")
            loaded_models = check_status()
            api_count = check_api_docs()
    
    # 3. 卸载图书管理系统
    if "图书管理系统" in loaded_models:
        if unload_model("图书管理系统"):
            time.sleep(2)  # 等待卸载完成
            print("\n3. 卸载后状态:")
            loaded_models = check_status()
            api_count = check_api_docs()
            
            # 验证 API 是否还能访问
            print("\n4. 测试 API 访问:")
            try:
                resp = requests.get(f"{BASE_URL}/api/v1/图书管理系统/books")
                print(f"访问图书 API 状态码: {resp.status_code}")
                print(f"响应: {resp.text[:100]}")
            except Exception as e:
                print(f"访问失败: {e}")

if __name__ == "__main__":
    main()