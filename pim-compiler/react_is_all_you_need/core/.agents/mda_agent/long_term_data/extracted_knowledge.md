# 知识库

## 元知识
- **测试验证方法**：通过 `pytest` 命令直接运行测试，无需额外配置即可收集并执行测试用例
- **测试发现机制**：pytest 自动发现以 `test_*.py` 命名的文件和以 `test_*` 命名的函数
- **测试状态判断**：通过 pytest 输出中的 `collected X items` 和 `passed/failed` 统计快速判断测试覆盖率与成功率
- **测试环境隔离**：使用独立测试数据库（`test.db`）避免污染生产数据
- **快速验证技巧**：`pytest --collect-only` 可快速查看测试收集情况而不实际运行

## 原理与设计
- **测试架构**：采用 pytest + FastAPI TestClient + SQLAlchemy 的测试组合
- **数据库测试策略**：每个测试函数使用独立的数据库会话，确保测试隔离性
- **fixture 设计**：使用 `@pytest.fixture(scope="function")` 为每个测试创建干净的数据库环境
- **测试金字塔**：当前项目遵循单元测试优先，覆盖核心操作的基本测试策略

## 接口与API
- **pytest 命令**：
  - `pytest` - 运行所有测试
  - `pytest -v` - 详细输出
  - `pytest --collect-only` - 仅收集测试用例
- **FastAPI 测试工具**：`TestClient` 用于模拟 HTTP 请求测试 API 端点
- **测试插件**：项目使用 `pytest-benchmark` 插件，可能用于性能测试
- **测试配置**：`conftest.py` 中定义共享的测试 fixture（数据库会话、TestClient）
- **数据库测试配置**：
  - 测试数据库 URL：`sqlite:///./test.db`
  - 引擎参数：`connect_args={"check_same_thread": False}` 解决 SQLite 线程问题

## 实现细节（需验证）
- **测试文件位置**：`tests/` 目录下
- **测试文件命名**：`test_articles.py`（对应功能模块）
- **fixture 位置**：`tests/conftest.py` 包含数据库和客户端 fixture
- **测试数据库**：项目根目录下的 `test.db`（自动生成）
- **测试用例结构**：
  - **更正**：测试用例数量已变化。最新运行显示共收集到 3 个测试用例，而非原先的 5 个。具体的测试用例名称需重新检查。
- **项目结构**：
  ```
  ├── tests/
  │   ├── __init__.py
  │   ├── conftest.py
  │   └── test_articles.py
  ├── app/
  │   ├── main.py
  │   ├── database.py
  │   └── models/
  └── test.db
  ```

## 用户偏好与项目特点
- **项目名称**：`pim-compiler`
- **测试框架选择**：偏好 pytest 而非 unittest
- **测试数据库**：使用 SQLite 文件数据库而非内存数据库（可能为了调试方便）
- **测试范围**：当前重点测试核心功能（3个测试用例）
- **配置风格**：**更正：** 项目可能使用 `pytest.ini` 或 `pyproject.toml` 等配置文件，pytest 运行时会加载它们。
- **工具偏好**：使用 `pytest-benchmark`，表明对性能测试有潜在需求。