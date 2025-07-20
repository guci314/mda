#!/bin/bash

# 设置 Gemini API Key
export GOOGLE_AI_STUDIO_KEY="AIzaSyAK6A0j6OkkDaUd6nB2mgFuzjnWowKBaE0"
export LLM_PROVIDER="gemini"
export USE_LLM_FOR_ALL="true"

# 检测操作系统和设置代理主机
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux: 获取 Docker 网桥 IP
    DOCKER_HOST_IP=$(ip -4 addr show docker0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "172.17.0.1")
    export PROXY_HOST=$DOCKER_HOST_IP
    echo "Detected Linux system, using Docker bridge IP: $PROXY_HOST"
elif [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "msys" ]]; then
    # macOS or Windows (Docker Desktop)
    export PROXY_HOST="host.docker.internal"
    echo "Detected Docker Desktop, using host.docker.internal"
else
    # 默认使用 Docker 网桥 IP
    export PROXY_HOST="172.17.0.1"
    echo "Using default Docker bridge IP: $PROXY_HOST"
fi

# 代理端口（根据你的实际代理端口修改）
export PROXY_PORT="7890"

echo "Starting PIM Engine with Gemini AI support..."
echo "API Key configured: ${GOOGLE_AI_STUDIO_KEY:0:10}..."
echo "Proxy configured: http://$PROXY_HOST:$PROXY_PORT"

# 先停止旧的容器
docker compose -f docker-compose.llm.yml down

# 使用 LLM 版本的 docker-compose
docker compose -f docker-compose.llm.yml up -d --build

echo "Waiting for services to start..."
sleep 10

# 检查服务状态
docker compose -f docker-compose.llm.yml ps

# 测试 LLM 提供商状态
echo ""
echo "Checking LLM providers..."
curl -s http://localhost:8001/api/v1/codegen/llm/providers | python3 -m json.tool || echo "API not ready yet"

echo ""
echo "PIM Engine with AI is running at http://localhost:8001"
echo "To view logs: docker compose -f docker-compose.llm.yml logs -f pim-engine"
echo "To stop: docker compose -f docker-compose.llm.yml down"