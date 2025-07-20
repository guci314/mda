# /mda-generate-fastapi Slash Command for Claude Code

## 命令定义
```
/mda-generate-fastapi domain=<领域名> service=<服务名> [output=<输出目录>]
```

## 执行指令

当用户执行此命令时，请按以下步骤操作：

### 1. 读取和理解领域模型（PSM）

```
1. 读取 models/domain/{domain}.md 文件
2. 深入理解：
   - 业务描述的含义和目的
   - Mermaid图中的实体关系
   - 业务规则的具体要求
   - API设计意图
   - 性能和安全需求
```

### 2. 智能代码生成

基于对模型的理解，生成定制化的FastAPI代码：

#### 2.1 项目结构
```
{service}/
├── app/
│   ├── __init__.py
│   ├── main.py              # 考虑服务特点定制
│   ├── models/
│   │   ├── domain.py        # 基于业务理解生成
│   │   └── database.py      # 优化的数据模型
│   ├── api/
│   │   ├── routes.py        # RESTful或其他合适的API风格
│   │   └── dependencies.py  # 智能依赖注入
│   ├── services/
│   │   └── {domain}_service.py  # 业务逻辑实现
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py      # 基于安全需求定制
│   │   └── database.py
│   ├── utils/               # 根据需要添加工具函数
│   └── debug/               # 流程调试器（仅当有可调试方法时）
│       ├── flow_debugger.py
│       ├── flow_models.py
│       ├── debug_routes.py
│       ├── decorators.py
│       └── static/
├── tests/                   # 生成有意义的测试
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

#### 2.2 代码生成原则

**不要使用固定模板**，而是：

1. **理解业务语境**
   - 用户管理 → 需要认证、授权、会话管理
   - 订单系统 → 需要事务、状态机、并发控制
   - 支付流程 → 需要安全加密、审计日志、幂等性

2. **智能决策**
   - 选择合适的认证方式（JWT、OAuth2、API Key）
   - 决定是否需要缓存（Redis）
   - 判断是否需要消息队列（RabbitMQ、Kafka）
   - 选择合适的数据库索引策略

3. **生成高质量代码**
   ```python
   # 示例：基于理解生成的验证逻辑
   # 而不是模板化的代码
   
   @validator('email')
   def validate_email_uniqueness(cls, v, values, **kwargs):
       """
       基于业务规则"用户邮箱必须唯一"生成
       考虑了性能（使用索引）和用户体验（友好错误信息）
       """
       # 智能生成的代码，不是模板
   ```

#### 2.3 特殊处理

根据领域特点添加特定功能：

- **用户管理**：
  - 密码加密（bcrypt）
  - 邮箱验证流程
  - 权限中间件
  - 登录限流

- **订单系统**：
  - 分布式事务
  - 库存锁定
  - 状态机实现
  - 事件发布

- **支付流程**：
  - 支付网关集成
  - 加密传输
  - 审计日志
  - 回调处理

- **包含流程图的方法**：
  - 生成流程调试器
  - 提供 /debug/ui 界面
  - WebSocket实时执行追踪
  - 支持断点和单步调试

### 3. 代码标记系统

生成的代码使用智能标记：

```python
# MDA-GENERATED-START: {context}
# 生成时间: {timestamp}
# 基于模型: {model_path}
# 理解要点: {key_insights}
... 生成的代码 ...
# MDA-GENERATED-END: {context}

# MDA-CUSTOM-START: {feature}
# 用户自定义代码区域
# MDA-CUSTOM-END: {feature}
```

### 4. 自动测试和验证

生成代码后，自动执行以下验证流程：

#### 4.1 环境准备和依赖安装
```bash
cd {output_path}
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx  # 测试依赖
```

#### 4.2 运行单元测试
```bash
# 运行所有测试
pytest tests/ -v

# 如果测试失败：
# 1. 分析失败原因
# 2. 修复代码问题
# 3. 重新运行测试
```

#### 4.3 Docker部署验证
```bash
# 构建并启动服务
docker compose up -d

# 等待服务完全启动
sleep 10

# 验证健康检查
curl --noproxy localhost http://localhost:8000/health

# 验证API文档可访问
curl --noproxy localhost http://localhost:8000/docs

# 如果验证失败，分析日志并修复
docker compose logs
```

#### 4.4 功能验证
- 测试基础CRUD操作
- 验证认证系统工作正常
- 检查数据库连接和迁移
- 确认Redis缓存功能
- 测试关键业务流程

### 5. 输出和反馈

完成所有验证后：
1. 显示生成的文件列表
2. 报告测试结果（✅ 通过 / ❌ 失败）
3. 解释关键设计决策
4. 提供服务访问信息：
   - API文档：http://localhost:8000/docs
   - 健康检查：http://localhost:8000/health
   - 调试界面：http://localhost:8000/debug/ui（如果有可调试方法）
   - 管理界面：http://localhost:8000/admin（如果有）
5. 询问是否需要调整或优化

## 生成示例

### 用户输入
```
/mda-generate-fastapi domain=用户管理_psm service=user-service
```

### Claude的理解和生成过程

1. **理解阶段**
   - "这是一个用户管理系统，需要处理认证、授权、用户信息管理"
   - "有复杂的角色权限体系，需要RBAC实现"
   - "要求高性能（10000并发）和安全性"

2. **决策阶段**
   - "使用JWT进行无状态认证"
   - "使用Redis缓存会话和权限信息"
   - "实现登录失败锁定机制"
   - "添加审计日志"

3. **生成阶段**
   - 不是填充模板，而是基于理解生成适合的代码
   - 包含业务特定的优化
   - 考虑实际部署需求

## 注意事项

1. **保持灵活性**：根据不同的业务需求生成不同的代码结构
2. **质量优先**：生成生产级代码，不是示例代码
3. **可维护性**：清晰的代码组织和充分的注释
4. **性能考虑**：基于需求添加适当的优化
5. **安全第一**：默认包含必要的安全措施

## 与其他命令的协作

- `/mda-update`：理解代码变更，智能合并
- `/mda-reverse`：从代码理解业务逻辑并更新模型
- `/mda-validate`：验证代码是否符合模型意图
- `/mda-troubleshooting`：查看故障排查指南

## 重要实现细节（基于经验教训）

### 流程调试器实现

当PIM中的方法包含流程图时，生成调试器时注意：

1. **Mermaid图表生成**
```python
# 正确：直接返回flowchart内容
def generate_mermaid_diagram(flow):
    lines = ["flowchart TD"]
    # 不要包含 ```mermaid 包装！
```

2. **DateTime JSON序列化**
```python
# 方案1：Pydantic配置
class Config:
    json_encoders = {
        datetime: lambda v: v.isoformat()
    }

# 方案2：使用model_dump
session.model_dump(mode='json')

# 方案3：自定义WebSocket消息发送
async def send_json_with_datetime(websocket, data):
    json_str = json.dumps(data, cls=DateTimeEncoder)
    await websocket.send_text(json_str)
```

3. **WebSocket状态同步**
```python
# 设置回调机制
async def on_state_change(event_type, data):
    await send_json_with_datetime(websocket, {
        "type": event_type,
        "data": data,
        "session": session.model_dump(mode='json')
    })

executor.on_state_change = on_state_change
```

4. **Docker配置**
```yaml
# 确保数据库健康检查
depends_on:
  postgres:
    condition: service_healthy

# 固定容器名避免解析问题
container_name: user-postgres
```

5. **环境变量配置**
```python
class Config:
    env_file = ".env"
    extra = "allow"  # 避免额外字段导致启动失败
```

### 常见问题预防

1. **"Syntax error in text"** - Mermaid渲染错误
   - 确保不包含markdown代码块标记

2. **"Object of type datetime is not JSON serializable"**
   - 使用上述三种方案之一处理datetime

3. **点击Start无反应**
   - 确保执行器有状态变化回调机制
   - 检查WebSocket消息类型处理

4. **Docker连接失败**
   - 使用健康检查确保启动顺序
   - 创建.env文件配置数据库连接

5. **CDN资源无法访问**（中国地区）
   - 使用 unpkg.com 替代 cdn.jsdelivr.net
   - 或使用国内CDN如 bootcdn.net
   - 避免使用被墙的CDN服务