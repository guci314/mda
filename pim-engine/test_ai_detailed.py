#!/usr/bin/env python3
"""Detailed test for AI code generation"""

import requests
import json
import time
import zipfile
import io
import re

print("=== Testing AI Code Generation (Detailed) ===\n")

# 1. Check health
print("1. Checking service health...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"   Status: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")
    exit(1)

# 2. Generate code with AI
print("\n2. Generating code with AI...")
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
    package_id = result['package_id']
    print(f"   ✅ Success! Generated {len(result['files'])} files in {elapsed:.1f}s")
    print(f"   Package ID: {package_id}")
    
    # 3. Download the generated code
    print("\n3. Downloading generated code...")
    download_response = requests.post(
        "http://localhost:8000/api/v1/codegen/download",
        json={"package_id": package_id}
    )
    
    if download_response.status_code == 200:
        # Extract and analyze the ZIP
        zip_buffer = io.BytesIO(download_response.content)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            # List all files
            file_list = zip_file.namelist()
            print(f"   Downloaded {len(file_list)} files")
            
            # Check service implementation
            service_files = [f for f in file_list if 'service' in f.lower() and f.endswith('.py')]
            
            has_real_implementation = False
            sample_shown = False
            
            for service_file in service_files:
                content = zip_file.read(service_file).decode('utf-8')
                
                # Check for real implementation
                has_def = 'def ' in content
                has_no_todo = 'TODO' not in content
                has_no_not_impl = 'NotImplementedError' not in content
                has_actual_code = bool(re.search(r'def \w+\(.*\):\s*\n\s*""".*"""\s*\n\s*[^#\s]', content, re.MULTILINE))
                
                if has_def and has_no_todo and has_no_not_impl and has_actual_code:
                    has_real_implementation = True
                    
                    if not sample_shown:
                        print(f"\n4. Sample from {service_file}:")
                        print("-" * 60)
                        
                        # Find and show a method implementation
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'def registerUser' in line or 'def register_user' in line:
                                # Show method and next 20 lines
                                for j in range(i, min(i+20, len(lines))):
                                    print(f"   {lines[j]}")
                                sample_shown = True
                                break
                        
                        if not sample_shown:
                            # Show any method
                            for i, line in enumerate(lines):
                                if line.strip().startswith('def ') and not line.strip().startswith('def __'):
                                    for j in range(i, min(i+20, len(lines))):
                                        print(f"   {lines[j]}")
                                    sample_shown = True
                                    break
                        print("-" * 60)
            
            print(f"\n5. Analysis:")
            print(f"   Has real implementation: {'✅ Yes' if has_real_implementation else '❌ No'}")
            print(f"   Total files: {len(file_list)}")
            print(f"   Service files: {len(service_files)}")
            
            # Save the zip
            with open("generated_code.zip", "wb") as f:
                f.write(download_response.content)
            print(f"   Code saved to: generated_code.zip")
            
    else:
        print(f"   ❌ Download failed: {download_response.text}")
        
else:
    print(f"   ❌ Generation failed: {response.json()}")

print("\n✅ Test complete!")