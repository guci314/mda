# FastAPI PSM → Code 生成规则

## 项目结构模板

### 标准FastAPI项目结构
```
{service-name}/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── models.py            # SQLAlchemy模型
│   ├── schemas.py           # Pydantic模型
│   ├── crud.py              # 数据库操作
│   ├── database.py          # 数据库连接
│   ├── dependencies.py      # 依赖注入
│   └── routers/             # 路由模块
│       ├── __init__.py
│       └── {resource}.py    # 各个资源的路由
├── tests/                   # 测试文件
├── requirements.txt         # Python依赖
├── Dockerfile               # 容器化配置
└── .env                     # 环境变量
```

## 代码生成规则

### 1. 模型生成规则
对于每个数据库表，生成SQLAlchemy模型和Pydantic Schema：

**SQLAlchemy模型模板**:
```python
class {TableName}(Base):
    __tablename__ = "{table_name}"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    # 其他字段根据PSM定义生成
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Pydantic Schema模板**:
```python
class {TableName}Base(BaseModel):
    # 字段定义
    
class {TableName}Create({TableName}Base):
    pass
    
class {TableName}({TableName}Base):
    id: UUID
    created_at: datetime
    updated_at: datetime
```

### 2. CRUD操作生成
为每个模型生成标准的CRUD操作：
```python
def get_{resource}(db: Session, {resource}_id: UUID):
    return db.query({Model}).filter({Model}.id == {resource}_id).first()

def get_{resources}(db: Session, skip: int = 0, limit: int = 100):
    return db.query({Model}).offset(skip).limit(limit).all()

def create_{resource}(db: Session, {resource}: {Schema}Create):
    db_{resource} = {Model}(**{resource}.dict())
    db.add(db_{resource})
    db.commit()
    db.refresh(db_{resource})
    return db_{resource}
```

### 3. 路由生成
为每个资源生成RESTful路由：
```python
@router.get("/", response_model=List[{Schema}])
async def read_{resources}(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    {resources} = crud.get_{resources}(db, skip=skip, limit=limit)
    return {resources}

@router.post("/", response_model={Schema})
async def create_{resource}({resource}: {Schema}Create, db: Session = Depends(get_db)):
    return crud.create_{resource}(db, {resource}={resource})
```

### 4. 依赖配置
生成数据库连接和依赖注入：
```python
# database.py
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# dependencies.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 环境配置
生成Dockerfile、requirements.txt和环境配置：

**requirements.txt模板**:
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-multipart==0.0.6
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.0.1
```

**Dockerfile模板**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```