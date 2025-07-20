#!/bin/bash

echo "=== Starting PIM Engine Locally ==="
echo

# 1. 停止并启动数据库服务
docker compose -f docker-compose.local.yml down
docker compose -f docker-compose.local.yml up -d

echo "Waiting for database..."
sleep 5

# 2. 设置环境变量
export DATABASE_URL="postgresql://pim:pim123@localhost:5432/pim_engine"
export REDIS_URL="redis://localhost:6379"
export PYTHONPATH="/home/guci/aiProjects/mda/pim-engine/src"
export LOG_LEVEL="INFO"
export HOT_RELOAD="true"
export SECRET_KEY="your-secret-key-please-change-in-production"

# LLM 配置
export LLM_PROVIDER="gemini"
export USE_LLM_FOR_ALL="true"
export GOOGLE_AI_STUDIO_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0"
export GEMINI_API_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0"
export LLM_TIMEOUT_SECONDS="1200"

# 代理配置
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export NO_PROXY="localhost,127.0.0.1"

# 3. 检查 Gemini CLI
echo -e "\nChecking Gemini CLI..."
gemini --version || echo "Gemini CLI not found. Please install: npm install -g @google/gemini-cli"

# 4. 启动引擎
echo -e "\nStarting PIM Engine on http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Models UI: http://localhost:8000/models"
echo -e "\nPress Ctrl+C to stop\n"

cd /home/guci/aiProjects/mda/pim-engine/src
python3 -m main