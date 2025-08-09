```markdown
# 知识库

## 元知识
- 通过PSM文档分析可快速提取系统核心数据模型和业务逻辑
- 分层目录结构(模型/路由/服务/模式)是组织FastAPI项目的有效方法
- 文件读写工具可用于自动化项目脚手架搭建
- PSM文档可直接映射为SQLAlchemy和Pydantic模型定义
- PSM文档中的实体关系可直接转换为数据库关系和API端点设计
- PIM文档可转换为PSM文档作为生成输入
- 项目生成前需验证依赖环境(python/pip)是否就绪
- 枚举类型应单独定义在schemas/enums.py中以提高复用性
- 测试文件应与服务模块保持1:1对应关系
- 基础API测试应包含在test_main.py中作为入口验证
- pytest测试文件命名需遵循test_*.py模式才能被自动识别
- 导入路径问题可通过绝对导入和PYTHONPATH环境变量解决
- 测试失败时应优先检查导入路径和缩进错误

## 原理与设计
- FastAPI项目应采用分层架构：
  - 模型层(SQLAlchemy)
  - 模式层(Pydantic)
  - 服务层(业务逻辑)
  - 路由层(API端点)
- 图书借阅系统核心实体包括：
  - Book(图书)
  - Reader(读者)
  - BorrowRecord(借阅记录)
  - ReservationRecord(预约记录)
- 数据库设计应包含唯一约束(如ISBN)和索引优化
- 实体关系设计原则：
  - 一对多(读者-借阅记录)
  - 多对多(图书-读者通过预约记录)
- 自动生成项目时应包含测试目录和基础配置文件
- 状态管理应使用枚举类型而非字符串常量
- 服务层应实现完整的CRUD操作和业务规则验证
- 测试架构应包含端点基础功能验证层
- 依赖注入应使用FastAPI的Depends机制
- 服务层构造函数应避免直接使用数据库会话类型

## 接口与API
- FastAPI标准项目结构：
  - `main.py`: 应用入口和CORS配置
  - `database.py`: SQLAlchemy设置
  - `models/`: SQLAlchemy模型定义
  - `schemas/`: Pydantic模型定义
  - `services/`: 业务逻辑实现
  - `routers/`: API路由定义
  - `tests/`: 测试代码
  - `utils/`: 工具函数
- 关键依赖：
  - fastapi
  - uvicorn
  - sqlalchemy
  - pydantic
  - pytest
- 基础API端点模式：
  - 创建(CREATE)
  - 读取(GET)
  - 更新(UPDATE)
  - 删除(DELETE)
- 图书管理API典型端点：
  - /books/ (GET, POST)
  - /books/{book_id} (GET, PUT, DELETE)
  - /books/isbn/{isbn} (GET)
- 项目生成工具应创建.env示例文件和requirements.txt
- 路由文件应按业务实体分离(books.py/readers.py等)
- 每个路由文件应包含对应实体的完整CRUD端点
- 测试API应包含根路径和基础CRUD操作验证
- 服务层应通过Depends注入数据库会话

## 实现细节（需验证）
- 数据库初始化可能在`database.py`中实现
- 各实体CRUD操作可能分布在对应service文件中
- API端点可能按实体分类在routers目录下
- 模型定义可能拆分到单独文件(models.py和schemas.py)
- 数据库关系可能通过SQLAlchemy relationship实现
- 项目生成可能包含config.py用于集中配置
- 枚举类型可能定义在schemas/enums.py中
- 测试文件可能使用pytest框架编写
- 服务层可能包含业务逻辑验证方法
- 基础测试可能集中在test_main.py中
- 测试可能使用TestClient进行端点验证
- 服务层构造函数可能接受Depends注入
- 路由文件可能使用APIRouter的prefix和tags参数
- 注：具体实现可能已变化，需验证文件内容

## 用户偏好与项目特点
- 偏好使用PSM文档作为系统设计输入
- 倾向完整的项目脚手架生成
- 遵循FastAPI官方推荐的项目结构
- 倾向于将模型和模式定义分离到不同文件
- 偏好包含基础CRUD操作的完整API端点实现
- 倾向于在模型层实现数据验证约束
- 偏好包含测试目录和实用工具目录
- 倾向生成环境配置示例文件
- 偏好按业务实体分离路由文件
- 倾向使用枚举类型管理状态
- 偏好包含基础API测试的入口验证
- 倾向保持测试文件与实现文件1:1对应
- 偏好使用绝对导入而非相对导入
- 倾向在服务层使用依赖注入
```