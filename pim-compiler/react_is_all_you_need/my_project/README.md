# Blog API

基于FastAPI的博客系统API，提供文章、分类、评论等管理功能。

## 功能特性

- ✅ 文章管理（创建、读取、更新、删除、发布）
- ✅ 分类管理
- ✅ 评论管理（支持审核）
- ✅ RESTful API设计
- ✅ SQLite数据库
- ✅ 单元测试覆盖
- ✅ OpenAPI文档

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy ORM
- **验证**: Pydantic
- **测试**: unittest
- **文档**: OpenAPI/Swagger

## 项目结构

```
blog_api/
├── main.py                 # 应用入口
├── database.py            # 数据库配置
├── requirements.txt       # 依赖列表
├── run_tests.py          # 测试运行脚本
├── .env.example          # 环境变量示例
├── models/               # 数据模型
│   ├── __init__.py
│   ├── article.py
│   ├── category.py
│   └── comment.py
├── schemas/              # Pydantic模式
│   ├── __init__.py
│   ├── article.py
│   ├── category.py
│   └── comment.py
├── repositories/         # 数据访问层
│   ├── __init__.py
│   ├── article.py
│   ├── category.py
│   └── comment.py
├── services/             # 业务逻辑层
│   ├── __init__.py
│   ├── article.py
│   ├── category.py
│   └── comment.py
├── routers/              # API路由
│   ├── __init__.py
│   ├── article.py
│   ├── category.py
│   └── comment.py
└── tests/                # 单元测试
    ├── __init__.py
    ├── conftest.py
    ├── test_main.py
    ├── test_articles.py
    ├── test_categories.py
    └── test_comments.py
```

## 安装运行

1. 克隆项目
```bash
git clone <repository-url>
cd blog_api
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量（可选）
```bash
cp .env.example .env
# 编辑 .env 文件配置参数
```

4. 运行应用
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. 访问文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API端点

### 文章管理
- `GET /articles/` - 获取文章列表
- `POST /articles/` - 创建文章
- `GET /articles/{id}` - 获取文章详情
- `PUT /articles/{id}` - 更新文章
- `DELETE /articles/{id}` - 删除文章
- `POST /articles/{id}/publish` - 发布文章

### 分类管理
- `GET /categories/` - 获取分类列表
- `POST /categories/` - 创建分类
- `GET /categories/{id}` - 获取分类详情
- `PUT /categories/{id}` - 更新分类
- `DELETE /categories/{id}` - 删除分类

### 评论管理
- `GET /comments/` - 获取评论列表（需article_id参数）
- `POST /comments/` - 创建评论
- `GET /comments/{id}` - 获取评论详情
- `PUT /comments/{id}` - 更新评论状态
- `DELETE /comments/{id}` - 删除评论
- `POST /comments/{id}/publish` - 发布评论
- `POST /comments/{id}/block` - 屏蔽评论

## 测试

运行所有测试：
```bash
python run_tests.py
```

或者使用unittest：
```bash
python -m unittest discover tests/
```

## 开发

### 代码风格
项目遵循PEP8规范，建议使用black进行代码格式化：
```bash
black .
```

### 添加新功能
1. 在对应层添加代码（模型→模式→仓储→服务→路由）
2. 编写单元测试
3. 更新API文档

## 部署

### 生产环境建议
1. 使用PostgreSQL替代SQLite
2. 配置合适的数据库连接池
3. 启用HTTPS
4. 配置反向代理（Nginx）
5. 使用进程管理器（Gunicorn + Uvicorn）
6. 设置监控和日志

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！