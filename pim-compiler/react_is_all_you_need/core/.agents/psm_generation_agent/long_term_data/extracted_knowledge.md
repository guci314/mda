# 知识库

## 元知识
- PIM到PSM的生成流程：首先读取并解析PIM文件（业务描述→业务实体→业务服务），然后按顺序生成PSM的五个核心部分：1. 领域模型 (Domain Models) 2. 服务层 (Service Layer) 3. REST API 设计 4. 应用配置 (Application Configuration) 5. 测试规范 (Testing Specification)，最后将各部分组合写入目标文件。
- 验证PSM完整性的标准：检查是否包含技术架构、数据模型（领域模型）、服务层、REST API、应用配置、技术栈、部署配置、测试规范等完整技术方案。
- 查找项目约定的技巧：通过`examples`目录下的示例文件理解项目规范。
- 文件生成策略：对于多段内容生成，先使用`write_file`创建并写入第一部分，然后使用`append_file`追加后续部分。
- PIM文件结构解析方法：按"业务描述→业务实体→业务服务"顺序提取信息，每个业务实体需识别其属性及类型，业务服务需识别操作及关联实体。

## 原理与设计
- PSM生成原则：保持业务逻辑不变，增加技术实现细节。
- PIM到PSM的映射关系：PIM中的`业务实体`映射为PSM的`数据模型`，`业务服务`映射为`服务层`和`API端点`。
- 分层架构设计：表现层→业务逻辑层→数据访问层→数据存储层。
- RESTful API设计：资源导向，使用标准HTTP方法，状态码规范。
- 默认技术栈选型：在未指定技术栈时，倾向于使用 FastAPI 和 SQLAlchemy 作为默认实现方案。
- 领域模型设计原则：每个业务实体对应一个数据模型，属性类型需明确（如String、Text、DateTime、Integer、Enum等），关系通过外键建立。
- 服务层设计模式：按业务服务划分服务类，每个操作对应一个方法，方法参数包含必要输入和可选参数。
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
- REST API设计规范：使用资源路径（如`/api/articles`），支持CRUD操作（GET/POST/PUT/DELETE），查询参数支持过滤和搜索。
- FastAPI路由定义模式：`@router.get("/api/{resource}")`，使用`response_model`指定返回类型，使用`Depends`注入服务依赖。
- SQLAlchemy模型定义模式：`class Model(Base): __tablename__ = "table_name"`，使用`Column`定义字段，使用`relationship`定义关联。

## 实现细节（需验证）
- 项目结构：`/home/guci/aiProjects/mda/pim-compiler/examples/`目录存放示例文件。
- PIM文件位置：`/home/guci/aiProjects/mda/pim-compiler/examples/blog.md`。
- PSM输出约定：输出路径和文件名由任务具体指定。可以是绝对路径，也可以是相对路径。当指定为相对路径时（如 `blog_psm.md`），文件将生成在当前工作目录。
- 示例文件命名模式：PIM文件使用小写名词（如`blog.md`），对应PSM文件添加`_psm`后缀（如`blog_psm.md`）。
- PIM文件内容组织：使用Markdown二级标题划分"业务描述"、"业务实体"、"业务服务"三个主要部分。
- 业务实体属性类型推断：字符串默认为VARCHAR(255)，长文本为TEXT，日期时间为DateTime，计数为Integer，状态为Enum。
- 注：实现细节可能已变化，使用前需验证

## 用户偏好与项目特点
- 使用Markdown格式编写技术文档。
- PIM文件结构：通常包含`业务描述`、`业务实体`（如文章、分类、评论）和`业务服务`（如文章服务、评论服务）。
- PSM文件结构：包含领域模型、Pydantic Schemas、服务层、REST API设计等部分。
- 技术栈倾向：FastAPI + SQLAlchemy。