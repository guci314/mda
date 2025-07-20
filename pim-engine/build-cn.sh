#!/bin/bash

echo "=== 使用中国镜像构建 PIM Engine ==="
echo

# 使用中国镜像的 Dockerfile
echo "使用淘宝 npm 镜像加速构建..."

# 备份原 Dockerfile
cp Dockerfile.llm Dockerfile.llm.bak

# 使用中国镜像版本
cp Dockerfile.llm.cn Dockerfile.llm

# 构建
docker compose -f docker-compose.llm.yml build --no-cache

# 恢复原 Dockerfile
mv Dockerfile.llm.bak Dockerfile.llm

echo "构建完成！"