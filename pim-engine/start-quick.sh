#!/bin/bash

# 设置环境变量
export GOOGLE_AI_STUDIO_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0"
export LLM_PROVIDER="gemini"
export USE_LLM_FOR_ALL="true"
export PROXY_HOST="172.17.0.1"
export PROXY_PORT="7890"

echo "Starting PIM Engine with Gemini AI support..."
echo "API Key: ${GOOGLE_AI_STUDIO_KEY:0:10}..."
echo "Proxy: http://$PROXY_HOST:$PROXY_PORT"

# 启动服务（不重新构建）
docker compose -f docker-compose.llm.yml up -d

echo "Waiting for services to start..."
sleep 10

# 检查状态
docker compose -f docker-compose.llm.yml ps

echo -e "\nChecking LLM providers:"
curl --noproxy localhost -s http://localhost:8001/api/v1/codegen/llm/providers | python3 -m json.tool

echo -e "\nPIM Engine is running at http://localhost:8001"