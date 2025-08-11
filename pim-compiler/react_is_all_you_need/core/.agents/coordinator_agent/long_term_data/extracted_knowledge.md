```markdown
# 知识库

## 元知识
- **路径验证策略**：当工具找不到文件时，使用`list_directory`检查实际目录结构，确认工作目录是否正确。
- **手动创建策略**：当自动化工具（如`psm_generation_agent`）无法创建文件时，采用手动创建方式：
  1. 先创建项目目录结构
  2. 读取PIM文件内容
  3. 手动构建PSM文件内容
- **工具失效应对**：当`read_file`或`search_files`无法找到预期文件时，使用`execute_command`结合`ls`、`find`等命令作为备用方案。
- **上下文确认**：每次执行命令前，先确认当前工作目录，使用`pwd`或`list_directory`验证。
- **渐进式验证**：每步操作后立即验证结果（如创建目录后检查是否成功，生成文件后确认内容）。
- **测试-调试-验证循环**：当单元测试（如`pytest`）失败时，使用专门的调试工具（如`debug_agent`）进行修复，然后必须重新运行测试以验证修复效果。
- **错误定位方法**：当测试失败或程序启动失败时，通过读取具体文件内容来定位问题根源，例如检查导入路径是否正确或分析错误日志。
- **超时处理策略**：当命令执行超时时，可尝试直接运行后续验证步骤，以确认是否实际已完成。

## 原理与设计
- **标准项目工作流**：
  1. 从PIM文件生成PSM文件 (`psm_generation_agent`)。
  2. 基于PSM生成FastAPI应用代码 (`generation_agent`)。
  3. 运行所有单元测试并验证100%通过。
  4. 如果测试失败，则进入“测试-修复”循环（可使用`debug_agent`），直到所有测试通过。
  5. 运行FastAPI应用（可使用`run_app_agent`）。
- **PSM文件结构**：基于PIM内容，PSM应包含五个核心部分：
  1. 领域模型（实体定义）
  2. 服务层（业务逻辑）
  3. REST API（端点定义）
  4. 应用配置
  5. 测试规范
- **手动PSM生成**：当自动化失败时，可以基于PIM的业务描述、实体、服务三部分手动构建PSM文件。
- **FastAPI项目结构**：一个标准的FastAPI应用应包含以下模块：
  - `models`: 数据模型定义（如SQLAlchemy模型）
  - `schemas`: Pydantic模型用于请求/响应
  - `services`: 业务逻辑层
  - `routers`: API路由定义（替代旧的`api`目录）
  - `database.py`: 数据库连接配置
  - `main.py`: 应用入口
- **模块导入规范**：在Python包中，确保所有子目录都有`__init__.py`文件，且导入路径需明确到具体模块（如`from app.models.models import Base`）。
- **数据模型转换陷阱**：当使用`.dict()`方法将一个Pydantic模型转换为字典以创建另一个（如数据库）模型实例时，需注意避免重复传递已存在于字典中的关键字参数，这可能导致`TypeError`。

## 接口与API
- **代码生成与调试代理**：
  - `psm_generation_agent`: 从PIM文件自动生成PSM文件。成功后会生成`<project_name>_psm.md`文件。
  - `generation_agent`: 基于PSM文件生成应用代码。
  - `debug_agent`: 用于在测试失败后自动修复代码。其输出可能不明确，需要通过再次运行测试来验证其效果。
  - `run_app_agent`: 用于在所有测试通过后，启动并运行FastAPI应用程序。
- **文件系统工具**：
  - `create_directory`: 用于手动创建项目根目录及子目录。
  - `read_file`: 读取PIM等文件内容，作为后续步骤的输入。
  - `write_file`: 当代码生成器失败时，用于手动创建或修复文件。
  - `list_directory`: 检查当前目录内容，确认操作上下文和文件创建结果。
- **命令执行工具**：
  - `execute_command`: 运行命令行工具，如`pytest`进行测试，或`ls`, `find`进行文件查找。注意设置合理的超时时间。

## 实现细节（需验证）
- **PSM文件位置**：应在项目根目录下，命名为`<project_name>_psm.md`。
- **项目根目录**（示例）：`/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/blog/`
- **PIM文件路径**（示例）：`/home/guci/aiProjects/mda/pim-compiler/examples/blog.md`
- **目录创建顺序**：先创建项目根目录，再创建内部子目录结构。
- **PSM内容构建**：从PIM中提取实体（如Article, Category, Comment）和服务描述，转换为PSM格式。
- **FastAPI项目结构**（可能已变化）：
  - 项目根目录：`output/<project_name>/`
  - 应用目录：`app/`
  - 模型目录：`app/models/`
  - Schemas目录：`app/schemas/`
  - 服务目录：`app/services/`
  - 路由目录：`app/routers/`
  - 数据库配置：`app/database.py`
  - 应用入口：`app/main.py`
- **关键文件内容**（可能已变化）：
  - `app/__init__.py`：确保包可被识别。
  - `app/models/models.py`：包含SQLAlchemy模型定义。
  - `app/main.py`：正确导入模型和路由，创建数据库表。
- **依赖管理**：项目根目录下的`requirements.txt`文件定义所需依赖。
- **常见运行时错误**：在服务层代码中，创建数据库模型实例时可能出现`TypeError: ... got multiple values for keyword argument ...`。这通常是因为调用`.dict()`方法后又显式传递了相同的参数。修复方法是移除重复的关键字参数。

## 用户偏好与项目特点
- **路径规范**：项目位于`/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/`目录下。
- **项目命名**：基于PIM文件名（如blog.md → blog项目）。
- **容错处理**：接受手动创建作为自动化失败的备选方案。
- **验证频率**：每步操作后都进行验证确认。
- **测试优先**：严格要求所有单元测试100%通过后，才能进行下一步（如运行应用）。
- **模块化设计**：遵循清晰的分层架构（models, schemas, services, routers），便于维护和调试。
- **自动化代理偏好**：倾向于使用专门的代理（如`debug_agent`, `run_app_agent`）来执行特定任务（如调试、运行应用），而不是完全依赖手动命令。
```