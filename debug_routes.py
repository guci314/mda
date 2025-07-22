#!/usr/bin/env python3
"""Debug script to check actual routes in FastAPI app"""

import requests
import os

# Disable proxy for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

BASE_URL = "http://localhost:8000"

# First, let's check what routes are actually registered
print("Checking actual routes via API test:")

# Test known model routes
test_routes = [
    "/api/v1/user-management/users",
    "/api/v1/order-management/products",
    "/api/v1/order-management/orders",
]

for route in test_routes:
    url = f"{BASE_URL}{route}"
    response = requests.get(url)
    print(f"{route}: {response.status_code}")

# Check OpenAPI
print("\nChecking OpenAPI paths:")
response = requests.get(f"{BASE_URL}/openapi.json")
if response.status_code == 200:
    openapi = response.json()
    paths = openapi.get("paths", {})
    
    # Count API paths
    api_paths = [p for p in paths if p.startswith("/api/v1/")]
    print(f"Total paths: {len(paths)}")
    print(f"API v1 paths: {len(api_paths)}")
    
    # Show API paths
    if api_paths:
        print("\nAPI paths found:")
        for path in sorted(api_paths):
            print(f"  {path}")
    else:
        print("\nNo API paths found in OpenAPI!")
        
    # Check if routes exist but aren't in OpenAPI
    print("\nChecking for route registration issue...")
    print("Loaded models in OpenAPI manager:", openapi.get("x-loaded-models", "Not tracked"))