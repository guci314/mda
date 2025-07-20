# /engine-deploy

部署PIM执行引擎的命令实现，创建一个可以运行所有PIM模型的通用引擎实例。

## 执行步骤

当用户执行此命令时：

### 1. 创建部署目录
```bash
mkdir -p pim-engine-{name}
cd pim-engine-{name}
```

### 2. 生成引擎镜像Dockerfile

创建 `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制引擎代码
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pim_engine/ ./pim_engine/
COPY config/ ./config/

# 创建必要目录
RUN mkdir -p /app/models /app/data /app/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "pim_engine.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. 生成requirements.txt
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
sqlalchemy==2.0.25
asyncpg==0.29.0
redis==5.0.1
httpx==0.26.0
pyyaml==6.0.1
python-multipart==0.0.6
prometheus-client==0.19.0
opentelemetry-api==1.22.0
opentelemetry-sdk==1.22.0
anthropic==0.8.0
```

### 4. 生成docker-compose.yml

根据用户参数生成完整的Docker Compose配置。

### 5. 生成引擎配置文件

创建 `config/engine.yml` 配置文件。

### 6. 构建和启动引擎

```bash
# 构建镜像
docker build -t pim-engine:latest .

# 启动服务
docker compose up -d

# 等待服务就绪
sleep 10

# 验证部署
curl http://localhost:{port}/health
```

### 7. 输出部署信息

```
✅ PIM执行引擎部署成功！

引擎信息：
- 名称: {name}
- 地址: http://localhost:{port}
- 状态: 运行中
- 版本: 1.0.0

管理端点：
- API文档: http://localhost:{port}/docs
- 健康检查: http://localhost:{port}/health
- 引擎状态: http://localhost:{port}/engine/status
- 监控面板: http://localhost:3000 (Grafana)

下一步：
1. 部署PIM模型: /pim-deploy model=your_model engine={name}
2. 查看引擎状态: /engine-status name={name}
3. 查看引擎日志: docker logs {name}
```

## 错误处理

- 端口冲突：提示更换端口
- Docker未安装：提供安装指引
- 资源不足：显示最低要求

## 实现要点

1. 使用模板生成所有配置文件
2. 自动处理环境变量和密钥
3. 确保所有服务正确启动
4. 提供清晰的错误信息