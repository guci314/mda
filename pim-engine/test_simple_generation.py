#!/usr/bin/env python3
"""Simple test for code generation comparison"""

import requests
import json
import time

API_BASE = "http://localhost:8001"

def test_template_generation():
    """Test template-based code generation"""
    print("=== Testing Template Generation ===")
    
    response = requests.post(
        f"{API_BASE}/api/v1/codegen/generate",
        json={
            "model_name": "user_management",
            "platform": "fastapi",
            "use_llm": False
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Generated {len(result['files'])} files")
        
        # Check for TODOs in generated code
        todo_count = 0
        for file in result['files']:
            if 'TODO' in file.get('content', '') or 'NotImplementedError' in file.get('content', ''):
                todo_count += 1
        
        print(f"  Files with TODOs: {todo_count}/{len(result['files'])}")
        
        # Show a sample
        for file in result['files']:
            if 'service' in file['path'].lower():
                print(f"\nSample from {file['path']}:")
                lines = file['content'].split('\n')[:30]
                for line in lines:
                    if 'def ' in line or 'TODO' in line or 'NotImplementedError' in line:
                        print(f"  {line.strip()}")
                break
    else:
        print(f"✗ Failed: {response.text}")

def test_ai_generation():
    """Test AI-based code generation"""
    print("\n=== Testing AI Generation (without proxy) ===")
    
    # First, let's test if Gemini is available
    providers_response = requests.get(f"{API_BASE}/api/v1/codegen/llm/providers")
    if providers_response.status_code == 200:
        providers = providers_response.json()
        print("Available providers:")
        for p in providers['providers']:
            print(f"  - {p['name']}: {'✓' if p['available'] else '✗'}")
    
    # Try generation without proxy
    print("\nAttempting code generation...")
    response = requests.post(
        f"{API_BASE}/api/v1/codegen/generate",
        json={
            "model_name": "user_management",
            "platform": "fastapi",
            "use_llm": True,
            "llm_provider": "gemini",
            "options": {
                "use_llm_for_all": True
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Generated {len(result['files'])} files with AI")
        
        # Check for actual implementation
        impl_count = 0
        for file in result['files']:
            content = file.get('content', '')
            if 'TODO' not in content and 'NotImplementedError' not in content and len(content) > 100:
                impl_count += 1
        
        print(f"  Files with implementations: {impl_count}/{len(result['files'])}")
    else:
        print(f"✗ Failed: {response.json().get('detail', response.text)}")

def test_model_loading():
    """Test model loading"""
    print("\n=== Testing Model Loading ===")
    
    response = requests.get(f"{API_BASE}/api/v1/models")
    if response.status_code == 200:
        models = response.json()
        print(f"Loaded models: {len(models['models'])}")
        for model in models['models']:
            print(f"  - {model['name']}: {model['status']}")
    else:
        print(f"✗ Failed to get models: {response.text}")

if __name__ == "__main__":
    print("PIM Engine Code Generation Test\n")
    
    # Check API health
    try:
        health = requests.get(f"{API_BASE}/health").json()
        print(f"API Status: {health['status']}")
        print(f"Models loaded: {health['models_loaded']}\n")
    except Exception as e:
        print(f"Failed to connect to API: {e}")
        exit(1)
    
    test_model_loading()
    test_template_generation()
    test_ai_generation()
    
    print("\nTest complete!")