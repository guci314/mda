# 知识库

## 元知识
- **测试验证流程**：先运行`pytest tests/ -xvs`检查整体状态，再针对性调试。使用`-x`参数可以在首次失败时立即停止，便于快速定位问题。
- **调试策略**：遇到导入错误时，优先检查模块路径和文件结构，而非立即修改代码。测试失败是调用`code_debugger`的明确信号。
- **路径验证**：使用`execute_command`执行项目内命令（如pytest）时，必须先`cd`到正确的项目工作目录（如`cd output/mda_dual_agent_demo`）。
- **状态追踪**：通过`coordinator_todo.json`维护任务状态，每次状态变更（开始、完成、跳过）必须同步更新文件，确保流程可追溯。
- **异步测试调试**：pytest异步配置问题是常见故障点，需要检查pytest.ini配置和fixture定义。当遇到"async generator"相关错误时，优先检查pytest异步模式配置。
- **工具故障处理**：当`code_debugger`在初始化阶段反复失败时，可以直接使用基础工具（search_replace、write_file）进行修复，特别是配置文件问题。
- **测试冲突识别**：测试文件中出现重复测试函数（独立函数 vs 类方法）会导致测试失败，需要检查文件结构一致性。

## 原理与设计
- **PSM到FastAPI的映射原则**：
  - 每个实体对应：Model(数据库) + Schema(Pydantic) + Service(业务逻辑) + Router(API路由)。
  - 使用Repository模式封装数据库操作，Service层处理业务逻辑。
  - 依赖注入通过`dependencies.py`管理数据库会话。
- **测试设计**：按功能模块组织测试文件（test_main.py, test_books.py, test_readers.py），确保代码覆盖率。
- **错误处理**：在Service层统一处理业务异常，Router层返回标准HTTP响应。
- **项目结构一致性**：所有模块必须包含`__init__.py`确保Python包结构完整。
- **异步架构**：全面使用async/await模式，包括数据库操作、API端点和测试fixture。
- **生命周期管理**：使用FastAPI的`lifespan`事件管理数据库初始化和清理。

## 接口与API
- **核心工具**：
  - `code_generator`: 用于从PSM等输入生成完整的FastAPI应用骨架。
  - `code_debugger`: 在测试失败时调用，用于自动修复代码问题。但在初始化阶段可能失败，需要备用方案。
- **FastAPI标准结构**：
  - `main.py`：应用入口，包含路由注册和中间件配置。
  - `routers/`：按资源分组的API端点。
  - `schemas/`：Pydantic模型定义请求/响应结构。
  - `models/`：SQLAlchemy数据库模型。
  - `services/`：业务逻辑实现。
  - `repositories/`：数据访问层。
- **关键命令**：
  - **测试命令**：`cd output/mda_dual_agent_demo && python -m pytest tests/ -xvs` (-x: 首次失败即停止, -v: 详细输出, -s: 显示print)。
  - **依赖安装**：`pip install -r requirements.txt`。
  - **应用启动**：`uvicorn main:app --reload --host 0.0.0.0 --port 8000`。
- **依赖管理**：`requirements.txt`包含fastapi, sqlalchemy, pytest, uvicorn等核心依赖。
- **TODO管理**：`coordinator_todo.json`格式包含tasks数组，每项含id/task/status字段。
- **pytest异步配置**：
  - 使用`pytest.ini`而非`pyproject.toml`配置异步模式：`asyncio_mode = auto`
  - 异步fixture必须正确定义scope和类型注解
  - 测试类方法需要`@pytest.mark.asyncio`装饰器

## 实现细节（需验证）
- **文件结构**：
  ```
  output/mda_dual_agent_demo/
  ├── app/
  │   ├── __init__.py
  │   ├── database/
  │   │   ├── __init__.py
  │   │   ├── connection.py      # 数据库连接配置
  │   │   └── database.py        # 可能已变化
  │   ├── dependencies.py        # 依赖注入定义
  │   ├── enums.py               # 枚举定义
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── database.py        # SQLAlchemy模型
  │   │   └── pydantic.py        # Pydantic模式
  │   ├── routers/               # API路由
  │   ├── schemas/               # 可能已变化
  │   ├── services/              # 业务服务
  │   └── repositories/          # 数据仓库