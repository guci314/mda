# /engine-deploy

## 描述
部署PIM执行引擎，一次性部署可运行所有业务模型的通用引擎。

## 语法
```
/engine-deploy name=<引擎名称> [port=<端口>] [config=<配置文件>]
```

## 参数
- `name` (必需): 引擎实例名称
- `port` (可选): 服务端口，默认8000
- `config` (可选): 引擎配置文件路径

## 功能说明

### 1. 引擎部署内容

部署一个包含所有微服务基础设施的PIM执行引擎：

```
PIM执行引擎
├── 核心组件
│   ├── 模型加载器（热加载PIM）
│   ├── 规则引擎（LLM驱动）
│   ├── 流程引擎（执行业务流程）
│   ├── 数据引擎（统一数据操作）
│   └── UI引擎（动态生成界面）
├── 基础设施
│   ├── 日志系统
│   ├── 限流/熔断
│   ├── 认证授权
│   ├── 服务发现
│   ├── 调试器
│   └── 监控告警
└── API网关
    ├── REST API
    ├── GraphQL
    └── WebSocket
```

### 2. Docker Compose配置

```yaml
version: '3.8'

services:
  pim-engine:
    image: pim-engine:latest
    container_name: ${name}
    ports:
      - "${port}:8000"
    environment:
      - ENGINE_NAME=${name}
      - LOG_LEVEL=INFO
      - LLM_API_KEY=${LLM_API_KEY}
    volumes:
      - ./models:/app/models
      - ./config:/app/config
      - pim-data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: pim_engine
      POSTGRES_USER: pim
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pim"]
      
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards

volumes:
  pim-data:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:
```

### 3. 引擎配置

```yaml
# config/engine.yml
engine:
  name: ${name}
  version: 1.0.0
  
  # 模型加载配置
  model_loader:
    path: /app/models
    hot_reload: true
    reload_interval: 5s
    
  # LLM配置
  llm:
    provider: anthropic
    model: claude-3-sonnet
    temperature: 0.3
    
  # 规则引擎配置
  rule_engine:
    cache_size: 1000
    cache_ttl: 3600
    parallel_execution: true
    
  # 数据引擎配置
  data_engine:
    connection_pool_size: 20
    query_timeout: 30s
    transaction_timeout: 60s
    
  # API配置
  api:
    rest:
      enabled: true
      prefix: /api/v1
      rate_limit: 1000/min
    graphql:
      enabled: true
      path: /graphql
      playground: true
    websocket:
      enabled: true
      path: /ws
      
  # 安全配置
  security:
    auth:
      type: jwt
      secret: ${JWT_SECRET}
      expiry: 24h
    cors:
      enabled: true
      origins: ["*"]
    rate_limiting:
      enabled: true
      default: 100/min
      
  # 监控配置
  monitoring:
    metrics:
      enabled: true
      path: /metrics
    tracing:
      enabled: true
      jaeger_endpoint: http://jaeger:14268
    logging:
      level: INFO
      format: json
```

### 4. 部署步骤

1. **生成部署文件**
   ```bash
   mkdir pim-engine-${name}
   cd pim-engine-${name}
   
   # 生成docker-compose.yml
   # 生成配置文件
   # 生成监控配置
   ```

2. **启动引擎**
   ```bash
   docker compose up -d
   ```

3. **验证部署**
   ```bash
   # 健康检查
   curl http://localhost:${port}/health
   
   # 引擎状态
   curl http://localhost:${port}/engine/status
   
   # API文档
   curl http://localhost:${port}/docs
   ```

4. **配置监控**
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090
   - 日志聚合: 通过ELK或Loki

## 使用示例

### 基础部署
```bash
/engine-deploy name=production-engine
```

### 自定义端口
```bash
/engine-deploy name=test-engine port=8080
```

### 使用配置文件
```bash
/engine-deploy name=prod-engine config=./prod-config.yml
```

## 部署后操作

1. **加载模型**
   ```bash
   /pim-deploy model=订单管理_pim engine=production-engine
   ```

2. **查看状态**
   ```bash
   /engine-status name=production-engine
   ```

3. **查看日志**
   ```bash
   docker logs production-engine -f
   ```

## 高可用部署

对于生产环境，支持集群部署：

```yaml
# ha-deployment.yml
services:
  pim-engine-1:
    extends:
      service: pim-engine
    container_name: ${name}-1
    
  pim-engine-2:
    extends:
      service: pim-engine
    container_name: ${name}-2
    
  pim-engine-3:
    extends:
      service: pim-engine
    container_name: ${name}-3
    
  nginx:
    image: nginx
    ports:
      - "${port}:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - pim-engine-1
      - pim-engine-2
      - pim-engine-3
```

## 维护操作

### 更新引擎
```bash
# 拉取最新镜像
docker pull pim-engine:latest

# 滚动更新
docker compose up -d --no-deps pim-engine
```

### 备份数据
```bash
# 备份数据库
docker exec postgres pg_dump -U pim pim_engine > backup.sql

# 备份模型
tar -czf models-backup.tar.gz ./models
```

### 性能调优
```bash
# 调整资源限制
docker update --cpus="4" --memory="8g" production-engine
```

## 注意事项

1. **资源需求**
   - CPU: 最少2核，推荐4核
   - 内存: 最少4GB，推荐8GB
   - 存储: 根据数据量调整

2. **安全考虑**
   - 修改默认密码
   - 配置防火墙规则
   - 启用HTTPS

3. **监控告警**
   - 配置告警规则
   - 设置自动伸缩
   - 定期查看性能指标

## 相关命令
- `/pim-deploy`: 部署PIM模型到引擎
- `/engine-status`: 查看引擎状态
- `/engine-scale`: 扩缩容引擎实例
- `/engine-update`: 更新引擎版本