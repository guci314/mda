# PIM引擎MVP实施计划

## MVP目标（6-8周）

快速构建一个可运行的PIM执行引擎原型，验证核心理念的可行性。

## 第1-2周：基础架构搭建

### 1.1 开发环境准备
```bash
# 项目结构
pim-engine/
├── src/
│   ├── core/           # 引擎核心
│   ├── loaders/        # 模型加载器
│   ├── engines/        # 各类引擎
│   ├── api/            # API层
│   └── utils/          # 工具类
├── models/             # 示例PIM模型
├── tests/              # 测试
├── docker/             # Docker配置
└── docs/               # 文档
```

### 1.2 核心依赖
```python
# requirements.txt
fastapi==0.109.0
pydantic==2.5.0
sqlalchemy==2.0.25
asyncpg==0.29.0
redis==5.0.1
pyyaml==6.0.1
pytest==7.4.0
httpx==0.26.0
```

### 1.3 基础框架代码
```python
# src/core/engine.py
from fastapi import FastAPI
from typing import Dict, Any
import yaml

class PIMEngine:
    def __init__(self):
        self.app = FastAPI(title="PIM执行引擎")
        self.models = {}
        self._setup_routes()
    
    def load_model(self, model_path: str):
        """加载PIM模型"""
        with open(model_path, 'r', encoding='utf-8') as f:
            # 简单的YAML解析作为开始
            model_data = yaml.safe_load(f)
        
        model_name = model_data.get('domain', 'unknown')
        self.models[model_name] = model_data
        self._register_model_apis(model_name, model_data)
    
    def _setup_routes(self):
        @self.app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        @self.app.get("/models")
        async def list_models():
            return {"models": list(self.models.keys())}
```

## 第3-4周：模型加载器和数据引擎

### 2.1 PIM模型解析器
```python
# src/loaders/pim_parser.py
import re
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Entity:
    name: str
    attributes: Dict[str, str]
    constraints: List[str]

class PIMParser:
    def parse_markdown(self, content: str) -> Dict:
        """解析Markdown格式的PIM"""
        entities = self._extract_entities(content)
        services = self._extract_services(content)
        rules = self._extract_rules(content)
        
        return {
            "entities": entities,
            "services": services,
            "rules": rules
        }
    
    def _extract_entities(self, content: str) -> List[Entity]:
        # 使用正则表达式提取实体定义
        # 示例实现
        entities = []
        # ... 解析逻辑
        return entities
```

### 2.2 动态数据模型
```python
# src/engines/data_engine.py
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class DataEngine:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Base = declarative_base()
        self.Session = sessionmaker(bind=self.engine)
        self.models = {}
    
    def create_model_class(self, entity_name: str, attributes: Dict):
        """动态创建SQLAlchemy模型类"""
        attrs = {
            '__tablename__': entity_name.lower(),
            'id': Column(Integer, primary_key=True)
        }
        
        # 动态添加属性
        for attr_name, attr_type in attributes.items():
            if attr_type == 'string':
                attrs[attr_name] = Column(String)
            elif attr_type == 'integer':
                attrs[attr_name] = Column(Integer)
            elif attr_type == 'float':
                attrs[attr_name] = Column(Float)
            elif attr_type == 'datetime':
                attrs[attr_name] = Column(DateTime)
        
        # 创建类
        model_class = type(entity_name, (self.Base,), attrs)
        self.models[entity_name] = model_class
        return model_class
    
    def create_tables(self):
        """创建所有表"""
        self.Base.metadata.create_all(self.engine)
```

## 第5-6周：API生成器和基础CRUD

### 3.1 动态API生成
```python
# src/api/api_generator.py
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from pydantic import create_model

class APIGenerator:
    def __init__(self, engine):
        self.engine = engine
        self.router = APIRouter()
    
    def generate_crud_routes(self, entity_name: str, attributes: Dict):
        """为实体生成CRUD路由"""
        
        # 动态创建Pydantic模型
        fields = {}
        for attr, type_str in attributes.items():
            if type_str == 'string':
                fields[attr] = (str, ...)
            elif type_str == 'integer':
                fields[attr] = (int, ...)
            elif type_str == 'float':
                fields[attr] = (float, ...)
        
        CreateModel = create_model(f"{entity_name}Create", **fields)
        UpdateModel = create_model(f"{entity_name}Update", **fields)
        
        # 生成路由
        @self.router.post(f"/{entity_name.lower()}")
        async def create(data: CreateModel):
            # 实现创建逻辑
            return {"id": 1, **data.dict()}
        
        @self.router.get(f"/{entity_name.lower()}/{{id}}")
        async def read(id: int):
            # 实现读取逻辑
            return {"id": id, "name": "Example"}
        
        @self.router.put(f"/{entity_name.lower()}/{{id}}")
        async def update(id: int, data: UpdateModel):
            # 实现更新逻辑
            return {"id": id, **data.dict()}
        
        @self.router.delete(f"/{entity_name.lower()}/{{id}}")
        async def delete(id: int):
            # 实现删除逻辑
            return {"status": "deleted"}
        
        @self.router.get(f"/{entity_name.lower()}")
        async def list_all(skip: int = 0, limit: int = 100):
            # 实现列表查询
            return {"items": [], "total": 0}
```

### 3.2 示例PIM模型
```yaml
# models/user_management.yaml
domain: 用户管理
version: 1.0.0

entities:
  - name: User
    attributes:
      name: string
      email: string
      phone: string
      status: string
    constraints:
      - email must be unique
      - status in ['active', 'inactive']

services:
  - name: UserService
    methods:
      - name: createUser
        parameters:
          userData: User
        rules:
          - validate email format
          - check email uniqueness

rules:
  email_format: "邮箱必须包含@符号"
  phone_format: "电话必须是11位数字"
```

## 第7-8周：集成测试和优化

### 4.1 集成测试
```python
# tests/test_engine.py
import pytest
from httpx import AsyncClient
from src.core.engine import PIMEngine

@pytest.fixture
async def engine():
    engine = PIMEngine()
    engine.load_model("models/user_management.yaml")
    return engine

@pytest.fixture
async def client(engine):
    async with AsyncClient(app=engine.app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post("/user", json={
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000",
        "status": "active"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "张三"

@pytest.mark.asyncio
async def test_list_users(client):
    response = await client.get("/user")
    assert response.status_code == 200
    assert "items" in response.json()
```

### 4.2 Docker部署
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY models/ ./models/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.3 docker-compose.yml
```yaml
version: '3.8'

services:
  pim-engine:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://pim:password@postgres:5432/pim_engine
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./models:/app/models
  
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=pim
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=pim_engine
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 交付清单

### 第8周末交付物
- [ ] 可运行的Docker镜像
- [ ] 3个示例PIM模型（用户管理、订单管理、库存管理）
- [ ] API文档（自动生成）
- [ ] 部署指南
- [ ] 性能测试报告

### 演示场景
1. **模型加载演示**
   ```bash
   # 加载用户管理模型
   curl -X POST http://localhost:8000/models/load \
     -d '{"model": "user_management.yaml"}'
   ```

2. **CRUD操作演示**
   ```bash
   # 创建用户
   curl -X POST http://localhost:8000/user \
     -H "Content-Type: application/json" \
     -d '{"name": "张三", "email": "zhang@example.com"}'
   
   # 查询用户
   curl http://localhost:8000/user/1
   ```

3. **性能展示**
   - 模型加载时间 < 500ms
   - API响应时间 < 100ms
   - 支持并发请求 > 100/s

## 后续优化方向

### 性能优化
- 模型预编译
- 查询缓存
- 连接池优化

### 功能增强
- 复杂数据类型支持
- 关联关系处理
- 批量操作API

### 开发体验
- 更好的错误提示
- 模型验证工具
- 在线模型编辑器

## 关键决策点

1. **技术栈确认**（第1周）
   - Python vs Go vs Java
   - FastAPI vs Flask vs Django
   - PostgreSQL vs MySQL

2. **模型格式**（第2周）
   - Markdown vs YAML vs JSON
   - 如何表达复杂关系
   - 规则语法设计

3. **API风格**（第4周）
   - REST vs GraphQL
   - 命名规范
   - 错误处理标准

4. **部署方案**（第6周）
   - Docker vs K8s
   - 单体 vs 微服务
   - 监控方案选择

通过这个MVP，我们将验证PIM执行引擎的核心理念，为后续的增强开发奠定基础！