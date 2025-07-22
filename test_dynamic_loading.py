#!/usr/bin/env python3
"""Test script for dynamic loading and unloading of PIM models"""

import requests
import json
import time
import os

# Disable proxy for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

def check_api_docs():
    """Check what's available in API docs"""
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        openapi = response.json()
        paths = list(openapi.get("paths", {}).keys())
        print(f"Total API paths: {len(paths)}")
        # Filter for model-specific paths
        model_paths = [p for p in paths if p.startswith("/api/v1/") and not p.startswith("/api/v1/codegen")]
        print(f"Model API paths: {len(model_paths)}")
        for path in sorted(model_paths)[:10]:  # Show first 10
            print(f"  - {path}")
        if len(model_paths) > 10:
            print(f"  ... and {len(model_paths) - 10} more")
    else:
        print(f"Failed to get OpenAPI spec: {response.status_code}")

def list_models():
    """List currently loaded models"""
    response = requests.get(f"{BASE_URL}/engine/models")
    if response.status_code == 200:
        data = response.json()
        print(f"Loaded models: {data['total']}")
        for model in data['models']:
            print(f"  - {model['name']} (v{model['version']})")
            print(f"    Entities: {', '.join(model['entities'])}")
            print(f"    Services: {', '.join(model['services'])}")
    else:
        print(f"Failed to list models: {response.status_code}")

def load_model(model_name):
    """Load a model"""
    print(f"\nLoading model: {model_name}")
    response = requests.post(f"{BASE_URL}/engine/models/load?model_name={model_name}")
    print(f"Response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Load time: {data.get('load_time_ms', 'N/A')}ms")
        print(f"  Entities: {data.get('entities', 'N/A')}")
        print(f"  Services: {data.get('services', 'N/A')}")
        return True
    else:
        print(f"  Error: {response.text}")
        return False

def unload_model(model_name):
    """Unload a model"""
    print(f"\nUnloading model: {model_name}")
    response = requests.delete(f"{BASE_URL}/engine/models/{model_name}")
    print(f"Response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Message: {data['message']}")
        return True
    else:
        print(f"  Error: {response.text}")
        return False

def test_model_api(model_name):
    """Test if model API endpoints are accessible"""
    # Try to access a model endpoint
    test_url = f"{BASE_URL}/api/v1/{model_name.lower().replace(' ', '-')}/users"
    print(f"\nTesting API endpoint: {test_url}")
    response = requests.get(test_url)
    print(f"Response: {response.status_code}")
    if response.status_code == 200:
        print("  API is accessible")
        return True
    else:
        print(f"  API not accessible: {response.text[:100]}")
        return False

def main():
    print_section("PIM Engine Dynamic Loading Test")
    
    # Step 1: Check initial state
    print_section("Step 1: Initial State")
    list_models()
    check_api_docs()
    
    # Step 2: Load a model
    print_section("Step 2: Load User Management Model")
    if load_model("user_management"):
        time.sleep(2)  # Give it time to update
        list_models()
        check_api_docs()
        test_model_api("user-management")
    
    # Step 3: Load another model
    print_section("Step 3: Load Order Management Model")
    if load_model("order_management"):
        time.sleep(2)
        list_models()
        check_api_docs()
    
    # Step 4: Test APIs work
    print_section("Step 4: Test Model APIs")
    test_model_api("user-management")
    test_model_api("order-management")
    
    # Step 5: Unload first model
    print_section("Step 5: Unload User Management Model")
    if unload_model("user_management"):
        time.sleep(2)
        list_models()
        check_api_docs()
        test_model_api("user-management")  # Should fail now
    
    # Step 6: Reload the model
    print_section("Step 6: Reload User Management Model")
    if load_model("user_management"):
        time.sleep(2)
        list_models()
        check_api_docs()
        test_model_api("user-management")  # Should work again
    
    # Step 7: Final state
    print_section("Step 7: Final State")
    list_models()
    
    print_section("Test Complete")

if __name__ == "__main__":
    main()