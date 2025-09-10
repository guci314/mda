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
        
# SQLAlchemy 模型示例（SQLite兼容）
class UserDB(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))  # SQLite使用String存储UUID
    
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
  - 使用同步方法，简化实现
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
    
    def register_user(self, user_data: UserCreate) -> UserResponse:
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
def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return service.create_user(user_data)
```

### 4. Application Configuration（应用配置）
**目的**：配置应用程序和基础设施

**必须包含**：
- Main Application（主应用）：FastAPI 应用初始化
- Database Configuration（数据库配置）：SQLite连接、会话管理
- Dependency Injection（依赖注入）：服务和仓储的注入配置
- Environment Settings（环境配置）：配置管理
- Startup/Shutdown Events（启动关闭事件）：应用生命周期

**代码规范**：
```python
app = FastAPI(title="User Management API")

@app.on_event("startup")
def startup_event():
    # 初始化数据库等
    Base.metadata.create_all(bind=engine)
```

### 5. Testing Specifications（测试规范）
**目的**：定义测试策略和测试用例（基于unittest框架）

**必须包含**：
- Unit Tests（单元测试）：使用unittest.TestCase和Mock对象测试服务层
- Integration Tests（集成测试）：使用TestClient测试API端点
- Test Fixtures（测试夹具）：setUp/tearDown方法准备测试数据
- Test Configuration（测试配置）：测试数据库和环境配置
- Test Utilities（测试工具）：辅助函数和测试数据生成器

**代码规范**：
```python
import unittest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

class TestUserAPI(unittest.TestCase):
    """用户API测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类级别的初始化"""
        # 创建测试数据库
        cls.test_db = "test_blog.db"
    
    def setUp(self):
        """每个测试方法执行前的准备"""
        self.client = TestClient(app)
        # 清理测试数据
    
    def tearDown(self):
        """每个测试方法执行后的清理"""
        # 清理测试数据
        pass
    
    def test_create_user(self):
        """测试创建用户"""
        response = self.client.post("/api/users", json={
            "name": "Test User",
            "email": "test@example.com"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())
    
    def test_get_user(self):
        """测试获取用户"""
        # 先创建用户
        create_response = self.client.post("/api/users", json={
            "name": "Test User",
            "email": "test@example.com"
        })
        user_id = create_response.json()["id"]
        
        # 测试获取
        get_response = self.client.get(f"/api/users/{user_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["name"], "Test User")

# 单元测试示例
class TestUserService(unittest.TestCase):
    """用户服务单元测试"""
    
    def setUp(self):
        """使用Mock对象进行单元测试"""
        self.mock_repository = Mock()
        self.service = UserService(self.mock_repository)
    
    def test_register_user(self):
        """测试用户注册逻辑"""
        # 配置Mock返回值
        self.mock_repository.create.return_value = User(
            id="123",
            name="Test User",
            email="test@example.com"
        )
        
        # 执行测试
        result = self.service.register_user(UserCreate(
            name="Test User",
            email="test@example.com"
        ))
        
        # 断言
        self.assertEqual(result.name, "Test User")
        self.mock_repository.create.assert_called_once()

# 运行测试
if __name__ == '__main__':
    unittest.main()
```

## FastAPI 平台特定知识

### 技术栈
- **框架**：FastAPI (最新版本)
- **ORM**：SQLAlchemy 2.0 (同步模式)
- **数据库**：SQLite（轻量级，适合开发和测试）
- **验证**：Pydantic v2
- **测试**：unittest（Python标准库，不使用pytest）
- **同步**：使用同步模式，简化开发

### 最佳实践

#### 1. 依赖注入
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
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

#### 3. 同步 SQLAlchemy with SQLite
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite同步配置
engine = create_engine("sqlite:///./blog.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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

### unittest最佳实践

#### 1. 测试组织结构
```
tests/
├── __init__.py
├── test_models.py          # 模型测试
├── test_services.py        # 服务层测试
├── test_repositories.py    # 仓储层测试
├── test_api/               # API测试
│   ├── __init__.py
│   ├── test_users.py
│   └── test_articles.py
├── fixtures/               # 测试数据
│   ├── __init__.py
│   └── test_data.py
└── conftest.py            # 测试配置（虽然是pytest的文件名，但可用于存放共享配置）
```

#### 2. 测试基类示例
```python
# tests/base.py
import unittest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

class BaseTestCase(unittest.TestCase):
    """所有测试的基类"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试数据库"""
        cls.engine = create_engine("sqlite:///./test.db")
        cls.SessionLocal = sessionmaker(bind=cls.engine)
        # 创建所有表
        Base.metadata.create_all(bind=cls.engine)
    
    @classmethod
    def tearDownClass(cls):
        """清理测试数据库"""
        Base.metadata.drop_all(bind=cls.engine)
        if os.path.exists("test.db"):
            os.remove("test.db")
    
    def setUp(self):
        """每个测试前的准备"""
        self.session = self.SessionLocal()
        self.client = TestClient(app)
    
    def tearDown(self):
        """每个测试后的清理"""
        self.session.rollback()
        self.session.close()
```

#### 3. Mock使用示例
```python
from unittest.mock import Mock, patch, MagicMock

class TestServiceWithMock(unittest.TestCase):
    
    @patch('module.DatabaseSession')
    def test_with_mock_db(self, mock_db):
        """使用patch装饰器模拟数据库"""
        mock_db.return_value.query.return_value.all.return_value = []
        # 测试代码
    
    def test_with_manual_mock(self):
        """手动创建Mock对象"""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = {"id": 1, "name": "test"}
        service = UserService(mock_repo)
        # 测试代码
```

#### 4. 断言方法
```python
# unittest提供的常用断言方法
self.assertEqual(a, b)           # a == b
self.assertNotEqual(a, b)        # a != b
self.assertTrue(x)                # bool(x) is True
self.assertFalse(x)               # bool(x) is False
self.assertIs(a, b)               # a is b
self.assertIsNone(x)              # x is None
self.assertIn(a, b)               # a in b
self.assertIsInstance(a, b)       # isinstance(a, b)
self.assertRaises(exc, fun, *args) # fun(*args) raises exc
self.assertAlmostEqual(a, b)      # round(a-b, 7) == 0
self.assertGreater(a, b)          # a > b
self.assertLess(a, b)             # a < b
self.assertListEqual(a, b)        # 列表相等
self.assertDictEqual(a, b)        # 字典相等
```

#### 5. 运行测试的方式
```bash
# 运行所有测试
python -m unittest discover tests/

# 运行特定测试文件
python -m unittest tests.test_users

# 运行特定测试类
python -m unittest tests.test_users.TestUserAPI

# 运行特定测试方法
python -m unittest tests.test_users.TestUserAPI.test_create_user

# 带详细输出
python -m unittest discover tests/ -v

# 失败时停止
python -m unittest discover tests/ -f
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

### SQLite特定配置
- 数据库文件：`blog.db`（本地文件）
- UUID存储：使用String(36)而非UUID类型
- 同步驱动：标准sqlite3
- 连接字符串：`sqlite:///./blog.db`
- 线程安全：`connect_args={"check_same_thread": False}`

### unittest测试配置
- 使用`unittest.TestCase`作为所有测试类的基类
- 使用`TestClient`来测试FastAPI应用
- 测试数据库：使用独立的`test_blog.db`
- 测试命令：`python -m unittest discover tests/`
- 测试文件命名：`test_*.py`
- 测试方法命名：`test_*`开头
- **不使用pytest**：所有测试都基于标准库unittest

## 生成指导原则

1. **完整性**：每个章节的代码必须是完整的、可运行的
2. **一致性**：所有章节使用相同的命名和编码规范
3. **专业性**：遵循 FastAPI 和 Python 最佳实践
4. **可测试性**：所有代码都应该易于测试
5. **文档化**：包含充分的注释和文档字符串
6. **必须生成所有5个章节**：不能只生成部分章节就停止

## PSM文档生成步骤（必须全部执行）

**重要**：PSM文档包含5个章节，必须全部生成，不能中途停止！

### 推荐方法：一次性生成所有章节
```python
# 构建完整的PSM文档内容
psm_content = """# Platform Specific Model (PSM) - 博客系统

## 1. Domain Models（领域模型）
...第一章完整内容...

## 2. Service Layer（服务层）
...第二章完整内容...

## 3. REST API Design（API设计）
...第三章完整内容...

## 4. Application Configuration（应用配置）
...第四章完整内容...

## 5. Testing Specifications（测试规范）
...第五章完整内容...
"""

# 一次性写入完整文件
write_file("blog_psm.md", psm_content)
```

### 备选方法：逐章追加（如果内容太大）

### 步骤1：创建文件并写入第一章
```bash
write_file(file_path="blog_psm.md", content="""# Platform Specific Model (PSM) - 博客系统

## 1. Domain Models（领域模型）

### Entity Definitions（实体定义）
...第一章完整内容...
""")
```

### 步骤2：追加第二章（必须执行）
```python
# 使用append_file直接追加
append_file("blog_psm.md", """

## 2. Service Layer（服务层）

### Business Services（业务服务）
...第二章完整内容...
""")
```

### 步骤3：追加第三章（必须执行）
```python
# 使用append_file直接追加
append_file("blog_psm.md", """

## 3. REST API Design（API设计）

### API Endpoints（端点定义）
...第三章完整内容...
""")
```

### 步骤4：追加第四章（必须执行）
```python
# 使用append_file直接追加
append_file("blog_psm.md", """

## 4. Application Configuration（应用配置）

### Main Application（主应用）
...第四章完整内容...
""")
```

### 步骤5：追加第五章（必须执行）
```python
# 使用append_file直接追加
append_file("blog_psm.md", """

## 5. Testing Specifications（测试规范）

### Unit Tests（单元测试）
...第五章完整内容...
""")
```

**记住**：即使内容很长，也必须完成所有5个章节！使用append_file工具可以简单安全地追加内容。

## 章节依赖关系

生成顺序应该遵循依赖关系：
1. Domain Models（无依赖）
2. Service Layer（依赖 Domain Models）
3. REST API Design（依赖 Service Layer 和 Domain Models）
4. Application Configuration（依赖所有其他章节）
5. Testing Specifications（依赖所有其他章节）

每个后续章节可以引用前面章节中定义的类和接口。