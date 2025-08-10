# 知识库

## 元知识
- **语法错误快速定位**：pytest 的 Exit code 2 通常表示语法错误，优先检查最近修改的测试文件
- **测试文件修复策略**：当测试文件严重损坏时，重建比修复更高效，保留核心测试逻辑
- **调试循环模式**："运行-失败-调试-再运行"是有效的自动化调试策略
- **状态检查顺序**：先运行测试看失败数量，再针对性修复，避免盲目修改

## 原理与设计
- **测试驱动开发**：测试用例定义了系统的预期行为，是开发的指南针
- **分层测试架构**：测试文件按功能模块组织（如预约API、借阅系统等）
- **fixture 设计模式**：使用 pytest fixture 设置测试前置条件，提高测试复用性
- **异步测试支持**：使用 `@pytest.mark.asyncio` 和 `AsyncClient` 测试异步API

## 接口与API
- **pytest 命令**：`pytest tests/` 运行所有测试，`pytest -v` 显示详细输出
- **AsyncClient 用法**：`httpx.AsyncClient` 用于异步HTTP测试，需要 `async with` 上下文
- **fixture 定义**：`@pytest.fixture` 装饰器定义测试前置条件，可依赖其他fixture
- **测试标记**：`@pytest.mark.asyncio` 标记异步测试函数

## 实现细节（需验证）
- **测试文件位置**：`tests/` 目录下按功能分文件组织
- **fixture 共享**：`conftest.py` 可能包含共享的fixture定义（需验证是否存在）
- **测试数据准备**：使用 fixture 如 `created_book`、`created_reader` 准备测试数据
- **数据库状态**：测试前可能需要重置数据库状态（`library.db` 文件存在）

## 用户偏好与项目特点
- **项目结构**：采用 FastAPI 风格，包含 `app/`, `models/`, `routers/`, `services/` 等目录
- **测试风格**：测试类按API模块组织，方法名清晰描述测试场景
- **调试工具**：使用 code_debugger 自动修复代码，但严重损坏时需要人工重建
- **成功标准**：唯一标准是 pytest 显示 "0 failed"