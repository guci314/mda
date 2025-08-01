# 博客系统 PSM

## 数据模型

### Article 表
- id: Integer, Primary Key, 自增
- title: String(200), Not Null
- content: Text, Not Null
- summary: String(500)
- author: String(100), Not Null
- published_at: DateTime
- updated_at: DateTime, Default=now(), OnUpdate=now()
- status: Enum('draft', 'published'), Default='draft'
- view_count: Integer, Default=0
- category_id: Integer, ForeignKey('categories.id')

### Category 表
- id: Integer, Primary Key, 自增
- name: String(50), Unique, Not Null
- description: Text
- article_count: Integer, Default=0

### Comment 表
- id: Integer, Primary Key, 自增
- article_id: Integer, ForeignKey('articles.id'), Not Null
- author_name: String(100), Not Null
- email: String(100), Not Null
- content: Text, Not Null
- published_at: DateTime, Default=now()
- status: Enum('pending', 'published', 'blocked'), Default='pending'

## API 设计

### 文章服务 API
- POST /api/articles - 创建文章（需认证）
- PUT /api/articles/{id} - 更新文章（需认证+授权）
- DELETE /api/articles/{id} - 删除文章（需认证+授权）
- GET /api/articles - 文章列表（分页）
- GET /api/articles/{id} - 文章详情
- GET /api/articles/category/{category_id} - 按分类查询文章
- GET /api/articles/search - 搜索文章（按标题或内容）
- POST /api/articles/{id}/view - 增加浏览量

### 评论服务 API
- POST /api/comments - 发表评论
- PUT /api/comments/{id}/status - 审核评论（需管理员权限）
- DELETE /api/comments/{id} - 删除评论（需管理员权限）
- GET /api/articles/{id}/comments - 获取文章的评论列表