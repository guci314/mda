#!/usr/bin/env python3
"""测试卸载模型后重启应用的功能"""

import requests
import time
import os

# 禁用代理
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

BASE_URL = "http://localhost:8001"

def check_status():
    """检查引擎状态"""
    try:
        resp = requests.get(f"{BASE_URL}/engine/status", timeout=5)
        if resp.status_code == 200:
            status = resp.json()
            loaded_models = [m['name'] for m in status.get('loaded_models', [])]
            print(f"✓ 引擎状态: 运行中")
            print(f"  已加载模型: {loaded_models}")
            return loaded_models
        else:
            print(f"✗ 引擎状态: 错误 {resp.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        print("✗ 引擎状态: 未连接")
        return []
    except Exception as e:
        print(f"✗ 引擎状态: 异常 {e}")
        return []

def load_model(model_name):
    """加载模型"""
    print(f"\n正在加载模型: {model_name}")
    try:
        resp = requests.post(f"{BASE_URL}/engine/models/load", params={"model_name": model_name})
        if resp.status_code == 200:
            print(f"✓ 加载成功")
            return True
        else:
            print(f"✗ 加载失败: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"✗ 加载失败: {e}")
        return False

def unload_model(model_name):
    """卸载模型（将触发重启）"""
    print(f"\n正在卸载模型: {model_name}")
    try:
        resp = requests.delete(f"{BASE_URL}/engine/models/{model_name}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"✓ 卸载成功: {result.get('message', '')}")
            return True
        else:
            print(f"✗ 卸载失败: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"✗ 卸载失败: {e}")
        return False

def wait_for_restart(max_wait=30):
    """等待应用重启"""
    print("\n等待应用重启...")
    start_time = time.time()
    
    # 首先等待服务下线
    while time.time() - start_time < max_wait:
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=1)
            if resp.status_code != 200:
                break
        except:
            break
        time.sleep(0.5)
        print(".", end="", flush=True)
    
    print("\n服务已下线，等待重新启动...")
    
    # 然后等待服务上线
    while time.time() - start_time < max_wait:
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=1)
            if resp.status_code == 200:
                print("✓ 服务已重启")
                return True
        except:
            pass
        time.sleep(1)
        print(".", end="", flush=True)
    
    print("\n✗ 服务重启超时")
    return False

def check_api_docs():
    """检查 API 文档中的模型数量"""
    try:
        resp = requests.get(f"{BASE_URL}/openapi.json")
        if resp.status_code == 200:
            openapi = resp.json()
            
            # 统计图书管理系统的 API 路径
            library_apis = []
            for path in openapi.get('paths', {}):
                if '图书' in path or 'library' in path.lower():
                    library_apis.append(path)
            
            print(f"  API 文档中图书管理系统的端点数: {len(library_apis)}")
            return len(library_apis)
        else:
            print(f"  无法获取 API 文档: {resp.status_code}")
            return -1
    except Exception as e:
        print(f"  获取 API 文档失败: {e}")
        return -1

def main():
    print("=== 测试卸载模型后重启应用功能 ===\n")
    
    # 1. 检查初始状态
    print("1. 初始状态:")
    loaded_models = check_status()
    api_count_before = check_api_docs()
    
    # 2. 如果图书管理系统未加载，先加载它
    if "图书管理系统" not in loaded_models:
        if load_model("图书管理系统"):
            time.sleep(2)
            print("\n2. 加载后状态:")
            loaded_models = check_status()
            api_count_before = check_api_docs()
    
    # 3. 卸载图书管理系统（触发重启）
    if "图书管理系统" in loaded_models:
        print(f"\n3. 执行卸载操作...")
        if unload_model("图书管理系统"):
            # 4. 等待重启
            if wait_for_restart():
                time.sleep(2)  # 给一点时间让服务完全启动
                
                # 5. 检查重启后状态
                print("\n4. 重启后状态:")
                loaded_models_after = check_status()
                api_count_after = check_api_docs()
                
                # 6. 验证结果
                print("\n5. 验证结果:")
                if "图书管理系统" not in loaded_models_after:
                    print("✓ 模型已成功卸载")
                else:
                    print("✗ 模型仍在加载列表中")
                
                if api_count_before > 0 and api_count_after == 0:
                    print("✓ API 文档已更新，移除了相关端点")
                else:
                    print(f"✗ API 文档未正确更新 (之前: {api_count_before}, 之后: {api_count_after})")

if __name__ == "__main__":
    main()