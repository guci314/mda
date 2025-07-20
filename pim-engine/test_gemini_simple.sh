#!/bin/bash

echo "=== Simple Gemini CLI Test ==="
echo

# 使用已有的启动脚本
echo "1. Starting PIM Engine with Gemini support..."
./start-with-gemini-linux.sh

echo -e "\n2. Waiting for container to be ready..."
sleep 15

# 检查容器状态
echo -e "\n3. Container status:"
docker compose -f docker-compose.llm.yml ps

# 检查 Node.js 安装
echo -e "\n4. Checking Node.js installation:"
docker exec pim-engine bash -c "node --version && npm --version" || echo "Node.js not installed"

# 检查 Gemini CLI
echo -e "\n5. Checking Gemini CLI:"
docker exec pim-engine bash -c '
    echo "Looking for gemini command:"
    which gemini || echo "gemini not found"
    
    echo -e "\nNPM global packages:"
    npm list -g --depth=0 2>/dev/null | grep gemini || echo "No gemini package"
    
    echo -e "\nTrying npx @google/gemini-cli:"
    npx @google/gemini-cli --version 2>&1 || echo "npx gemini-cli failed"
'

# 测试 API
echo -e "\n6. Testing LLM providers API:"
curl -s http://localhost:8001/api/v1/codegen/llm/providers | python3 -m json.tool || echo "API not ready"

# 查看日志
echo -e "\n7. Recent logs:"
docker compose -f docker-compose.llm.yml logs --tail=10 pim-engine