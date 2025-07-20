#!/bin/bash

echo "=== Building PIM Engine with Proxy Support ==="
echo

# 设置代理
PROXY_HOST="${PROXY_HOST:-172.17.0.1}"  # Linux Docker 默认网桥
PROXY_PORT="${PROXY_PORT:-7890}"

HTTP_PROXY="http://${PROXY_HOST}:${PROXY_PORT}"
HTTPS_PROXY="http://${PROXY_HOST}:${PROXY_PORT}"
NO_PROXY="localhost,127.0.0.1,*.local"

echo "Proxy settings:"
echo "  HTTP_PROXY: $HTTP_PROXY"
echo "  HTTPS_PROXY: $HTTPS_PROXY"
echo "  NO_PROXY: $NO_PROXY"
echo

# 停止现有容器
echo "Stopping existing containers..."
docker compose -f docker-compose.llm.yml down

# 构建镜像，传递代理参数
echo "Building image with proxy..."
docker compose -f docker-compose.llm.yml build \
  --build-arg HTTP_PROXY=$HTTP_PROXY \
  --build-arg HTTPS_PROXY=$HTTPS_PROXY \
  --build-arg NO_PROXY=$NO_PROXY \
  --no-cache

# 检查构建结果
if [ $? -eq 0 ]; then
    echo -e "\n✅ Build successful!"
    
    # 启动容器
    echo -e "\nStarting containers..."
    docker compose -f docker-compose.llm.yml up -d
    
    # 等待服务启动
    echo "Waiting for services to start..."
    sleep 10
    
    # 检查 Gemini CLI
    echo -e "\nChecking Gemini CLI installation:"
    docker exec pim-engine bash -c "which gemini || npx @google/gemini-cli --version 2>&1 | head -5"
else
    echo -e "\n❌ Build failed!"
    echo "Try running with explicit proxy settings:"
    echo "  export PROXY_HOST=your_proxy_host"
    echo "  export PROXY_PORT=your_proxy_port"
fi