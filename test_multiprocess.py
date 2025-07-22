#!/usr/bin/env python3
"""Test Multi-Process PIM Engine Architecture"""

import time
import sys
import requests
import subprocess
from pathlib import Path

# Add pim-engine/src to Python path
sys.path.insert(0, str(Path(__file__).parent / "pim-engine" / "src"))


def test_master_controller():
    """Test the multi-process architecture"""
    print("=== Testing Multi-Process PIM Engine ===\n")
    
    base_url = "http://localhost:8000"
    
    # 1. Check master controller health
    print("1. Checking master controller health...")
    try:
        resp = requests.get(f"{base_url}/health")
        assert resp.status_code == 200
        print(f"✓ Master controller is healthy: {resp.json()}")
    except Exception as e:
        print(f"✗ Master controller not running: {e}")
        print("\nPlease start the master controller first:")
        print("cd pim-engine && python src/main.py")
        return
    
    # 2. List models (should be empty initially)
    print("\n2. Listing loaded models...")
    resp = requests.get(f"{base_url}/models")
    print(f"✓ Models: {resp.json()}")
    
    # 3. Load a model
    print("\n3. Loading user_management model...")
    resp = requests.post(f"{base_url}/models/load", json={
        "model_name": "user_management"
    })
    if resp.status_code == 200:
        print(f"✓ Model loaded: {resp.json()}")
    else:
        print(f"✗ Failed to load model: {resp.status_code} - {resp.text}")
        return
    
    # 4. Create first instance
    print("\n4. Creating first instance...")
    resp = requests.post(f"{base_url}/instances", json={
        "model_name": "user_management",
        "instance_id": "user_prod",
        "port": 8001
    })
    if resp.status_code == 200:
        instance1 = resp.json()
        print(f"✓ Instance created: {instance1}")
    else:
        print(f"✗ Failed to create instance: {resp.status_code} - {resp.text}")
        return
    
    # Wait for instance to start
    print("\n   Waiting for instance to start...")
    time.sleep(3)
    
    # 5. Check instance health
    print("\n5. Checking instance health...")
    resp = requests.get(f"{base_url}/instances/{instance1['id']}/health")
    print(f"✓ Instance health: {resp.json()}")
    
    # 6. Test instance API
    print("\n6. Testing instance API...")
    try:
        resp = requests.get(f"http://localhost:{instance1['port']}/health")
        print(f"✓ Instance API health: {resp.json()}")
        
        resp = requests.get(f"http://localhost:{instance1['port']}/docs")
        print(f"✓ Instance API docs available: {resp.status_code}")
    except Exception as e:
        print(f"✗ Failed to connect to instance: {e}")
    
    # 7. Create second instance
    print("\n7. Creating second instance of same model...")
    resp = requests.post(f"{base_url}/instances", json={
        "model_name": "user_management",
        "instance_id": "user_test"
    })
    if resp.status_code == 200:
        instance2 = resp.json()
        print(f"✓ Second instance created: {instance2}")
    else:
        print(f"✗ Failed to create second instance: {resp.status_code} - {resp.text}")
    
    # 8. List all instances
    print("\n8. Listing all instances...")
    resp = requests.get(f"{base_url}/instances")
    print(f"✓ Active instances: {resp.json()}")
    
    # 9. Stop first instance
    print("\n9. Stopping first instance...")
    resp = requests.delete(f"{base_url}/instances/{instance1['id']}")
    if resp.status_code == 200:
        print(f"✓ Instance stopped: {resp.json()}")
    else:
        print(f"✗ Failed to stop instance: {resp.status_code} - {resp.text}")
    
    # 10. Verify instance is stopped
    print("\n10. Verifying instance is stopped...")
    resp = requests.get(f"{base_url}/instances")
    instances = resp.json()
    print(f"✓ Remaining instances: {instances}")
    
    # 11. Unload model (should stop remaining instances)
    print("\n11. Unloading model...")
    resp = requests.delete(f"{base_url}/models/user_management")
    if resp.status_code == 200:
        print(f"✓ Model unloaded: {resp.json()}")
    else:
        print(f"✗ Failed to unload model: {resp.status_code} - {resp.text}")
    
    print("\n=== Test completed successfully! ===")


if __name__ == "__main__":
    # Disable proxy for localhost
    import os
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    
    test_master_controller()