# FastAPI 博客管理系统

## 项目结构
```
blog_management_output_v2/
├── models/          # 数据模型
├── api/             # API路由
├── database.py      # 数据库配置
├── main.py          # 主应用文件
├── requirements.txt # 依赖文件
├── config.py        # 配置
├── .env.example     # 环境变量示例
└── README.md        # 项目说明
```

## 安装步骤
1. 克隆仓库
2. 创建虚拟环境: `python -m venv venv`
3. 激活虚拟环境:
   - Windows: `venv\Scripts\activate`
   - Unix: `source venv/bin/activate`
4. 安装依赖: `pip install -r requirements.txt`
5. 复制.env.example为.env并配置
6. 运行: `uvicorn main:app --reload`

## API文档
访问 `http://localhost:8000/docs` 查看Swagger文档