# 图书借阅系统 FastAPI 应用

## 项目概述

这是一个基于FastAPI框架开发的图书借阅系统，提供完整的图书管理、读者管理、借阅管理和预约管理功能。

## 项目结构

```
mda_dual_agent_demo/
├── main.py                 # FastAPI应用入口
├── requirements.txt        # 项目依赖
├── start_server.py         # 服务器启动脚本
├── pytest.ini             # pytest配置
├── pyproject.toml          # 项目配置
├── README.md               # 项目说明
├── app/                    # 应用核心代码
│   ├── __init__.py
│   ├── database.py         # 数据库连接配置
│   ├── dependencies.py     # 依赖注入
│   ├── enums.py           # 枚举定义
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   ├── database.py    # SQLAlchemy ORM模型
│   │   ├── pydantic.py    # Pydantic DTO模型
│   │   ├── enums.py       # 模型枚举
│   │   ├── book.py        # 图书模型
│   │   ├── reader.py      # 读者模型
│   │   ├── borrow_record.py # 借阅记录模型
│   │   └── reservation_record.py # 预约记录模型
│   ├── repositories/      # 数据访问层
│   │   ├── __init__.py
│   │   ├── book_repository.py
│   │   ├── reader_repository.py
│   │   ├── borrow_repository.py
│   │   └── reservation_repository.py
│   ├── services/          # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── book_service.py
│   │   ├── reader_service.py
│   │   ├── borrow_service.py
│   │   └── reservation_service.py
│   ├── routers/           # API路由
│   │   ├── __init__.py
│   │   ├── books.py
│   │   ├── readers.py
│   │   ├── borrows.py
│   │   └── reservations.py
│   └── schemas/           # API模式定义
│       └── __init__.py
└── tests/                 # 测试用例
    ├── __init__.py
    ├── conftest.py        # pytest配置
    ├── test_simple.py     # 简单测试用例
    ├── test_main.py       # 主应用测试
    ├── test_books.py      # 图书API测试
    ├── test_readers.py    # 读者API测试
    ├── test_borrows.py    # 借阅API测试
    └── test_reservations.py # 预约API测试
```

## 核心功能

### 1. 图书管理
- 图书信息的增删改查
- 图书搜索（按标题、作者、分类）
- 图书可用性检查
- 图书统计信息

### 2. 读者管理
- 读者注册和信息管理
- 读者状态管理（正常、冻结、删除）
- 读者信用评分管理
- 读者统计信息

### 3. 借阅管理
- 图书借阅和归还
- 借阅记录查询
- 借阅续期
- 逾期处理
- 借阅统计

### 4. 预约管理
- 图书预约
- 预约队列管理
- 预约通知
- 预约完成和取消

## 技术栈

- **Web框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL (支持异步)
- **ORM**: SQLAlchemy 2.0.23 (异步)
- **数据验证**: Pydantic 2.5.0
- **测试框架**: pytest 7.4.3 + pytest-asyncio
- **ASGI服务器**: uvicorn 0.24.0
- **数据库迁移**: Alembic 1.13.0

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

创建 `.env` 文件：

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost/library_db
```

### 3. 启动服务器

```bash
# 方式1：使用启动脚本
python start_server.py

# 方式2：直接使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 运行测试

```bash
# 运行所有测试
pytest

# 运行简单测试
pytest tests/test_simple.py -v

# 运行特定模块测试
pytest tests/test_books.py -v
```

## API端点

### 图书管理
- `POST /books/` - 创建图书
- `GET /books/` - 获取图书列表
- `GET /books/{isbn}` - 获取图书详情
- `PUT /books/{isbn}` - 更新图书信息
- `DELETE /books/{isbn}` - 删除图书
- `GET /books/search/title` - 按标题搜索
- `GET /books/search/author` - 按作者搜索
- `GET /books/available/list` - 获取可借图书

### 读者管理
- `POST /readers/` - 注册读者
- `GET /readers/` - 获取读者列表
- `GET /readers/{reader_id}` - 获取读者详情
- `PUT /readers/{reader_id}` - 更新读者信息
- `POST /readers/{reader_id}/freeze` - 冻结读者
- `POST /readers/{reader_id}/unfreeze` - 解冻读者

### 借阅管理
- `POST /borrows/` - 借阅图书
- `GET /borrows/` - 获取借阅记录
- `POST /borrows/{borrow_id}/return` - 归还图书
- `POST /borrows/{borrow_id}/renew` - 续借图书
- `GET /borrows/overdue/list` - 获取逾期借阅

### 预约管理
- `POST /reservations/` - 预约图书
- `GET /reservations/` - 获取预约记录
- `POST /reservations/{reservation_id}/cancel` - 取消预约
- `GET /reservations/ready/list` - 获取可取图书

## 数据模型

### 图书 (Book)
- ISBN、标题、作者、出版社
- 出版年份、分类、库存数量
- 位置、描述、状态

### 读者 (Reader)
- 读者ID、姓名、身份证号
- 电话、邮箱、读者类型
- 状态、信用评分、注册时间

### 借阅记录 (BorrowRecord)
- 借阅ID、图书ISBN、读者ID
- 借阅时间、应还时间、实际还书时间
- 续借次数、状态、备注

### 预约记录 (ReservationRecord)
- 预约ID、图书ISBN、读者ID
- 预约时间、状态、优先级
- 通知时间、过期时间

## 开发说明

### 架构设计
- **分层架构**: Repository -> Service -> Router
- **依赖注入**: 使用FastAPI的Depends机制
- **异步编程**: 全面支持异步操作
- **类型安全**: 使用Pydantic进行数据验证

### 代码规范
- 使用Python类型提示
- 遵循PEP 8代码风格
- 完整的文档字符串
- 单元测试覆盖

### 扩展建议
- 添加用户认证和授权
- 实现图书推荐系统
- 添加邮件/短信通知
- 集成支付系统（罚金）
- 添加图书评价功能

## 许可证

MIT License