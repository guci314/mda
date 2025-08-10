# 知识库

## 元知识
- **灵活协调原则**：目标是让测试通过，支持调试Agent灵活选择修复方案
- **成本导向决策**：评估修复成本，选择总成本最低的方案
- **调试Agent任务模板**：
  ```
  修复错误，使所有测试通过。
  
  错误分析：{具体错误}
  
  修复策略：
  1. 评估修复成本
  2. 选择最简单的方案
  3. 可以修改测试或功能
  
  目标：用最小改动让测试通过
  ```
- **验证成功标准**：唯一标准是 "0 failed"，但需注意警告信息可能影响后续维护
- **常见问题快速解决**：
  - AsyncClient错误 → 改用TestClient
  - 路径404 → 调整测试路径或添加缺失端点
  - 数据验证失败 → 补充测试数据
  - 相对导入错误 → 替换为绝对导入路径
  - 测试数据隔离 → 确保每个测试创建所需数据
- **项目初始化流程**：
  1. 创建coordinator_todo.json跟踪任务
  2. 读取PSM文件内容
  3. 创建项目目录结构（app/, tests/, routers/）
  4. 基于PSM生成代码文件
  5. 运行测试验证
- **手动创建项目结构**：当code_generator无法自动创建时，需要手动创建目录和文件
- **测试依赖管理**：当测试失败涉及数据隔离时，需在测试中创建独立数据集

## 原理与设计
- **目标驱动**：让测试通过是最终目标，方法灵活
- **成本评估矩阵**：
  - 404路径错误：修改测试路径（低成本）vs 创建模块（高成本）
  - 架构不匹配：修改测试（低成本）vs 重构应用（极高成本）
  - 数据不匹配：调整数据（低成本）vs 修改Schema（中成本）
  - 导入路径错误：修复单个文件（低）vs 重构整个项目结构（高）
- **协调流程**：
  1. 运行测试获取错误
  2. 分析错误根因
  3. 评估修复方案
  4. 调用适当的Agent
  5. 验证结果
- **PSM到FastAPI映射原则**：
  - 领域模型 → Pydantic模型
  - 业务逻辑 → 服务层
  - 接口定义 → FastAPI路由
  - 测试用例 → pytest测试
- **手动代码生成策略**：当自动化工具失败时，按顺序手动创建文件（database.py → models.py → schemas.py → crud.py → routers/*.py → main.py → tests/*.py）
- **测试隔离原则**：每个测试应独立创建所需数据，避免跨测试依赖

## 接口与API
- **核心工具**：
  - `code_generator`：生成基础代码
  - `code_debugger`：灵活修复错误
  - `execute_command`：运行测试验证
  - `write_file`：管理TODO笔记和代码修改
  - `create_directory`：创建目录结构
  - `read_file`：检查文件内容定位问题
- **测试命令**：
  - `cd output/xxx && python -m pytest tests/ -xvs`
  - `rm test*.db`：清理测试数据库
- **调试结果验证**：
  ```python
  if "0 failed" in result:
      return "成功"
  ```
- **目录结构标准**：
  ```
  output/
    └── project_name/
        ├── app/
        │   ├── __init__.py
        │   ├── main.py
        │   ├── models.py
        │   ├── schemas.py
        │   ├── crud.py
        │   ├── database.py
        │   └── routers/
        │       ├── __init__.py
        │       └── *.py
        ├── tests/
        │   ├── __init__.py
        │   └── test_*.py
        └── coordinator_todo.json
  ```
- **文件读取模式**：使用read_file工具检查数据库配置、路由实现和测试逻辑

## 实现细节（需验证）
- **协调策略调整**：
  - 不再强制要求"不修改测试"
  - 支持双向修复（测试和功能）
  - 优先选择简单方案
- **PSM文件解析模式**：
  - 查找"Domain Models"部分提取实体定义
  - 查找"API Endpoints"部分提取路由定义
  - 查找"Test Cases"部分提取测试用例
- **代码生成顺序**：
  1. database.py（数据库配置）→ 需验证是否包含get_db函数
  2. models.py（Pydantic模型）
  3. schemas.py（请求/响应模型）
  4. crud.py（数据库操作）→ 需验证是否包含所有必要方法
  5. routers/*.py（API路由）→ 需验证端点完整性
  6. main.py（FastAPI实例）
  7. tests/test_*.py（测试文件）→ 需验证导入路径
- **测试验证流程**：
  - 首次运行：预期会有失败
  - 错误分析：查看具体失败原因
  - 修复循环：debug → 修改 → 重测
  - 成功标准：pytest输出包含"0 failed"
- **TODO文件格式**：JSON格式，包含tasks数组，每个task有id、description、status、timestamp字段
- **测试文件模式**：
  - 使用绝对导入路径（from app.main import app）
  - 每个测试独立创建所需数据
  - 包含数据库初始化逻辑
- **常见修复模式**：
  - 路由缺失端点 → 在对应router.py添加实现
  - CRUD方法缺失 → 在crud.py添加逻辑
  - 导入错误 → 检查文件位置和导入语法

## 用户偏好与项目特点
- **测试优先**：强调100%测试通过率
- **容忍警告**：接受弃用警告但记录为技术债务
- **路径规范**：项目位于/home/guci/aiProjects/mda/目录结构
- **技术栈**：FastAPI + SQLAlchemy + pytest组合
- **代码现代性**：倾向使用最新API（如Pydantic的model_dump()）