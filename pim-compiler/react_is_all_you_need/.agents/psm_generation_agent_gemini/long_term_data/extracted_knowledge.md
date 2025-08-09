# 知识库

## 元知识
- **PIM到PSM转换方法论**：
    - 核心实体 (PIM) -> 数据模型 (PSM)
    - 业务操作 (PIM) -> API 设计 (PSM)
    - 业务约束和规则 (PIM) -> 实现细节 (PSM)
    - 命名转换：中文转英文，遵循编程语言和数据库命名规范（snake_case, PascalCase）
- **文档生成策略**：在进行复杂转换（如PIM到PSM）时，先明确转换思路和步骤，再逐步生成内容，有助于确保转换的完整性和准确性。
- **结构化生成与验证工作流**：采用“读取输入 -> 分析需求 -> 规划输出结构 -> 分步生成内容 -> **使用工具写入文件 -> 读取并验证文件**”的流程，可以系统性地完成复杂生成任务并保证质量。验证步骤应包括检查文件是否存在和内容是否完整（如包含所有必需章节）。
- **PSM文档结构化方法**：将PSM文档划分为明确的章节（如Domain Models, Service Layer, REST API Design, Application Configuration, Testing Specifications），有助于系统化地组织和呈现PSM内容。
- **PIM解析策略**：通过正则表达式解析Markdown格式的PIM文档，提取实体、属性及其详细信息（类型、是否必填、是否唯一、默认值、枚举值等）。
- **命名转换函数**：`to_snake_case` 和 `to_pascal_case` 是将中文或混合大小写名称转换为符合编程规范的有效方法。
- **类型映射策略**：PIM中的抽象类型（如“文本”、“整数”、“日期时间”）需要映射到PSM中特定技术栈的具体类型（如Python的`str`, `int`, `datetime`，SQLAlchemy的`String`, `Integer`, `DateTime`，Pydantic的`str`, `int`, `datetime`）。

## 原理与设计
- **PIM (Platform Independent Model) 到 PSM (Platform Specific Model) 转换原则**：
    - PIM关注业务概念和逻辑，不涉及具体技术实现。
    - PSM将PIM中的概念映射到特定技术栈（如数据库、API框架）的具体实现细节。
    - 转换过程中需考虑数据类型映射、约束（唯一、非空）、关系、API端点设计、请求/响应体结构、以及业务规则的具体实现方式。
- **系统设计分层思想**：将业务逻辑（PIM）与技术实现（PSM）分离，提高系统的可维护性和可移植性。PSM的输出结构（Domain, Service, API）是这一思想的具体体现。
- **PSM文档内容分层**：PSM文档应包含从数据模型到API设计，再到服务层逻辑和配置、测试的完整技术实现描述，体现了从静态结构到动态行为的全面映射。
- **领域模型设计**：PSM中的领域模型应包含纯Python类（表示核心业务对象）、SQLAlchemy ORM模型（用于数据库持久化）和Pydantic Schema（用于数据验证和序列化），以适应不同层次的需求。
- **API设计原则**：遵循RESTful原则，为每个资源（实体）提供CRUD（创建、读取、更新、删除）操作的API端点。
- **服务层职责**：服务层负责封装业务逻辑，协调数据访问，保持与API层的解耦。
- **自动化字段添加**：在PSM中为实体自动添加 `id` (主键) 和 `created_at`, `updated_at` (时间戳) 字段是常见的实践，用于审计和唯一标识。
- **状态字段的枚举化**：对于业务实体中的状态字段（如图书状态、读者状态、读者类型、借阅状态），使用枚举（Enum）进行建模，可以增强代码的可读性、类型安全性和可维护性。例如，PIM中的“图书状态”会转换为`BookStatusEnum`，“读者状态”会转换为`ReaderStatusEnum`。

## 接口与API
- **文件操作工具**：
    - `read_file`: 用于读取指定路径的文件内容。
    - `write_file` 或 `WriteFileSystemTool`: 用于将内容写入指定路径的文件。
- **PIM到PSM转换中涉及的技术概念（PSM侧）**：
    - **数据库模型**：SQLAlchemy ORM 模型（用于实体持久化），包括 `Column`, `Integer`, `String`, `DateTime`, `Date`, `Float`, `Boolean`, `UUID`, `SQLEnum` 等类型。
    - **API模型**：Pydantic Schema（用于请求/响应数据验证和序列化），包括 `BaseModel`, `Field`, `EmailStr`, `ConfigDict` 等。
    - **枚举类型接口**：在FastAPI/Pydantic中，使用 `class MyEnum(str, Enum):` 的形式定义枚举，使其同时兼容字符串和枚举类型，便于API的序列化和验证。
    - **字段类型映射**：PIM中的文本、整数、枚举等类型需映射到数据库和Pydantic的相应类型。
    - **约束**：唯一性 (`unique=True`)、非空 (`nullable=False`)、主键 (`primary_key=True`)、索引等。
    - **时间戳**：`created_at`, `updated_at` 字段的自动管理 (`default=datetime.utcnow`, `onupdate=datetime.utcnow`)。
    - **API设计**：RESTful API，HTTP方法（GET, POST, PUT, DELETE），路径，请求体，响应体。使用FastAPI的`APIRouter`, `Depends`, `HTTPException`, `status`。
    - **业务逻辑实现**：Service层、Repository层（数据访问抽象）。
    - **Python标准库**：`re` (正则表达式), `datetime`, `uuid`, `enum`。
    - **FastAPI应用配置**：`FastAPI` 应用初始化，`asynccontextmanager` 用于生命周期管理，`create_async_engine`, `AsyncSession`, `async_sessionmaker` 用于异步数据库连接。
    - **测试框架**：`pytest`, `httpx.AsyncClient` 用于API测试，`asyncio` 用于异步测试。

## 实现细节（需验证）
- **PIM文件结构与解析**：
    - 预期PIM文件（如`library_borrowing_system_pim.md`）包含“领域概述”、“核心实体”等Markdown标题结构。
    - “核心实体”下包含具体的实体定义，每个实体有“属性”列表。
    - 实体名称提取模式：`### (.*?)\s*\((.*?)\)`，用于从 `### 图书 (Book)` 中提取中文和英文实体名。
    - 属性列表通常以 `**属性:**` 开头，后跟无序列表项。
    - 属性行格式示例：`- ISBN (文本，必填，唯一): 国际标准书号`。
    - 属性行解析：通过正则表达式提取属性名、括号内的元数据（如类型、约束）和描述。括号内的元数据需要进一步解析。
    - 枚举类型在PIM中以特定格式出现，如 `- 状态 (枚举，必填): [在架, 已下架]` 或 `- 状态 (枚举，必填): [正常, 冻结, 注销]`，解析时需提取方括号内的值。
- **PSM文件生成结构**：
    - 生成的PSM文件（如`library_borrowing_system_psm.md`）应包含对数据库模型（SQLAlchemy）和API模型（Pydantic）的详细描述。
    - PSM文档预期包含以下核心章节：`1. Domain Models`, `2. Service Layer`, `3. REST API Design`, `4. Application Configuration`, `5. Testing Specifications`。
    - PSM文档中的代码示例会根据逻辑功能放置在推荐的文件路径下，如 `src/models/enums.py`。
- **命名转换模式**：
    - 实体名和属性名从中文转换为英文。
    - 数据库表名和字段名通常使用 `snake_case`（例如：`books`, `reader_id`）。
    - Python类名（如Pydantic或SQLAlchemy模型）通常使用 `PascalCase`（例如：`Book`, `ReaderDB`）。
    - 枚举类名通常为属性名 `PascalCase` + `Enum` 后缀（例如：`StatusEnum`）。
    - 枚举成员名转换为大写蛇形（`UPPER_SNAKE_CASE`），而其值保留PIM中的原始字符串。例如，PIM中的 `[在架, 已下架]` 转换为 `ON_SHELF = "在架"` 和 `OFF_SHELF = "已下架"`；`[正常, 冻结, 注销]` 转换为 `NORMAL = "正常"`, `FROZEN = "冻结"`, `CANCELLED = "注销"`。
- **通用字段添加**：在PSM中，通常会为每个实体添加 `id` (主键) 和 `created_at`, `updated_at` (时间戳) 字段。
- **PSM生成步骤**：
    1. 从PIM中提取核心实体及其属性（包括枚举值）。
    2. 生成Enums和Constants部分（基于PIM中的枚举类型）。
    3. 为每个实体生成Domain Models（包括纯Python类、SQLAlchemy模型和Pydantic Schema）。
    4. 生成Service Layer，包含Repository和Service类的通用CRUD方法。
    5. 生成REST API Design，使用FastAPI的APIRouter为每个实体创建CRUD API端点。
    6. 生成Application Configuration，包含数据库连接、FastAPI应用初始化和路由注册。
    7. 生成Testing Specifications，包含Pytest测试配置和示例单元/集成测试。
- **枚举实现模式**：在FastAPI/Pydantic中，使用 `class MyEnum(str, Enum):` 的形式定义枚举，使其同时兼容字符串和枚举类型，便于API的序列化和验证。
- 注：实现细节可能已变化，使用前需验证

## 用户偏好与项目特点
- 用户倾向于将PIM文档作为输入，并期望输出结构化的PSM文档。
- **任务性质**：用户强调任务是**文件生成**而非简单的内容输出，必须调用文件写入工具创建物理文件。
- **输出格式**：输出必须是**单一、完整**的Markdown格式文档，而非零散的代码片段或不完整的章节。
- **输出验证**：任务完成后，需要有明确的验证步骤，如检查文件是否存在、读取文件内容确认所有必需章节都已生成。
- 用户对PIM到PSM的转换有明确的期望，包括数据模型、API设计和业务规则的实现细节。
- 任务要求输出文件名为 `[input_base_name]_psm.md`，例如 `library_borrowing_system_psm.md`。
- 用户期望PSM文档内容结构化，包含Domain Models, Service Layer, REST API Design, Application Configuration, Testing Specifications等章节。
- 用户期望生成的PSM代码示例是Python语言，并使用FastAPI、SQLAlchemy和Pydantic等主流库。
- 用户对数据库持久化和API数据验证有明确需求。
- 用户对测试策略和示例测试用例有需求。
- 用户偏好将生成的代码示例置于一个清晰、符合惯例的项目文件结构中（例如 `src/models/enums.py`）。