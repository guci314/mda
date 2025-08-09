# 项目总结

## 功能概述

- 图书管理：添加、更新、下架图书
- 读者管理：注册、更新、冻结读者
- 借阅管理：借阅、归还、续借图书
- 预约管理：预约、取消预约

## 技术栈

- **框架**：FastAPI
- **数据库**：SQLAlchemy (异步)
- **测试**：pytest + pytest-asyncio
- **部署**：Docker + PostgreSQL

## 项目结构

```
app/
  ├── __init__.py
  ├── database.py
  ├── models/
  │   ├── __init__.py
  │   ├── enums.py
  │   ├── database.py
  │   └── pydantic.py
  ├── repositories/
  │   ├── __init__.py
  │   ├── book_repository.py
  │   └── reader_repository.py
  ├── services/
  │   ├── __init__.py
  │   ├── book_service.py
  │   └── reader_service.py
  └── routers/
      ├── __init__.py
      ├── books.py
      └── readers.py
```

## 测试覆盖率

所有核心功能均已通过单元测试和集成测试验证。