# Hello World FastAPI PSM

## 概述
这是一个简单的 Hello World 服务的平台特定模型（PSM），使用 FastAPI 框架实现。

## 技术栈
- 框架：FastAPI
- Python 版本：3.8+
- 依赖：fastapi, uvicorn

## API 设计

### 端点定义

#### 1. 根路径问候
- **路径**: `/`
- **方法**: GET
- **描述**: 返回简单的问候消息
- **响应**:
  ```json
  {
    "message": "Hello World!"
  }
  ```

#### 2. 个性化问候
- **路径**: `/hello/{name}`
- **方法**: GET
- **描述**: 返回个性化的问候消息
- **参数**:
  - `name` (路径参数): 要问候的名字
- **响应**:
  ```json
  {
    "message": "Hello, {name}!",
    "timestamp": "2024-07-25T10:00:00Z"
  }
  ```

#### 3. 健康检查
- **路径**: `/health`
- **方法**: GET
- **描述**: 服务健康状态检查
- **响应**:
  ```json
  {
    "status": "healthy",
    "service": "hello-world-api",
    "version": "1.0.0"
  }
  ```

## 项目结构
```
hello_world_project/
├── main.py          # 主应用文件
├── requirements.txt # 依赖文件
└── README.md       # 项目说明
```

## 实现要求
1. 使用 FastAPI 框架
2. 包含自动生成的 API 文档（Swagger UI）
3. 使用 Pydantic 模型定义响应格式
4. 包含 CORS 中间件支持
5. 使用 uvicorn 作为 ASGI 服务器

## 启动命令
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```