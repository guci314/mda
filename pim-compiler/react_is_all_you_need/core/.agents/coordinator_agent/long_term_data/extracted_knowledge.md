# 知识库

## 元知识
- **测试验证流程**：先运行`pytest tests/ -xvs`检查整体状态，再针对性调试
- **调试策略**：遇到导入错误时，优先检查模块路径和文件结构，而非立即修改代码
- **路径验证**：使用`execute_command`时确保工作目录正确（`cd output/mda_dual_agent_demo`）
- **状态追踪**：通过coordinator_todo.json维护任务状态，每次状态变更必须同步更新

## 原理与设计
- **PSM到FastAPI的映射原则**：
  - 每个实体对应：Model(数据库) + Schema(Pydantic) + Service(业务逻辑) + Router(API路由)
  - 使用Repository模式封装数据库操作，Service层处理业务逻辑
  - 依赖注入通过`dependencies.py`管理数据库会话
- **测试设计**：按功能模块组织测试文件（test_main.py, test_books.py, test_readers.py）
- **错误处理**：在Service层统一处理业务异常，Router层返回标准HTTP响应

## 接口与API
- **FastAPI标准结构**：
  - `main.py`：应用入口，包含路由注册和中间件配置
  - `routers/`：按资源分组的API端点
  - `schemas/`：Pydantic模型定义请求/响应结构
  - `models/`：SQLAlchemy数据库模型
  - `services/`：业务逻辑实现
  - `repositories/`：数据访问层
- **测试命令**：`python -m pytest tests/ -xvs`（-x: 首次失败即停止, -v: 详细输出, -s: 显示print）
- **依赖管理**：requirements.txt包含fastapi, sqlalchemy, pytest等核心依赖

## 实现细节（需验证）
- **文件结构**：
  ```
  output/mda_dual_agent_demo/
  ├── app/
  │   ├── main.py          # FastAPI应用实例
  │   ├── database.py      # 数据库连接配置
  │   ├── dependencies.py  # 依赖注入定义
  │   ├── enums.py         # 枚举定义
  │   ├── models/          # SQLAlchemy模型
  │   ├── routers/         # API路由
  │   ├── schemas/         # Pydantic模式
  │   ├── services/        # 业务服务
  │   └── repositories/    # 数据仓库
  └── tests/               # pytest测试用例
  ```
- **数据库配置**：使用SQLite文件数据库，路径在database.py中配置
- **测试覆盖率**：当前包含主应用、图书管理、读者管理三个测试模块

## 用户偏好与项目特点
- **任务管理**：强制要求使用coordinator_todo.json跟踪所有任务状态
- **调试规范**：必须通过code_debugger修复问题，禁止手动修改代码
- **测试标准**：要求100%测试通过率，任何失败都必须修复
- **目录约定**：输出目录固定为output/mda_dual_agent_demo/