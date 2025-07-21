# 任务管理系统 API

这是一个基于 FastAPI 和 SQLAlchemy 2.0 实现的任务管理系统 API。

## 功能

- 任务的增删改查 (CRUD)
- 标签的增删改查 (CRUD)
- 任务与标签的多对多关联
- 按状态、优先级、标签等进行高级查询
- 异步数据库操作

## 技术栈

- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0 (异步)
- **数据库**: PostgreSQL / SQLite
- **数据验证**: Pydantic V2
- **依赖管理**: pip
- **数据库迁移**: Alembic

## 项目设置与运行

### 1. 环境准备

- 安装 Python 3.10+
- (可选) 创建并激活虚拟环境:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/macOS
  # venv\Scripts\activate  # Windows
  ```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 文件为 `.env`，并根据需要修改其中的配置。

```bash
cp .env.example .env
```

默认使用 SQLite 数据库，无需额外配置。如果使用 PostgreSQL，请确保数据库已创建，并更新 `DATABASE_URL`。

### 4. 数据库迁移

使用 Alembic 初始化并升级数据库到最新版本。

```bash
# 这将根据 models 创建第一个迁移脚本
alembic revision --autogenerate -m "Initial migration"

# 这将应用迁移，创建所有表
alembic upgrade head
```

### 5. 运行应用

使用 Uvicorn 启动应用服务器。

```bash
uvicorn app.main:app --reload
```

`--reload` 参数会在代码变更后自动重启服务，适合开发环境。

### 6. 访问 API 文档

服务启动后，在浏览器中访问以下地址即可查看和测试 API：

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 运行测试

使用 `pytest` 运行所有测试。

```bash
pytest
```
