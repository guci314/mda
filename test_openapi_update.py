#!/usr/bin/env python3
"""Test that OpenAPI documentation updates correctly with dynamic loading"""

import requests
import os

# Disable proxy for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

BASE_URL = "http://localhost:8000"

def get_api_paths():
    """Get all API paths from OpenAPI spec"""
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get("paths", {})
        # Show all paths first
        print("\nAll paths in OpenAPI:")
        for path in sorted(paths.keys()):
            print(f"  {path}")
        
        # Filter for model API paths
        model_paths = {
            path: list(methods.keys())
            for path, methods in paths.items()
            if path.startswith("/api/v1/") and not path.startswith("/api/v1/codegen")
        }
        return model_paths
    return {}

print("Initial API paths:")
initial_paths = get_api_paths()
for path, methods in sorted(initial_paths.items()):
    print(f"  {path}: {methods}")

print(f"\nTotal model API paths: {len(initial_paths)}")

# Check Swagger UI
print(f"\nSwagger UI available at: {BASE_URL}/docs")
print(f"ReDoc available at: {BASE_URL}/redoc")