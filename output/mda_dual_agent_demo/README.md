# 图书借阅系统 API

基于 FastAPI 的图书借阅系统后端服务。

## 快速开始

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 启动服务：`uvicorn main:app --reload`

## 环境变量

复制 `.env.example` 为 `.env` 并配置数据库连接。

## Docker 运行

```bash
docker-compose up --build
```

## API 文档

访问 `http://localhost:8000/docs` 查看交互式 API 文档。