```markdown
# 知识库

## 元知识
- **依赖版本诊断**：当遇到`ImportError`时，优先检查相关库的版本兼容性，特别是主要依赖（如`pydantic`）的版本变更可能导致API不兼容
- **测试路径验证**：当测试返回404时，需同时检查路由注册路径和测试期望路径的一致性
- **API响应验证**：当测试返回422状态码时，表明请求数据验证失败，应检查请求数据格式与Pydantic模型的匹配性
- **模块导入错误排查**：遇到`ModuleNotFoundError`时，需检查目录结构和导入路径的匹配性
- **路由匹配验证**：测试失败时需验证路由前缀设置与测试请求路径的一致性

## 原理与设计
- **Pydantic版本兼容性**：项目使用Pydantic 1.x版本，需注意2.x版本的重大变更（如`Undefined`移除）
- **路由前缀设计**：路由前缀应在`include_router`时统一设置，避免在router文件中重复设置
- **请求验证原则**：所有API端点应使用Pydantic模型进行请求数据验证
- **分层路由设计**：API路由应通过`APIRouter`实现，并在主应用中统一注册

## 接口与API
- **Pydantic版本管理**：
  ```bash
  pip install pydantic==1.10.7
  ```
- **FastAPI路由注册**：
  ```python
  app.include_router(articles.router, prefix="/api/articles")
  ```
- **测试客户端使用**：
  ```python
  client.post("/api/articles/", json={"title": "Test", "content": "..."})
  ```
- **APIRouter基础用法**：
  ```python
  router = APIRouter()
  @router.post("/")
  ```

## 实现细节（需验证）
- **项目结构调整**：
  ```
  app/
  ├── api/
  │   ├── articles.py  # 实现/articles端点
  │   └── comments.py
  ├── main.py         # 路由注册入口
  ```
- **Pydantic模型位置**：请求/响应模型应定义在`schemas.py`中
- **测试文件结构**：测试文件应通过`TestClient`访问统一前缀的API路径
- **路由实现模式**：端点实现应返回测试期望的完整字段结构

## 用户偏好与项目特点
- **严格版本控制**：项目锁定特定版本的依赖（如Pydantic 1.x）
- **统一路由前缀**：所有API路由必须使用`/api/`前缀
- **测试驱动开发**：测试文件定义了严格的API契约（路径、响应格式）
- **分层架构**：路由实现与模型定义分离
```