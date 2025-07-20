#!/bin/bash

# 设置 Gemini API Key
export GOOGLE_AI_STUDIO_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0"
export LLM_PROVIDER="gemini"
export USE_LLM_FOR_ALL="true"

echo "Starting PIM Engine with Gemini AI support..."
echo "API Key configured: ${GOOGLE_AI_STUDIO_KEY:0:10}..."

# 使用 LLM 版本的 docker-compose
docker compose -f docker-compose.llm.yml up -d

echo "Waiting for services to start..."
sleep 10

# 检查服务状态
docker compose -f docker-compose.llm.yml ps

echo ""
echo "PIM Engine with AI is running at http://localhost:8001"
echo "To view logs: docker compose -f docker-compose.llm.yml logs -f pim-engine"
echo "To stop: docker compose -f docker-compose.llm.yml down"