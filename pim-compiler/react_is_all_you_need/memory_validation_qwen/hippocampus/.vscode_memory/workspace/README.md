# 简单的Python Web应用

这是一个使用Flask框架构建的简单Web应用示例。

## 功能特性

- 主页显示欢迎信息
- 提供RESTful API接口
- 支持JSON数据交换

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 上运行。

## API接口

### 获取欢迎信息

```
GET /api/hello
```

返回:
```json
{
  "message": "Hello, World!",
  "status": "success"
}
```

### 回显数据

```
POST /api/echo
```

请求体:
```json
{
  "your_data": "value"
}
```

返回:
```json
{
  "received": {
    "your_data": "value"
  },
  "status": "success"
}
```