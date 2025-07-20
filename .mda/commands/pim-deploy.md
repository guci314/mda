# /pim-deploy

## 描述
将PIM模型部署到执行引擎，实现业务逻辑的即时运行，无需代码生成和编译。

## 语法
```
/pim-deploy model=<PIM模型名> engine=<引擎地址> [version=<版本>] [env=<环境>]
```

## 参数
- `model` (必需): PIM模型文件名（不含路径和扩展名）
- `engine` (必需): 引擎地址或名称
- `version` (可选): 模型版本标签，默认为latest
- `env` (可选): 部署环境（dev/test/prod），默认为dev

## 功能说明

### 1. 部署流程

```mermaid
flowchart LR
    A[读取PIM模型] --> B[验证模型完整性]
    B --> C[转换为引擎格式]
    C --> D[上传到引擎]
    D --> E[引擎加载模型]
    E --> F[生成API端点]
    F --> G[启动健康检查]
    G --> H[部署完成]
```

### 2. 模型预处理

在部署前，自动进行以下处理：

#### 2.1 模型验证
```yaml
验证项目:
  - 实体定义完整性
  - 服务方法签名
  - 流程图语法正确
  - 业务规则可解析
  - 数据约束合法性
```

#### 2.2 格式转换
将Markdown格式的PIM转换为引擎可执行格式：

```json
{
  "domain": "订单管理",
  "version": "1.0.0",
  "entities": [
    {
      "name": "Order",
      "attributes": {
        "id": "string",
        "customer": "reference:Customer",
        "total": "decimal",
        "status": "enum:pending,paid,shipped,completed"
      },
      "constraints": [
        "total > 0",
        "status transitions follow order flow"
      ]
    }
  ],
  "services": [
    {
      "name": "OrderService",
      "methods": [
        {
          "name": "createOrder",
          "flow": "create-order-flow",
          "rules": [
            "validate customer exists",
            "check inventory availability",
            "calculate total with discounts"
          ]
        }
      ]
    }
  ],
  "flows": {
    "create-order-flow": {
      "steps": [...]
    }
  }
}
```

### 3. 引擎API调用

#### 3.1 上传模型
```http
POST /engine/models
Content-Type: application/json

{
  "name": "order-management",
  "version": "1.0.0",
  "content": { ... },
  "metadata": {
    "author": "business-analyst",
    "timestamp": "2024-01-20T10:00:00Z",
    "environment": "production"
  }
}
```

#### 3.2 激活模型
```http
POST /engine/models/order-management/activate
```

#### 3.3 验证部署
```http
GET /engine/models/order-management/status

Response:
{
  "status": "active",
  "endpoints": [
    "/api/v1/order",
    "/api/v1/order-service/create-order"
  ],
  "health": "healthy",
  "metrics": {
    "load_time": "230ms",
    "memory_usage": "45MB"
  }
}
```

### 4. 自动生成的功能

部署后，引擎自动提供：

#### 4.1 REST API
```bash
# 实体CRUD
GET    /api/v1/{entity}
POST   /api/v1/{entity}
GET    /api/v1/{entity}/{id}
PUT    /api/v1/{entity}/{id}
DELETE /api/v1/{entity}/{id}

# 服务方法
POST   /api/v1/{service}/{method}
```

#### 4.2 GraphQL Schema
```graphql
type Order {
  id: ID!
  customer: Customer!
  total: Float!
  status: OrderStatus!
}

type Query {
  order(id: ID!): Order
  orders(filter: OrderFilter): [Order!]!
}

type Mutation {
  createOrder(input: CreateOrderInput!): Order!
  updateOrder(id: ID!, input: UpdateOrderInput!): Order!
}
```

#### 4.3 WebSocket订阅
```javascript
// 订阅实体变更
ws.subscribe('order.created')
ws.subscribe('order.updated')
ws.subscribe('order.status.changed')
```

#### 4.4 管理界面
- 自动生成的CRUD界面：`/admin/{entity}`
- 流程调试器：`/debug/flows/{flow-name}`
- 业务仪表板：`/dashboard`

### 5. 部署选项

#### 5.1 蓝绿部署
```bash
# 部署到预发布环境
/pim-deploy model=订单管理_pim engine=prod version=v2.0 env=staging

# 验证后切换
/engine-switch engine=prod from=v1.0 to=v2.0
```

#### 5.2 金丝雀发布
```bash
# 部署新版本到部分流量
/pim-deploy model=订单管理_pim engine=prod version=v2.0 canary=10%
```

#### 5.3 A/B测试
```bash
# 部署实验版本
/pim-deploy model=订单管理_pim engine=prod version=experiment-1 ab-test=true
```

## 使用示例

### 基础部署
```bash
/pim-deploy model=用户管理_pim engine=http://localhost:8000
```

### 生产部署
```bash
/pim-deploy model=订单管理_pim engine=production version=v1.2.0 env=prod
```

### 多引擎部署
```bash
# 部署到多个地区
/pim-deploy model=商品管理_pim engine=asia-engine,europe-engine,us-engine
```

## 部署后验证

### 1. 自动测试
部署完成后自动运行：
- 健康检查
- API可用性测试
- 基础功能验证
- 性能基准测试

### 2. 手动验证
```bash
# 查看部署状态
/engine-status engine=production model=订单管理

# 运行业务测试
/pim-test model=订单管理 scenario=创建订单

# 查看实时日志
/engine-logs engine=production model=订单管理
```

## 回滚机制

如果部署出现问题：

```bash
# 自动回滚到上一版本
/pim-rollback model=订单管理_pim engine=production

# 回滚到指定版本
/pim-rollback model=订单管理_pim engine=production version=v1.1.0
```

## 监控和告警

部署后自动配置：

1. **性能监控**
   - API响应时间
   - 资源使用率
   - 并发请求数
   - 错误率

2. **业务监控**
   - 业务规则执行次数
   - 流程完成率
   - 数据操作统计

3. **告警规则**
   - 错误率超过阈值
   - 响应时间过长
   - 资源使用异常
   - 业务规则失败

## 配置示例

```yaml
# .mda/deploy-config.yml
deployment:
  default_engine: production
  
  environments:
    dev:
      engine: http://dev-engine:8000
      auto_deploy: true
      health_check_interval: 10s
      
    test:
      engine: http://test-engine:8000
      require_approval: false
      run_tests: true
      
    prod:
      engine: http://prod-engine:8000
      require_approval: true
      canary_percentage: 10
      rollback_on_error: true
      
  validation:
    strict_mode: true
    test_coverage_required: 80
    
  monitoring:
    enable_metrics: true
    alert_webhook: https://alerts.company.com
```

## 注意事项

1. **模型兼容性**：确保PIM模型格式正确
2. **版本管理**：使用语义化版本号
3. **环境隔离**：不同环境使用不同引擎实例
4. **监控告警**：配置适当的监控和告警

## 相关命令
- `/engine-deploy`: 部署PIM执行引擎
- `/pim-validate`: 验证模型正确性
- `/pim-test`: 测试部署的模型
- `/pim-rollback`: 回滚模型版本