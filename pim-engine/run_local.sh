#!/bin/bash

echo "=== Running PIM Engine Locally (with Docker for DB/Redis) ==="
echo

# 1. 启动数据库和 Redis（使用 Docker）
echo "1. Starting PostgreSQL and Redis in Docker..."
docker compose -f docker-compose.local.yml up -d

# 2. 等待服务启动
echo "2. Waiting for services to start..."
sleep 5

# 3. 设置环境变量
echo "3. Setting environment variables..."
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

# 代理配置（本地运行可以直接使用 localhost）
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export NO_PROXY="localhost,127.0.0.1"

echo "Environment configured:"
echo "  Database: $DATABASE_URL"
echo "  Redis: $REDIS_URL"
echo "  LLM Provider: $LLM_PROVIDER"
echo "  Proxy: $HTTP_PROXY"

# 4. 检查 Python 环境
echo -e "\n4. Checking Python environment..."
python3 --version

# 5. 安装依赖（如果需要）
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt
pip install anthropic aiohttp httpx

# 6. 检查 Gemini CLI
echo -e "\n5. Checking Gemini CLI..."
which gemini || echo "Gemini CLI not found. Installing..."
if ! which gemini > /dev/null 2>&1; then
    echo "Installing Gemini CLI..."
    npm install -g @google/gemini-cli
fi

gemini --version

# 7. 启动 PIM Engine
echo -e "\n6. Starting PIM Engine locally..."
cd src
python -m main