# 知识库

## 元知识
- **PSM缺失时的处理策略**：当PSM文件不存在时，基于标准图书借阅系统模式生成完整应用，包含Book、Reader、BorrowRecord、ReservationRecord四大核心实体
- **项目结构验证方法**：使用`find`命令检查关键文件存在性，通过文件计数验证生成完整性
- **渐进式目录创建**：先创建主目录结构(app/models/routers/services/repositories)，再填充具体文件
- **枚举类最佳实践**：将枚举定义独立为`enums.py`，使用`str, Enum`组合确保数据库兼容性和API文档可读性
- **模型文件组织策略**：数据库模型(`database.py`)与Pydantic模型(`schemas/`目录下按功能分文件)分离，避免循环引用
- **测试环境快速验证**：使用`pytest test_simple.py -v`先验证基础功能，避免一次性运行所有测试
- **文件存在性检查**：使用`list_directory`工具递归检查项目结构，确认关键文件是否已存在

## 原理与设计
- **四层实体架构**：Book(图书)、Reader(读者)、BorrowRecord(借阅记录)、ReservationRecord(预约记录)构成完整业务闭环
- **状态机设计**：使用枚举类型定义业务状态(BookStatus、ReaderStatus、BorrowStatus)，实现状态转换约束
- **软删除模式**：通过状态字段(REMOVED)实现逻辑删除，保持数据完整性
- **关联关系设计**：
  - Book 1-N BorrowRecord(借阅历史)
  - Reader 1-N BorrowRecord(借阅记录)
  - Book 1-N ReservationRecord(预约记录)
  - Reader 1-N ReservationRecord(预约记录)
- **事务边界控制**：在service层实现复杂业务操作(借书、还书、预约)的事务管理
- **DTO转换模式**：使用Pydantic的`from_orm`进行数据库模型到响应模型的转换
- **依赖注入层级**：router → service → repository → database，每层通过Depends注入依赖
- **模块化设计**：按功能将Pydantic模型分散到`schemas/`目录下的独立文件(book.py, reader.py, borrow.py, reservation.py)

## 接口与API
- **标准CRUD端点模式**：
  - POST /api/{resource} - 创建
  - GET /api/{resource} - 列表查询
  - GET /api/{resource}/{id} - 详情查询
  - PUT /api/{resource}/{id} - 更新
  - DELETE /api/{resource}/{id} - 删除
- **业务操作端点**：
  - POST /api/borrowing/{book_id}/borrow - 借书
  - POST /api/borrowing/{book_id}/return - 还书
  - POST /api/reservations/{book_id}/reserve - 预约
  - POST /api/reservations/{reservation_id}/cancel - 取消预约
- **查询参数标准**：
  - skip: int = 0 (分页偏移)
  - limit: int = 100 (分页大小)
  - status: Optional[Enum] (状态过滤)
- **响应模型规范**：所有响应使用统一包装格式，包含code、message、data字段

## 实现细节（需验证）
- **项目根目录结构**：
  ```
  output/mda_dual_agent_demo/
  ├── main.py                 # FastAPI应用入口
  ├── requirements.txt        # 项目依赖
  ├── pytest.ini             # pytest配置
  ├── pyproject.toml         # 项目配置
  ├── .env.example          # 环境变量模板
  ├── Dockerfile             # Docker配置
  ├── docker-compose.yml     # Docker编排
  ├── verify_project.py      # 项目验证脚本
  ├── run.py                # 启动脚本
  ├── test.py               # 测试脚本
  └── app/
      ├── __init__.py
      ├── database.py        # 数据库连接配置
      ├── dependencies.py    # 依赖注入
      ├── models/
      │   ├── __init__.py
      │   ├── enums.py       # 枚举定义
      │   └── database.py    # SQLAlchemy模型
      ├── routers/
      │   ├── __init__.py
      │   ├── books.py       # 图书路由
      │   ├── readers.py     # 读者路由
      │   ├── borrowing.py   # 借阅路由
      │   └── reservations.py # 预约路由
      ├── services/
      │   ├── __init__.py
      │   ├── book_service.py
      │   ├── reader_service.py
      │   ├── borrowing_service.py
      │   └── reservation_service.py
      ├── repositories/
      │   ├── __init__.py
      │   ├── book_repository.py
      │   ├── reader_repository.py
      │   ├── borrow