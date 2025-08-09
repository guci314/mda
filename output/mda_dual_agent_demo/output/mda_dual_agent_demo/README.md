# 图书借阅系统 API

基于 FastAPI 的图书借阅管理系统，提供完整的图书、读者、借阅、预约管理功能。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 检查项目

```bash
python check.py
```

### 3. 启动服务

```bash
python run.py
```

或者使用 uvicorn 直接启动：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API根路径: http://localhost:8000/

## 🧪 运行测试

### 运行所有测试

```bash
python test.py
```

或者使用 pytest：

```bash
pytest tests/ -v
```

### 运行特定测试

```bash
python test.py books        # 测试图书模块
python test.py readers      # 测试读者模块
python test.py borrows      # 测试借阅模块
python test.py reservations # 测试预约模块
```

## 📁 项目结构

```
mda_dual_agent_demo/
├── main.py                 # FastAPI应用入口
├── run.py                  # 启动脚本
├── test.py                 # 测试脚本
├── check.py                # 项目检查脚本
├── requirements.txt        # 项目依赖
├── README.md              # 项目说明
├── .env.example           # 环境变量示例
├── Dockerfile             # Docker配置
├── docker-compose.yml     # Docker Compose配置
├── app/                   # 应用代码
│   ├── __init__.py
│   ├── database.py        # 数据库连接配置
│   ├── dependencies.py    # 依赖注入配置
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   ├── database.py    # SQLAlchemy ORM模型
│   │   ├── pydantic.py    # Pydantic DTO模型
│   │   └── enums.py       # 枚举定义
│   ├── routers/           # API路由
│   │   ├── __init__.py
│   │   ├── books.py       # 图书路由
│   │   ├── readers.py     # 读者路由
│   │   ├── borrows.py     # 借阅路由
│   │   └── reservations.py # 预约路由
│   ├── services/          # 业务服务层
│   │   ├── __init__.py
│   │   ├── book_service.py
│   │   ├── reader_service.py
│   │   ├── borrow_service.py
│   │   └── reservation_service.py
│   └── repositories/      # 数据仓储层
│       ├── __init__.py
│       ├── book_repository.py
│       ├── reader_repository.py
│       ├── borrow_repository.py
│       └── reservation_repository.py
└── tests/                 # 测试代码
    ├── __init__.py
    ├── conftest.py        # pytest配置
    ├── test_main.py       # 主应用测试
    ├── test_books.py      # 图书测试
    ├── test_readers.py    # 读者测试
    ├── test_borrows.py    # 借阅测试
    └── test_reservations.py # 预约测试
```

## 📚 API 功能

### 图书管理 (`/books`)

- `POST /books/` - 创建图书
- `GET /books/` - 获取图书列表
- `GET /books/{isbn}` - 获取图书详情
- `PUT /books/{isbn}` - 更新图书信息
- `DELETE /books/{isbn}` - 下架图书
- `GET /books/search/title` - 按书名搜索
- `GET /books/search/author` - 按作者搜索
- `GET /books/search/category` - 按分类搜索
- `GET /books/available/list` - 获取可借图书
- `GET /books/{isbn}/availability` - 检查图书可借状态
- `GET /books/stats/count` - 获取图书统计

### 读者管理 (`/readers`)

- `POST /readers/` - 注册读者
- `GET /readers/` - 获取读者列表
- `GET /readers/{reader_id}` - 获取读者详情
- `PUT /readers/{reader_id}` - 更新读者信息
- `DELETE /readers/{reader_id}` - 注销读者
- `GET /readers/search/name` - 按姓名搜索读者
- `GET /readers/{reader_id}/status` - 获取读者状态
- `POST /readers/{reader_id}/activate` - 激活读者
- `POST /readers/{reader_id}/suspend` - 暂停读者
- `GET /readers/stats/count` - 获取读者统计

### 借阅管理 (`/borrows`)

- `POST /borrows/` - 借阅图书
- `POST /borrows/simple` - 简化借阅接口
- `GET /borrows/` - 获取借阅记录列表
- `GET /borrows/{borrow_id}` - 获取借阅记录详情
- `GET /borrows/reader/{reader_id}` - 获取读者借阅记录
- `GET /borrows/reader/{reader_id}/active` - 获取读者活跃借阅
- `GET /borrows/book/{isbn}` - 获取图书借阅记录
- `POST /borrows/{borrow_id}/return` - 归还图书
- `POST /borrows/{borrow_id}/renew` - 续借图书
- `POST /borrows/{borrow_id}/overdue` - 标记逾期
- `POST /borrows/{borrow_id}/lost` - 标记丢失
- `GET /borrows/overdue/list` - 获取逾期记录
- `POST /borrows/process/overdue` - 处理逾期图书
- `GET /borrows/stats/count` - 获取借阅统计

### 预约管理 (`/reservations`)

- `POST /reservations/` - 预约图书
- `GET /reservations/` - 获取预约记录列表
- `GET /reservations/{reservation_id}` - 获取预约记录详情
- `GET /reservations/reader/{reader_id}` - 获取读者预约记录
- `GET /reservations/book/{isbn}` - 获取图书预约记录
- `POST /reservations/{reservation_id}/cancel` - 取消预约
- `POST /reservations/{reservation_id}/fulfill` - 完成预约
- `POST /reservations/{reservation_id}/expire` - 过期预约
- `GET /reservations/pending/list` - 获取待处理预约
- `POST /reservations/process/expired` - 处理过期预约
- `GET /reservations/stats/count` - 获取预约统计

## 🔧 配置

### 环境变量

创建 `.env` 文件（参考 `.env.example`）：

```env
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./library_borrowing_system.db

# 服务配置
HOST=0.0.0.0
PORT=8000
RELOAD=true

# 日志配置
LOG_LEVEL=info
```

### 数据库

默认使用 SQLite 数据库，支持以下数据库：

- SQLite (默认): `sqlite+aiosqlite:///./database.db`
- PostgreSQL: `postgresql+asyncpg://user:pass@localhost/dbname`
- MySQL: `mysql+aiomysql://user:pass@localhost/dbname`

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
docker-compose up -d
```

### 使用 Docker

```bash
# 构建镜像
docker build -t library-api .

# 运行容器
docker run -p 8000:8000 library-api
```

## 🧪 测试覆盖

项目包含完整的测试用例，覆盖：

- ✅ 所有 API 端点
- ✅ 数据验证
- ✅ 错误处理
- ✅ 业务逻辑
- ✅ 边界条件

测试使用内存 SQLite 数据库，确保测试隔离和快速执行。

## 📊 性能特性

- 🚀 异步处理 - 基于 FastAPI 和 SQLAlchemy 异步引擎
- 📝 自动文档 - Swagger UI 和 ReDoc
- 🔍 数据验证 - Pydantic 模型验证
- 🏗️ 分层架构 - Repository-Service-Router 三层分离
- 🔄 依赖注入 - FastAPI 依赖注入系统
- 📊 错误处理 - 统一错误响应格式

## 🤝 开发指南

### 添加新功能

1. 在 `app/models/` 中定义数据模型
2. 在 `app/repositories/` 中实现数据访问层
3. 在 `app/services/` 中实现业务逻辑层
4. 在 `app/routers/` 中实现 API 路由
5. 在 `tests/` 中添加测试用例

### 代码规范

- 使用 Python 类型注解
- 遵循 PEP 8 代码风格
- 编写完整的文档字符串
- 保持测试覆盖率

## 📄 许可证

MIT License

## 🆘 问题排查

### 常见问题

1. **端口被占用**
   ```bash
   # 更换端口启动
   PORT=8001 python run.py
   ```

2. **依赖包缺失**
   ```bash
   pip install -r requirements.txt
   ```

3. **数据库连接失败**
   - 检查 DATABASE_URL 配置
   - 确保数据库服务运行正常

4. **测试失败**
   ```bash
   # 清理测试环境
   rm -f test_*.db
   python test.py
   ```

### 获取帮助

- 查看 API 文档: http://localhost:8000/docs
- 运行项目检查: `python check.py`
- 查看日志输出获取详细错误信息