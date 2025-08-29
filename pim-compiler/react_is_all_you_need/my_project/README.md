# 博客系统API

基于FastAPI构建的博客系统，支持文章、分类和评论管理。

## 功能特性

- **文章管理**：创建、更新、删除、发布文章
- **分类管理**：创建、更新、删除分类
- **评论系统**：创建、审核、屏蔽评论
- **RESTful API**：符合REST设计原则的API接口
- **数据验证**：使用Pydantic进行数据验证
- **单元测试**：完整的unittest测试套件

## 项目结构

```
blog-api/
├── main.py              # 主应用入口
├── database.py          # 数据库配置
├── requirements.txt     # 依赖列表
├── run_tests.py        # 测试运行脚本
├── .env.example        # 环境变量示例
├── models/             # 数据库模型
│   ├── article.py
│   ├── category.py
│   ├── comment.py
│   └── __init__.py
├── schemas/            # 数据验证模式
│   ├── article.py
│   ├── category.py
│   ├── comment.py
│   └── __init__.py
├── routers/            # API路由
│   ├── articles.py
│   ├── categories.py
│   ├── comments.py
│   └── __init__.py
├── services/           # 业务逻辑层
│   ├── article_service.py
│   ├── category_service.py
│   ├── comment_service.py
│   └── __init__.py
└── tests/              # 单元测试
    ├── test_articles.py
    ├── test_categories.py
    ├── test_comments.py
    ├── test_main.py
    └── __init__.py
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd blog-api

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行应用

```bash
# 直接运行
python main.py

# 或使用uvicorn
uvicorn main:app --reload
```

### 3. 访问API文档

启动后访问：http://localhost:8000/docs

## API端点

### 文章管理
- `POST /api/v1/articles/` - 创建文章
- `GET /api/v1/articles/` - 获取文章列表
- `GET /api/v1/articles/{id}` - 获取单篇文章
- `PUT /api/v1/articles/{id}` - 更新文章
- `DELETE /api/v1/articles/{id}` - 删除文章
- `POST /api/v1/articles/{id}/publish` - 发布文章
- `POST /api/v1/articles/{id}/increment-view` - 增加浏览量

### 分类管理
- `POST /api/v1/categories/` - 创建分类
- `GET /api/v1/categories/` - 获取分类列表
- `GET /api/v1/categories/{id}` - 获取单个分类
- `PUT /api/v1/categories/{id}` - 更新分类
- `DELETE /api/v1/categories/{id}` - 删除分类

### 评论管理
- `POST /api/v1/comments/` - 创建评论
- `GET /api/v1/comments/` - 获取评论列表
- `GET /api/v1/comments/{id}` - 获取单个评论
- `PUT /api/v1/comments/{id}` - 更新评论
- `DELETE /api/v1/comments/{id}` - 删除评论
- `POST /api/v1/comments/{id}/approve` - 审核通过评论
- `POST /api/v1/comments/{id}/block` - 屏蔽评论

## 运行测试

```bash
# 运行所有测试
python run_tests.py

# 或运行特定测试
python -m unittest tests.test_articles
python -m unittest tests.test_categories
python -m unittest tests.test_comments
```

## 环境变量

复制 `.env.example` 为 `.env` 并根据需要修改：

```bash
cp .env.example .env
```

## 技术栈

- **FastAPI**: 现代、快速的Web框架
- **SQLAlchemy**: Python SQL工具包和ORM
- **SQLite**: 轻量级数据库（可替换为PostgreSQL/MySQL）
- **Pydantic**: 数据验证和设置管理
- **unittest**: Python标准库测试框架

## 开发规范

- 使用Pydantic进行数据验证
- 遵循RESTful API设计原则
- 使用三层架构：路由层、服务层、数据层
- 为每个功能编写单元测试
- 使用类型注解提高代码可读性

## 扩展建议

- 添加用户认证和授权
- 实现文章搜索功能
- 添加文章标签系统
- 实现文章点赞功能
- 添加文件上传功能
- 实现缓存机制
- 添加日志系统