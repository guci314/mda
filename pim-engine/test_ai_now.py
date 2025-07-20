#!/usr/bin/env python3
"""Quick test for AI code generation"""

import requests
import json
import time

print("=== Testing AI Code Generation ===\n")

# 1. Check health
print("1. Checking service health...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"   Status: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")
    exit(1)

# 2. Check LLM providers
print("\n2. Checking LLM providers...")
response = requests.get("http://localhost:8000/api/v1/codegen/llm/providers")
providers = response.json()
print(f"   Available providers: {[p['name'] for p in providers['providers'] if p['available']]}")

# 3. Generate code with AI
print("\n3. Generating code with AI...")
start_time = time.time()

response = requests.post(
    "http://localhost:8000/api/v1/codegen/generate",
    json={
        "model_name": "user_management",
        "platform": "fastapi",
        "use_llm": True,
        "llm_provider": "gemini"
    }
)

elapsed = time.time() - start_time

if response.status_code == 200:
    result = response.json()
    print(f"   ✅ Success! Generated {len(result['files'])} files in {elapsed:.1f}s")
    
    # Save result
    with open("ai_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Check for actual implementation
    has_implementation = False
    for file in result['files']:
        content = file.get('content', '')
        if 'def ' in content and 'TODO' not in content and 'NotImplementedError' not in content:
            has_implementation = True
            # Show a sample
            if 'service' in file['path'].lower():
                print(f"\n   Sample from {file['path']}:")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'def registerUser' in line:
                        # Print function and next 15 lines
                        for j in range(i, min(i+15, len(lines))):
                            print(f"     {lines[j]}")
                        break
                break
    
    print(f"\n   Has real implementation: {'✅ Yes' if has_implementation else '❌ No'}")
    print(f"   Full result saved to: ai_result.json")
    
else:
    print(f"   ❌ Failed: {response.json()}")

# 4. Compare with template generation
print("\n4. Generating code with templates...")
response = requests.post(
    "http://localhost:8000/api/v1/codegen/generate",
    json={
        "model_name": "user_management",
        "platform": "fastapi",
        "use_llm": False
    }
)

if response.status_code == 200:
    result = response.json()
    with open("template_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Count TODOs
    todo_count = sum(1 for f in result['files'] if 'TODO' in f.get('content', ''))
    print(f"   Files with TODOs: {todo_count}/{len(result['files'])}")

print("\n✅ Test complete!")