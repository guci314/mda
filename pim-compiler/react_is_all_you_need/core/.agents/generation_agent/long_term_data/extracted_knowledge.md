# 知识库

## 元知识
- **PSM到代码的完整映射流程**：从PSM文件→枚举定义→模型类→Schema→CRUD层→服务层→路由→测试→文档的完整流水线。
- **项目初始化策略**：
    - 优先创建分层目录结构：`app/models`, `app/schemas`, `app/crud`, `app/services`, `app/routers`, `tests`。
    - 在各子目录中创建`__init__.py`文件，使其成为可导入的包。
    - 在项目根目录生成`requirements.txt`和`README.md`。
- **模型与Schema组织模式**：存在两种主要模式，需根据项目规模和团队偏好选择。
    - **领域聚合模式（高内聚）**：将同一领域（如博客）下的紧密相关模型（Article, Category, Comment）聚合到单个文件中（如`models/blog.py`）。适用于领域模型关联紧密、方便统一查看关系的场景。
    - **资源拆分模式（高解耦）**：为每个模型/资源（Article, Category）创建单独的文件（如`models/article.py`, `models/category.py`）。适用于模型间独立性强、便于按功能并行开发的场景。
- **目录结构一致性**：CRUD、服务、路由、测试等按资源划分的目录，其文件名应保持一致（如`crud/crud_article.py`, `services/article_service.py`, `routers/articles.py`, `tests/test_articles.py`），便于查找和自动化生成。
- **枚举提取模式**：将PSM中的枚举字段统一提取到`models/enums.py`（用于SQLAlchemy）和`schemas/enums.py`（用于Pydantic），使用`str, Enum`基类。
- **Schema分层模式**：Create/Update/Response三层Schema，避免字段泄露。
- **服务层引入时机**：当业务逻辑超出简单CRUD时（如统计、关联查询、调用外部服务）引入services层。
- **字段映射验证方法**：PSM字段类型→SQLAlchemy类型→Pydantic类型的三重验证。
- **PSM字段类型映射表**：
  - Integer → sqlalchemy.Integer
  - String(长度) → sqlalchemy.String(长度)
  - Text → sqlalchemy.Text
  - DateTime → sqlalchemy.DateTime(timezone=True)
  - Enum → 自定义str, Enum类
  - ForeignKey → sqlalchemy.ForeignKey('表名.字段')
- **项目初始化验证方法**：在生成代码前检查目标目录是否为空，若为空则按标准结构初始化。
- **增量生成策略**：检查目标目录内容，仅生成缺失文件，避免覆盖已有内容。

## 原理与设计
- **分层职责边界**：
  - **路由层 (routers)**：仅处理HTTP协议相关逻辑（路径参数、请求体验证、响应序列化、HTTP状态码）。不包含业务逻辑，负责调用服务层。
  - **服务层 (services)**：封装核心业务逻辑。编排对一个或多个CRUD操作的调用，处理复杂的业务规则、事务管理和跨模型操作。
  - **CRUD层 (crud)**：提供与数据库单一模型对应的原子化、可复用的数据访问操作（Create, Read, Update, Delete）。
- **时间字段设计模式**：
  - 使用`DateTime(timezone=True)`确保时区安全。
  - 数据库层默认值：`server_default=func.now()`。
  - 应用层默认值：`default=datetime.utcnow`。
  - 自动更新：`onupdate=datetime.utcnow`。
- **外键关系配置**：
  - 双向关联：`relationship(back_populates=...)`。
  - 级联删除：`cascade="all, delete-orphan"`。
  - 预加载策略：`lazy="selectin"`避免N+1查询。
- **枚举类型最佳实践**：
  - 业务状态使用`str, Enum`确保类型安全，并分别在模型层和Schema层定义。
  - 枚举值使用小写字符串（draft/published）。
  - 在Schema中使用`Literal`类型或Pydantic的Enum约束输入。
- **Schema设计原则**：
  - CreateSchema：必填字段验证，排除不可写字段（如id, created_at）。
  - UpdateSchema：所有字段可选，支持部分更新。
  - ResponseSchema：包含关联字段配置，控制序列化深度。
- **默认值配置策略**：
  - 数据库层：使用`server_default`确保数据一致性。
  - 应用层：使用`default`提供业务默认值。
  - 整型默认值：使用`server_default=text("0")`而非字符串"0"。
- **项目结构设计原则**：保持与FastAPI推荐结构一致，引入`crud`层实现数据访问与业务逻辑的进一步分离。模型/Schema可按领域聚合或按资源拆分，但路由/服务/CRUD/测试层应始终按资源拆分。
- **数据库连接管理**：使用异步数据库引擎和会话管理，支持并发操作，配置文件为`app/database.py`。

## 接口与API
- **SQLAlchemy高级配置**：
  - `Index("idx_article_status", "status")`：状态字段索引。
  - `server_default=text("0")`：整型字段默认值。
  - `UniqueConstraint("name")`：复合唯一约束。
  - `DateTime(timezone=True)`：时区感知时间类型。
- **Pydantic模式配置**：
  - `orm_mode = True`：支持模型直接序列化。
  - `exclude={"comments"}`：控制关联字段深度。
  - `Field(..., min_length=1)`：字段验证约束。

## 实现细节（需验证）
- 注：以下结构为推荐实践，具体文件名可能变化，使用前需验证。
- **标准项目文件结构**：
  ```
  .
  ├── app/
  │   ├── __init__.py
  │   ├── crud/
  │   │   ├── __init__.py
  │   │   └── crud_[resource].py
  │   ├── database.py
  │   ├── main.py
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── enums.py
  │   │   └── [resource].py  # 或 blog.py (领域聚合模式)
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   └── [resource]s.py
  │   ├── schemas/
  │   │   ├── __init__.py
  │   │   ├── enums.py
  │   │   └── [resource].py  # 或 blog.py (领域聚合模式)
  │   └── services/
  │       ├── __init__.py
  │       └── [resource]_service.py
  ├── tests/
  │   ├── __init__.py
  │   └── test_[resource]s.py
  ├── README.md
  └── requirements.txt
  ```
- **数据库会话管理**：在`app/database.py`中定义引擎和会话，通过依赖注入在路由中使用。
- **应用入口**：在`app/main.py`中创建FastAPI应用实例，并使用`app.include_router()`挂载所有路由。