# 知识库

## 元知识
- **路由路径调试流程**：检查测试请求路径 → 验证路由注册路径 → 确认前缀匹配 → 检查HTTP方法匹配
- **字段名映射策略**：当Pydantic模型与数据库模型字段名不一致时，使用显式映射而非自动赋值
- **测试路径修正方法**：测试代码中的URL路径必须与路由注册的前缀一致（如 `/api/books/` vs `/books/`）
- **同步/异步代码一致性检查**：路由层使用同步代码时，服务层也必须是同步的，反之亦然
- **模块导入路径验证**：检查 `__init__.py` 是否正确定义了子模块导出，验证 `from package import module` 的可用性

## 原理与设计
- **路由前缀设计**：FastAPI应用采用 `/api` 前缀作为所有REST API的统一入口
- **模型字段命名规范**：数据库模型使用 `publication_year`，API模型使用 `publish_year`，通过服务层进行转换
- **测试路径设计原则**：测试代码应使用完整路径（包含前缀），避免硬编码相对路径
- **路由模块化**：每个业务领域（books/readers/borrows/reservations）拥有独立的路由文件
- **同步异步架构分离**：路由层可以同步，但服务层必须异步，通过依赖注入处理会话

## 接口与API
- **路由注册规范**：
  ```python
  app.include_router(books.router, prefix="/api")
  app.include_router(readers.router, prefix="/api")
  ```
- **字段映射实现**：
  ```python
  book.publication_year = book_data.publish_year
  ```
- **测试路径格式**：所有测试请求必须使用 `/api/{resource}/` 格式
- **路由文件命名**：使用 `{domain}_router.py` 或 `{domain}.py` 两种模式并存
- **HTTP方法覆盖**：需要实现 POST/PUT/DELETE/GET 完整CRUD操作

## 实现细节（需验证）
- **路由文件位置**：`app/routers/` 目录下存在两种命名模式（`books.py` 和 `book_router.py`）
- **模型字段差异**：`BookDB.publication_year` vs `BookCreate.publish_year`
- **路由前缀**：主应用在 `main.py` 中统一添加 `/api` 前缀
- **测试路径修正**：所有测试文件已从 `/books/` 改为 `/api/books/`
- **服务层字段映射**：`app/services/book_service.py` 中需要显式处理字段名映射
- **路由导入问题**：`app/routers/__init__.py` 需要正确导出子模块

## 用户偏好与项目特点
- **严格路径匹配**：测试期望精确的路径，不接受模糊匹配
- **完整CRUD要求**：测试期望所有HTTP方法（POST/PUT/DELETE/GET）都实现
- **前缀一致性**：所有API路由必须使用统一的 `/api` 前缀
- **字段命名分离**：API层和数据库层可以使用不同字段名，通过服务层转换
- **测试驱动验证**：任何路由变更必须同步更新测试中的请求路径