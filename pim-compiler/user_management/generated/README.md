# 用户管理系统

基于FastAPI和PostgreSQL的用户管理系统，提供完整的CRUD功能。

## 功能特性

- 用户创建、查询、更新和删除
- 数据验证和唯一性检查
- 分页查询支持
- 软删除机制

## 技术栈

- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Pydantic数据验证

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
复制.env.example为.env并填写实际值

3. 启动服务：
```bash
uvicorn app.main:app --reload
```

## API文档

启动服务后访问：
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## 项目结构

```
user_management/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI主应用
│   ├── models.py       # SQLAlchemy模型
│   ├── schemas.py      # Pydantic模型
│   ├── crud.py         # CRUD操作
│   ├── api/
│   │   ├── __init__.py
│   │   └── users.py    # 用户路由
│   └── database.py     # 数据库配置
├── requirements.txt    # 依赖清单
└── .env.example        # 环境变量示例
```

## 开发指南

### 数据库迁移

项目使用SQLAlchemy ORM，数据库表结构定义在models.py中。

### 测试

```bash
pytest
```

### 部署

提供Docker支持：
```bash
docker build -t user-management .
docker run -p 8000:8000 user-management
```

## 贡献

欢迎提交Issue和PR。