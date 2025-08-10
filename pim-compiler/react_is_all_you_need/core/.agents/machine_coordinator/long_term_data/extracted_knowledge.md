# 知识库

## 元知识
- **状态机调试模式**：通过严格的状态转换表执行，忽略中间过程的解释性内容，只关注状态转换条件和结果
- **测试驱动验证**：使用pytest作为核心验证工具，"0 failed"是唯一成功标准
- **语法错误修复策略**：当测试文件严重损坏时，重构比修复更有效
- **文件存在性检查**：作为状态转换的关键条件，优先检查关键文件（如app/main.py）

## 原理与设计
- **FastAPI应用结构**：采用模块化设计，通过include_router组织不同功能模块（books, readers）
- **生命周期管理**：使用@asynccontextmanager管理数据库初始化等启动任务
- **测试文件组织**：按功能模块分组测试（如test_reservations.py对应预约功能）
- **状态机设计原则**：每个状态有明确的转换条件，避免复杂分支

## 接口与API
- **pytest命令**：`pytest tests/` - 执行所有测试
- **FastAPI模块导入**：`from fastapi import FastAPI`, `from .routers import books, readers`
- **测试工具**：`httpx.AsyncClient`用于异步API测试
- **pytest标记**：`@pytest.mark.asyncio`标记异步测试，`@pytest.fixture`创建测试数据

## 实现细节（需验证）
- **主应用位置**：`app/main.py` - 包含FastAPI实例和路由注册
- **数据库初始化**：`app.database.init_db()` - 在应用启动时调用
- **路由模块**：`app/routers/books.py`和`app/routers/readers.py` - 具体API端点实现
- **测试目录**：`tests/` - 包含功能测试文件
- **测试文件命名**：`test_*.py`格式，如`test_reservations.py`

## 用户偏好与项目特点
- **严格状态机执行**：偏好明确的规则执行，不接受解释性干预
- **测试优先**：所有代码必须通过pytest验证，0失败是硬性要求
- **模块化设计**：功能按模块划分，保持清晰的代码结构
- **异步优先**：使用async/await模式处理I/O操作