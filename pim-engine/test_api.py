#!/usr/bin/env python3
import requests
import json
import traceback

url = 'http://localhost:8001/api/v1/codegen/generate'
data = {'model_name': 'user_management', 'platform': 'fastapi'}

print("Testing code generation API...")
try:
    resp = requests.post(url, json=data)
    print(f'Status: {resp.status_code}')
    print(f'Headers: {dict(resp.headers)}')
    print(f'Response: {resp.text}')
    
    if resp.status_code == 200:
        result = resp.json()
        print("\nSuccess! Generated code package:")
        print(f"Package ID: {result.get('package_id')}")
        print(f"Model: {result.get('model_name')}")
        print(f"Platform: {result.get('platform')}")
        print(f"Files: {len(result.get('files', []))}")
        for file in result.get('files', [])[:5]:
            print(f"  - {file['path']}: {file.get('description', 'No description')}")
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()