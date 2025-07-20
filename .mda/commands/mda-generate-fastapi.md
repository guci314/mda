# /mda-generate-fastapi

## 描述
从领域模型（当前为PSM - Platform Specific Model）生成完整的FastAPI微服务代码。

## 语法
```
/mda-generate-fastapi domain=<领域名称> service=<服务名> [output=<输出目录>]
```

## 参数
- `domain` (必需): 领域模型文件名称，对应models/domain/目录下的.md文件名（不含扩展名）
- `service` (必需): 生成的微服务名称
- `output` (可选): 输出目录路径，默认为./services/<service>

## 功能说明

### 1. 模型解析
- 读取指定的领域模型文件（PSM）
- 解析Mermaid类图获取实体结构
- 提取业务规则和API设计意图
- 识别实体间的关系

### 2. 代码生成内容

#### 项目结构
```
<service-name>/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── models/
│   │   ├── __init__.py
│   │   ├── domain.py        # Pydantic模型
│   │   └── database.py      # SQLAlchemy模型
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py        # API路由
│   │   └── dependencies.py  # 依赖注入
│   ├── services/
│   │   ├── __init__.py
│   │   └── <domain>_service.py  # 业务逻辑
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # 配置管理
│   │   ├── security.py      # 安全相关
│   │   └── database.py      # 数据库连接
│   ├── utils/
│   │   ├── __init__.py
│   │   └── validators.py    # 自定义验证器
│   └── debug/               # 流程调试器模块
│       ├── __init__.py
│       ├── flow_debugger.py # 调试器核心
│       ├── flow_models.py   # 流程模型定义
│       ├── debug_routes.py  # 调试API路由
│       ├── decorators.py    # 流程装饰器
│       ├── middleware.py    # 调试中间件
│       └── static/          # 调试界面
│           ├── index.html
│           ├── debugger.js
│           └── debugger.css
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services.py
├── alembic/                 # 数据库迁移
│   ├── alembic.ini
│   └── versions/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

#### 生成的代码特性
- **Pydantic模型**: 包含请求/响应模型，自动验证
- **SQLAlchemy ORM**: 数据库实体映射
- **FastAPI路由**: RESTful API端点
- **Service层**: 业务逻辑实现
- **依赖注入**: 数据库会话管理
- **配置管理**: 环境变量和配置文件
- **Docker支持**: 容器化部署配置
- **测试框架**: pytest基础测试
- **流程调试器**: 可视化业务流程调试（仅限标记为可调试的方法）

### 3. 智能生成特性

#### 自动推断
- CRUD操作：为每个实体生成标准的增删改查API
- 关联查询：基于实体关系生成关联数据获取接口
- 分页支持：列表接口自动添加分页参数
- 过滤排序：支持字段过滤和排序

#### 业务规则映射
- 字段验证：将业务规则转换为Pydantic验证器
- 权限控制：基于角色的访问控制实现
- 业务逻辑：在Service层实现复杂业务规则

#### 代码质量
- 类型注解：完整的Python类型提示
- 文档字符串：自动生成API文档
- 错误处理：统一的异常处理机制
- 日志记录：结构化日志输出

### 4. 自动测试和验证

生成代码后，Claude Code会自动执行以下验证步骤：

#### 单元测试
1. 安装测试依赖：`pip install pytest pytest-asyncio httpx`
2. 运行单元测试：`pytest tests/ -v`
3. 确保所有测试通过

#### Docker部署验证
1. 构建并启动容器：`docker compose up -d`
2. 等待服务启动完成
3. 执行健康检查：`curl --noproxy localhost http://localhost:8000/health`
4. 验证API文档可访问：`curl --noproxy localhost http://localhost:8000/docs`

#### 功能验证
1. 测试基础API端点
2. 验证数据库连接
3. 检查Redis缓存功能
4. 确认认证系统工作正常

如果任何测试失败，Claude Code会：
- 分析错误原因
- 自动修复常见问题
- 重新运行测试直到通过

## 使用示例

### 基础使用
```bash
/mda-generate-fastapi domain=用户管理_psm service=user-service
```

### 指定输出目录
```bash
/mda-generate-fastapi domain=订单系统 service=order-service output=./microservices/order
```

### 生成后的自动流程

生成代码后，Claude Code会自动执行以下步骤：

1. **环境准备**
   ```bash
   cd services/<service-name>
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **单元测试**
   ```bash
   pip install pytest pytest-asyncio httpx
   pytest tests/ -v
   ```

3. **Docker部署**
   ```bash
   docker compose up -d
   # 等待服务启动
   sleep 10
   ```

4. **服务验证**
   ```bash
   # 健康检查
   curl --noproxy localhost http://localhost:8000/health
   # API文档检查
   curl --noproxy localhost http://localhost:8000/docs
   ```

5. **清理（如果需要）**
   ```bash
   docker compose down
   ```

### 手动启动（如果需要）
```bash
cd services/user-service
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件设置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload
```

## 配置选项

在`.mda/config.yml`中可以配置生成选项：

```yaml
generation:
  # API风格配置
  api:
    prefix: /api/v1
    style: restful  # restful | graphql
    
  # 数据库配置
  database:
    orm: sqlalchemy  # sqlalchemy | tortoise-orm
    driver: postgresql  # postgresql | mysql | sqlite
    
  # 认证配置
  auth:
    type: jwt  # jwt | oauth2 | api-key
    
  # 特性开关
  features:
    pagination: true
    sorting: true
    filtering: true
    validation: true
    cors: true
    rate_limiting: true
    caching: false
```

## 注意事项

1. **模型文件要求**
   - 必须包含完整的Mermaid类图
   - 实体必须有明确的属性和类型
   - 建议包含业务规则说明

2. **命名规范**
   - 服务名使用kebab-case（如user-service）
   - 实体名使用PascalCase（如UserProfile）
   - 属性名使用camelCase（如firstName）

3. **依赖管理**
   - 生成的requirements.txt包含所有必需依赖
   - 建议使用虚拟环境隔离项目依赖

4. **数据库支持**
   - 默认使用PostgreSQL
   - 支持MySQL和SQLite
   - 需要手动创建数据库

## 常见问题和解决方案

### 1. ASGI中间件实现问题
当使用FastAPI的`app.add_middleware()`时，中间件类需要正确处理ASGI调用约定：

**问题**：`TypeError: RateLimitMiddleware.__call__() takes 3 positional arguments but 4 were given`

**原因**：FastAPI会以两种方式调用中间件：
1. 初始化时：`middleware_class(app)`
2. 请求时：`middleware_instance(scope, receive, send)`

**解决方案**：
```python
class RateLimitMiddleware:
    def __init__(self, app=None, rate_limiter: RateLimiter = None):
        self.app = app
        self.rate_limiter = rate_limiter or default_rate_limiter
    
    async def __call__(self, scope, receive, send):
        # 如果是通过add_middleware调用，app会通过第一个参数传入
        if self.app is None and callable(scope):
            self.app = scope
            return self
        
        # 正常的ASGI处理
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # 中间件逻辑...
```

### 2. Pydantic v2兼容性
生成的代码需要适配Pydantic v2的变化：
- `BaseSettings`从`pydantic`移到`pydantic_settings`
- `Field`的`regex`参数改为`pattern`
- 配置类的`orm_mode`改为`from_attributes`

### 3. SQLAlchemy保留字
避免使用SQLAlchemy的保留字作为字段名：
- `metadata` → `activity_metadata`或其他名称

### 4. Docker Compose v2
使用新的命令格式：
- `docker compose up -d` (不是 `docker-compose up -d`)

### 5. 流程调试器实现

对于PIM中包含流程图的方法，自动生成可视化调试器：

#### 调试器核心组件

1. **流程模型定义** (`flow_models.py`)
```python
from datetime import datetime
from pydantic import BaseModel

class FlowStep(BaseModel):
    id: str
    name: str
    step_type: StepType  # validation, action, decision
    next_steps: List[str]

class DebugSession(BaseModel):
    id: str
    flow_name: str
    status: str = "idle"
    created_at: datetime
    current_step: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

2. **装饰器标记可调试方法** (`decorators.py`)
```python
@flow(name="创建用户流程", description="处理用户注册的完整流程")
async def create_user(user_data: UserCreate) -> User:
    @step(name="验证用户数据", step_type="validation")
    async def validate_data():
        # 验证逻辑
        pass
```

3. **调试路由实现** (`debug_routes.py`)

**重要经验教训**：
- WebSocket消息必须处理datetime序列化
- 使用自定义JSON编码器或`model_dump(mode='json')`
- 实现状态变化回调机制

```python
# 自定义JSON编码器处理datetime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def send_json_with_datetime(websocket: WebSocket, data: dict):
    json_str = json.dumps(data, cls=DateTimeEncoder)
    await websocket.send_text(json_str)

# WebSocket处理
@router.websocket("/sessions/{session_id}/ws")
async def debug_websocket(websocket: WebSocket, session_id: str):
    # 设置执行器回调
    async def on_state_change(event_type: str, data: dict):
        await send_json_with_datetime(websocket, {
            "type": event_type,
            "data": data,
            "session": session.model_dump(mode='json')
        })
    
    debugger.set_executor_callback(session_id, on_state_change)
```

4. **Mermaid图表生成**

**重要**：不要包含markdown包装
```python
def generate_mermaid_diagram(flow: BusinessFlow) -> str:
    lines = ["flowchart TD"]  # 直接开始，无```mermaid包装
    lines.append('    Start([开始])')
    # ... 添加节点和边
    return "\n".join(lines)
```

5. **前端集成** (`main.py`)
```python
# 挂载调试路由
app.include_router(debug_routes.router, prefix="/debug", tags=["debug"])

# 挂载静态文件
app.mount("/debug-ui", StaticFiles(directory="app/debug/static"), name="debug-ui")

# 服务端点
@app.get("/")
async def root():
    return {
        "endpoints": {
            "api_docs": "/docs",
            "debug": "/debug",      # 调试器入口
            "debug_ui": "/debug/ui" # 调试界面
        }
    }
```

6. **JavaScript客户端处理**
```javascript
// 处理不同的事件类型
handleWebSocketMessage(data) {
    switch (data.type) {
        case 'execution_started':
            this.status = 'running';
            break;
        case 'step_started':
            this.currentStep = data.data.step_id;
            this.highlightCurrentStep();
            break;
        case 'step_completed':
            // 更新历史记录
            break;
        case 'execution_completed':
            this.status = 'completed';
            break;
    }
}
```

**重要：CDN资源引用**
```html
<!-- 使用国内可访问的CDN -->
<script src="https://unpkg.com/mermaid/dist/mermaid.min.js"></script>
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>

<!-- 或使用 bootcdn -->
<script src="https://cdn.bootcdn.net/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>
<script src="https://cdn.bootcdn.net/ajax/libs/vue/3.4.15/vue.global.js"></script>
```

#### Docker配置注意事项

1. **数据库连接**
```yaml
services:
  postgres:
    container_name: user-postgres  # 固定容器名
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      
  user-service:
    depends_on:
      postgres:
        condition: service_healthy  # 等待数据库就绪
```

2. **环境变量处理**
```python
class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}..."
    
    class Config:
        env_file = ".env"
        extra = "allow"  # 允许额外字段避免启动错误
```

#### 常见问题解决

1. **"Syntax error in text" (Mermaid)**
   - 原因：图表包含markdown包装
   - 解决：直接返回flowchart内容

2. **"Object of type datetime is not JSON serializable"**
   - 原因：WebSocket发送datetime对象
   - 解决：使用`model_dump(mode='json')`或自定义编码器

3. **点击Start无反应**
   - 原因：执行器未发送状态更新
   - 解决：实现回调机制通知WebSocket

4. **Docker连接失败**
   - 原因：容器名解析或启动顺序问题
   - 解决：使用健康检查和固定容器名

## 相关命令
- `/mda-update`: 更新已生成的代码
- `/mda-reverse`: 从代码反向生成模型
- `/mda-validate`: 验证模型和代码一致性
- `/mda-troubleshooting`: 查看故障排查指南