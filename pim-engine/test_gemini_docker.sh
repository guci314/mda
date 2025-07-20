#!/bin/bash

echo "=== Gemini CLI Docker Integration Test ==="
echo

# 1. 重建镜像
echo "1. Rebuilding Docker image with Gemini CLI..."
docker compose -f docker-compose.llm.yml build --no-cache pim-engine

# 2. 启动容器
echo -e "\n2. Starting container..."
docker compose -f docker-compose.llm.yml up -d
sleep 5

# 3. 检查安装
echo -e "\n3. Checking Gemini CLI installation..."
docker exec pim-engine bash -c '
    echo "NPM packages:"
    npm list -g --depth=0 | grep gemini || echo "No gemini package found"
    
    echo -e "\nChecking commands:"
    which gemini && echo "Found: gemini" || echo "gemini command not found"
    which npx && echo "Found: npx" || echo "npx not found"
    
    echo -e "\nTrying npx @google/gemini-cli:"
    npx @google/gemini-cli --help 2>&1 | head -5 || echo "Failed to run via npx"
'

# 4. 运行简单测试
echo -e "\n4. Running simple test..."
docker exec pim-engine python /app/tests/test_gemini_cli_simple.py

# 5. 检查日志
echo -e "\n5. Recent container logs:"
docker compose -f docker-compose.llm.yml logs --tail=20 pim-engine

echo -e "\nTest complete!"