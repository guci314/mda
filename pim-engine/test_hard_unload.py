#!/usr/bin/env python3
"""Test hard unload functionality"""

import requests
import time
import os

# Disable proxy for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

API_URL = "http://127.0.0.1:8000"

def test_hard_unload():
    """Test hard unload of a model"""
    
    print("=== Testing Hard Unload Functionality ===")
    
    # Check if hello_world_pim is loaded
    print("\n1. Checking loaded models...")
    try:
        response = requests.get(f"{API_URL}/models")
        if response.status_code != 200:
            print(f"   Error: Got status code {response.status_code}")
            print(f"   Response: {response.text}")
            return
        models = response.json()
        print(f"   Current models: {[m['name'] for m in models['models']]}")
    except requests.exceptions.RequestException as e:
        print(f"   Error connecting to API: {e}")
        return
    except Exception as e:
        print(f"   Error: {e}")
        print(f"   Response status: {response.status_code}")
        print(f"   Response text: {response.text}")
        return
    
    if not any(m['name'] == 'hello_world_pim' for m in models['models']):
        print("   hello_world_pim not loaded, loading it first...")
        response = requests.post(f"{API_URL}/models/load", json={"model_name": "hello_world_pim"})
        if response.status_code == 200:
            print("   Model loaded successfully")
        else:
            print(f"   Failed to load model: {response.text}")
            return
    
    # Check model directory exists
    model_dir = "classpath/hello_world_pim"
    print(f"\n2. Checking model directory: {model_dir}")
    if os.path.exists(model_dir):
        print(f"   Directory exists")
        # List some files
        for root, dirs, files in os.walk(model_dir):
            level = root.replace(model_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"   {indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show max 5 files per dir
                print(f"   {subindent}{file}")
            if len(files) > 5:
                print(f"   {subindent}... and {len(files) - 5} more files")
    else:
        print(f"   Directory does not exist")
    
    # Perform hard unload
    print("\n3. Performing hard unload...")
    response = requests.delete(f"{API_URL}/models/hello_world_pim?hard=true")
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: {result['message']}")
        print(f"   Hard delete: {result.get('hard_delete', False)}")
        print(f"   Instances stopped: {result.get('instances_stopped', 0)}")
    else:
        print(f"   Failed: {response.text}")
        return
    
    # Check if model directory was deleted
    print(f"\n4. Verifying directory deletion...")
    if os.path.exists(model_dir):
        print(f"   ERROR: Directory still exists!")
    else:
        print(f"   SUCCESS: Directory has been deleted")
    
    # Verify model is unloaded
    print("\n5. Verifying model is unloaded...")
    response = requests.get(f"{API_URL}/models")
    models = response.json()
    if not any(m['name'] == 'hello_world_pim' for m in models['models']):
        print("   SUCCESS: Model is no longer loaded")
    else:
        print("   ERROR: Model is still loaded!")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_hard_unload()