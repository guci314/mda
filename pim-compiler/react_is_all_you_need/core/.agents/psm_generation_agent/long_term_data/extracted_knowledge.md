```markdown
# 知识库

## 元知识
- PIM到PSM的生成流程：首先读取并解析PIM文件（业务描述→业务实体→业务服务），然后按顺序生成PSM的五个核心部分：1. 领域模型 (Domain Models) 2. 服务层 (Service Layer) 3. REST API 设计 4. 应用配置 (Application Configuration) 5. 测试规范 (Testing Specification)，最后将各部分组合写入目标文件。
- 处理复杂PIM的策略：当PIM文件内容庞大、实体众多时，应识别并优先处理核心业务实体，以生成具有代表性且可管理的PSM。
- 验证PSM完整性的标准：检查是否包含技术架构、数据模型（领域模型）、服务层、REST API、应用配置、技术栈、部署配置、测试规范等完整技术方案。
- 生成文件后，可使用`read_file`读取并检查最终内容，以验证所有部分都已成功写入，确保文件完整性。
- 查找项目约定的技巧：通过`examples`目录下的示例文件理解项目规范。
- 文件生成策略：对于多段内容生成，先使用`write_file`创建并写入第一部分，然后使用`append_file`追加后续部分。
- PIM文件结构解析方法：按"业务描述→业务实体→业务服务"顺序提取信息，每个业务实体需识别其属性及类型，业务服务需识别操作及关联实体。
- 新增验证方法：生成PSM后必须通过`read_file`验证所有必需章节是否存在，缺失则继续生成。

## 原理与设计
- PSM生成原则：保持业务逻辑不变，增加技术实现细节。
- PIM到PSM的映射关系：PIM中的`业务实体`映射为PSM的`数据模型`，`业务服务`映射为`服务层`和`API端点`。
- PIM中的状态属性（如 '状态：草稿/已发布'）应映射为PSM中的Python `Enum`类型，以增强代码的可读性和健壮性。
- 分层架构设计：表现层（REST API）→业务逻辑层（Services）→数据访问层（Repositories）→数据存储层（Database）。通过依赖注入（Dependency Injection）解耦各层。
- 模型分离原则：使用SQLAlchemy ORM定义持久化数据模型（与数据库表映射），使用Pydantic定义API数据传输对象（DTOs/Schemas）用于请求校验和响应序列化。
- RESTful API设计：资源导向，使用标准HTTP方法，状态码规范。
- 默认技术栈选型：在未指定技术栈时，倾向于使用 FastAPI 和 SQLAlchemy 作为默认实现方案。
- 领域模型设计原则：每个业务实体对应一个数据模型，属性类型需明确（如String、Text、DateTime、Integer、Enum等），关系通过外键建立。
- 服务层设计模式：按业务服务划分服务类，每个操作对应一个方法，通常采用仓储模式（Repository Pattern）将数据访问逻辑与业务逻辑分离。方法参数包含必要输入和可选参数。
- 数据模型设计模式：使用SQLAlchemy ORM模型，包含id主键、业务属性、时间戳、关系字段，使用Enum定义状态字段。
- REST API设计模式：使用FastAPI路由，路径参数对应资源ID，查询参数支持过滤和分页，响应模型使用Pydantic定义。

## 接口与API
- 文件操作API：
  - `read_file(path)`: 用于读取项目文件内容。
  - `write_file(filename, content)`: 用于创建或覆盖写入文件。
  - `append_file(filename, content)`: 用于在文件末尾追加内容。
- PSM输出文件结构：生成的Markdown文件包含以下二级标题（H2）：
  - `Domain Models`
  - `Service Layer`
  - `REST API Design`
  - `Application Configuration`
  - `Testing Specifications`
  - `Domain Models` 部分通常会进一步细分为 `Enums and Constants`, `Database Models (SQLAlchemy)`, 和 `Pydantic Schemas`。
- REST API设计规范：使用资源路径（如`/api/articles`），支持CRUD操作（GET/POST/PUT/DELETE），查询参数支持过滤和搜索。
- FastAPI路由定义模式：`@router.get("/api/{resource}")`，使用`response_model`指定返回类型，使用`Depends`注入服务依赖。
- SQLAlchemy模型定义模式：`class Model(Base): __tablename__ = "table_name"`，使用`Column`定义字段，使用`relationship`定义关联。

## 实现细节（需验证）
- 示例文件位置：`/home/guci/aiProjects/mda/pim-compiler/examples/` 目录存放PIM示例文件（如 `blog.md`, `smart_hospital_system.md`）。
- 博客系统PSM文件结构验证：生成的PSM文件必须包含5个核心章节（Domain Models, Service Layer, REST API Design, Application Configuration, Testing Specifications）。
- 状态枚举实现模式：对于PIM中的状态属性，PSM中应实现为Python Enum类（如ArticleStatus, CommentStatus）。
```