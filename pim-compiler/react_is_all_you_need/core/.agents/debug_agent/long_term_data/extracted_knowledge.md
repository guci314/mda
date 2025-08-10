# 知识库

## 元知识
- **任务前置验证**：在开始修复任务（如“修复测试”）前，首先运行相关命令（如`pytest`）验证问题是否确实存在，避免在已经正常工作的系统上进行不必要的操作。
- **缺失文件诊断**：当遇到导入错误时，优先检查缺失的模块/文件，而非立即修改导入路径。
- **项目结构推断方法**：通过分析models、schemas、database.py等文件推断项目架构，然后反向验证缺失的组件。
- **测试文件创建策略**：当测试文件不存在时，根据项目结构创建基础测试套件，而非等待测试失败。
- **路由前缀验证**：检查路由注册路径（如`/api/articles`）与测试期望路径的一致性。
- **批量创建模式**：发现多个缺失文件时，一次性创建所有相关文件（路由、模型、模式）。
- **路径重复诊断**：当测试返回404但路由已注册时，检查是否存在双重前缀（router内prefix + include_router prefix）。
- **API路径验证**：使用`curl`或`TestClient`直接访问预期路径，确认实际可用路由列表。

## 原理与设计
- **完整MVC架构要求**：博客系统需要完整的四层结构 - models（数据层）、schemas（验证层）、services（业务层）、routers（接口层）。
- **路由模块化设计**：每个资源应有独立的路由文件（articles.py、categories.py、comments.py）。
- **测试驱动开发原则**：测试文件定义了期望的API契约，即使测试文件缺失，也应根据项目结构推断测试需求。
- **统一路由前缀**：API路由应使用统一前缀（如`/api/`）进行版本和作用域隔离。
- **渐进式修复策略**：从解决导入错误开始，逐步构建完整功能，而非一次性实现所有功能。
- **单一前缀原则**：路由前缀应在注册时（include_router）统一设置，避免在router定义中重复设置。

## 接口与API
- **测试套件执行**：使用`pytest`命令在项目根目录运行完整的单元测试套件。
- **FastAPI路由注册**：
  ```python
  app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
  ```
- **测试数据库配置**：
  ```python
  SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
  engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
  TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  ```
- **pytest fixture模式**：
  ```python
  @pytest.fixture(scope="function")
  def db_session():
      Base.metadata.create_all(bind=engine)
      # ... 测试逻辑 ...
      Base.metadata.drop_all(bind=engine)
  ```
- **路由文件模板**：
  ```python
  from fastapi import APIRouter, Depends, HTTPException
  from sqlalchemy.orm import Session
  from app.database import get_db
  
  router = APIRouter()
  
  @router.get("/")
  def get_items(db: Session = Depends(get_db)):
      return {"message": "Hello World"}
  ```
- **路由路径检查**：使用`TestClient(app).get("/openapi.json")`获取实际注册的所有路由路径。

## 实现细节（需验证）
- **项目文件结构**（可能已变化）：
  ```
  blog/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── database.py
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── article.py
  │   │   ├── category.py
  │   │   └── comment.py
  │   ├── schemas/
  │   │   ├── __init__.py
  │   │   ├── article.py
  │   │   ├── category.py
  │   │   └── comment.py
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   ├── articles.py
  │   │   ├── categories.py
  │   │   └── comments.py
  │   └── services/
  │       ├── __init__.py
  │       ├── article.py
  │       ├── category.py
  │       └── comment.py
  └── tests/
      ├── __init__.py
      ├── conftest.py
      └── test_articles.py
  ```
- **路由初始化顺序**：需要在routers/__init__.py中显式导入所有路由模块。
- **测试文件命名约定**：测试文件应以`test_`前缀命名，与被测试模块对应。
- **数据库初始化**：测试前需调用`Base.metadata.create_all(bind=engine)`创建表结构。
- **路由前缀设置位置**：应在`main.py`的`include_router`中设置prefix，**不应**在router文件中设置prefix。

## 用户偏好与项目特点
- **标准MVC结构**：项目采用标准MVC结构，每个资源有独立的model、schema、service、router文件。
- **API前缀约定**：所有API路由使用`/api/`前缀。
- **测试隔离**：测试数据库使用独立的test.db文件，与开发数据库。