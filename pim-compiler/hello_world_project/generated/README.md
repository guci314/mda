# Hello World FastAPI 项目

## 项目介绍
这是一个简单的 Hello World 服务，使用 FastAPI 框架实现。包含三个API端点：根路径问候、个性化问候和健康检查。

## 技术栈
- 框架：FastAPI
- Python 版本：3.8+
- 依赖：fastapi, uvicorn

## 安装
1. 创建虚拟环境：
```bash
python -m venv venv
```
2. 激活虚拟环境：
```bash
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```
3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API文档
启动服务后，访问以下URL查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 端点说明
1. GET `/` - 根路径问候
2. GET `/hello/{name}` - 个性化问候
3. GET `/health` - 健康检查