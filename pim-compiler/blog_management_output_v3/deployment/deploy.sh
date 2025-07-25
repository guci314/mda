#!/bin/bash

# 构建Docker镜像
docker build -t blog-management .

# 运行容器
docker run -d     -p 8000:8000     -e DB_HOST=\$DB_HOST     -e DB_NAME=\$DB_NAME     -e DB_USER=\$DB_USER     -e DB_PASSWORD=\$DB_PASSWORD     --name blog_management     blog-management
