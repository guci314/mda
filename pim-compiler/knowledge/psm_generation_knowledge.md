# PSM 生成知识库

## PSM 文档章节结构

PSM（Platform Specific Model）文档应该包含以下五个核心章节：

### 1. Domain Models（领域模型）
**目的**：定义系统的数据结构和领域对象

**必须包含**：
- Entity Definitions（实体定义）：使用纯 Python 类定义领域对象
- Database Models（数据库模型）：使用 SQLAlchemy 2.0 定义 ORM 模型
- Pydantic Schemas（验证模型）：定义请求/响应的数据验证模型
  - `{Entity}Create`：创建时的输入模型
  - `{Entity}Update`：更新时的输入模型
  - `{Entity}Response`：响应输出模型
  - `{Entity}Query`：查询参数模型
- Enums and Constants（枚举和常量）：定义业务常量和枚举类型

**代码规范**：
```python
# 实体定义示例
class User:
    """用户领域实体"""
    def __init__(self, ...):
        self.id = id or uuid4()
        
# SQLAlchemy 模型示例
class UserDB(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
# Pydantic 模型示例
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
```

### 2. Service Layer（服务层）
**目的**：实现业务逻辑和数据访问

**必须包含**：
- Business Services（业务服务）：实现核心业务逻辑
  - 每个实体对应一个 Service 类
  - 使用依赖注入获取数据库会话
  - 所有方法使用 async/await
- Repository Pattern（仓储模式）：封装数据访问逻辑
  - 抽象接口定义
  - 具体实现类
- Transaction Management（事务管理）：处理数据库事务
- Business Rules（业务规则）：实现业务约束和验证

**代码规范**：
```python
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        # 业务逻辑实现
        pass
```

### 3. REST API Design（API 设计）
**目的**：定义 RESTful API 接口

**必须包含**：
- API Endpoints（端点定义）：遵循 RESTful 规范
  - GET /api/{resource} - 列表查询
  - GET /api/{resource}/{id} - 单个查询
  - POST /api/{resource} - 创建
  - PUT /api/{resource}/{id} - 更新
  - DELETE /api/{resource}/{id} - 删除
- Request/Response Models（请求响应模型）：API 数据格式
- API Routing（路由配置）：FastAPI 路由组织
- Middleware（中间件）：认证、日志、错误处理

**代码规范**：
```python
router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(user_data)
```

### 4. Application Configuration（应用配置）
**目的**：配置应用程序和基础设施

**必须包含**：
- Main Application（主应用）：FastAPI 应用初始化
- Database Configuration（数据库配置）：连接池、会话管理
- Dependency Injection（依赖注入）：服务和仓储的注入配置
- Environment Settings（环境配置）：配置管理
- Startup/Shutdown Events（启动关闭事件）：应用生命周期

**代码规范**：
```python
app = FastAPI(title="User Management API")

@app.on_event("startup")
async def startup_event():
    # 初始化数据库等
    pass
```

### 5. Testing Specifications（测试规范）
**目的**：定义测试策略和测试用例

**必须包含**：
- Unit Tests（单元测试）：服务层和工具函数测试
- Integration Tests（集成测试）：API 端点测试
- Test Fixtures（测试夹具）：测试数据和模拟对象
- Test Configuration（测试配置）：测试数据库和环境

**代码规范**：
```python
@pytest.mark.asyncio
async def test_create_user(client: TestClient):
    response = await client.post("/api/users", json={...})
    assert response.status_code == 201
```

## FastAPI 平台特定知识

### 技术栈
- **框架**：FastAPI (最新版本)
- **ORM**：SQLAlchemy 2.0 (使用异步)
- **数据库**：PostgreSQL
- **验证**：Pydantic v2
- **测试**：pytest + httpx
- **异步**：全面使用 async/await

### 最佳实践

#### 1. 依赖注入
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)
```

#### 2. 错误处理
```python
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

#### 3. 异步 SQLAlchemy
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

engine = create_async_engine("postgresql+asyncpg://...")
async_session = sessionmaker(engine, class_=AsyncSession)
```

#### 4. Pydantic v2 特性
```python
from pydantic import BaseModel, ConfigDict, field_validator

class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # 自定义验证
        return v
```

#### 5. API 版本控制
```python
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(users_router)
app.include_router(v1_router)
```

### 代码组织结构
```
src/
├── api/
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── deps.py
├── core/
│   ├── config.py
│   └── security.py
├── db/
│   ├── base.py
│   └── session.py
├── models/
│   ├── __init__.py
│   └── user.py
├── schemas/
│   ├── __init__.py
│   └── user.py
├── services/
│   ├── __init__.py
│   └── user_service.py
├── repositories/
│   ├── __init__.py
│   └── user_repository.py
└── main.py
```

### 命名规范
- 类名：PascalCase（如 `UserService`）
- 函数名：snake_case（如 `get_user_by_id`）
- 常量：UPPER_SNAKE_CASE（如 `MAX_RETRY_COUNT`）
- 文件名：snake_case（如 `user_service.py`）

### 注释规范
- 所有类和方法必须有 docstring
- 使用中文注释说明业务逻辑
- 复杂逻辑必须添加行内注释

## 生成指导原则

1. **完整性**：每个章节的代码必须是完整的、可运行的
2. **一致性**：所有章节使用相同的命名和编码规范
3. **专业性**：遵循 FastAPI 和 Python 最佳实践
4. **可测试性**：所有代码都应该易于测试
5. **文档化**：包含充分的注释和文档字符串

## 章节依赖关系

生成顺序应该遵循依赖关系：
1. Domain Models（无依赖）
2. Service Layer（依赖 Domain Models）
3. REST API Design（依赖 Service Layer 和 Domain Models）
4. Application Configuration（依赖所有其他章节）
5. Testing Specifications（依赖所有其他章节）

每个后续章节可以引用前面章节中定义的类和接口。