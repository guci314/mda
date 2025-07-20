#!/bin/bash

echo "=== Starting PIM Engine Locally (Background) ==="
echo

# 1. 确保数据库服务运行
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
export GEMINI_API_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0"
export LLM_TIMEOUT_SECONDS="1200"

# 代理配置（同时设置大写和小写）
export PROXY_HOST="127.0.0.1"
export PROXY_PORT="7890"
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export NO_PROXY="localhost,127.0.0.1"
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export no_proxy="localhost,127.0.0.1"

# 3. 启动引擎（后台）
echo "Starting PIM Engine in background..."
cd /home/guci/aiProjects/mda/pim-engine/src
nohup python3 -m main > ../pim-engine.log 2>&1 &
PID=$!

echo "PIM Engine started with PID: $PID"
echo "Log file: pim-engine.log"
echo

# 4. 等待服务启动
echo "Waiting for service to start..."
for i in {1..10}; do
    if curl --noproxy localhost -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Service is ready!"
        break
    fi
    echo -n "."
    sleep 1
done

echo -e "\n"

# 5. 显示状态
echo "Service URLs:"
echo "  API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Models UI: http://localhost:8000/models"
echo "  Debug UI: http://localhost:8000/debug/ui"
echo

echo "To stop the service:"
echo "  kill $PID"
echo "  docker compose -f docker-compose.local.yml down"
echo

echo "To view logs:"
echo "  tail -f pim-engine.log"