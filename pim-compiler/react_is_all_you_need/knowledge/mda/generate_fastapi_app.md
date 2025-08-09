# FastAPI 应用生成完整指南

## 工作流概述

本指南定义了从 PSM 生成 FastAPI 应用的完整工作流程。

## 工作流函数

### `generate_fastapi_from_psm(psm_file: str) -> bool`

执行从 PSM 文档生成 FastAPI 应用的完整工作流。

**参数:**
- `psm_file`: PSM 文档文件名（如 library_borrowing_system_psm.md）

**返回:**
- `bool`: 生成和测试是否成功

## 工作流步骤

### 第一阶段：分析与准备

#### 1.1 读取知识文件
- 读取 `/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/mda/fastapi_generation_knowledge.md`
- 获取 FastAPI 代码生成的核心知识、模板和最佳实践
- 理解项目结构规范、代码生成规范和依赖管理要求

#### 1.2 读取 PSM 文档
- 在工作目录中查找 PSM 文档（文件名模式：`*_psm.md`）
- 提取关键信息：
  - 数据模型定义
  - API 端点规范
  - 业务规则说明
  - 认证授权要求

#### 1.3 制定生成计划
- 根据 PSM 内容规划生成顺序
- 确定需要创建的模块和文件
- 识别模型之间的依赖关系

### 第二阶段：代码生成

#### 2.1 创建项目结构
```
app/
├── __init__.py          # Python 包标识
├── main.py              # 应用入口
├── config.py            # 配置管理
├── database.py          # 数据库设置
├── models/              # ORM 模型
├── schemas/             # Pydantic 模型
├── routers/             # API 路由
├── services/            # 业务逻辑
├── utils/               # 工具函数
└── tests/               # 测试代码
```

#### 2.2 生成顺序
1. **基础设施层**
   - `database.py` - 数据库连接配置
   - `config.py` - 应用配置管理

2. **数据层**
   - `models/*.py` - 根据 PSM 数据模型生成 SQLAlchemy 模型
   - `schemas/*.py` - 生成对应的 Pydantic 验证模型

3. **业务层**
   - `services/*.py` - 实现 PSM 中定义的业务规则

4. **API 层**
   - `routers/*.py` - 根据 PSM 端点定义生成路由
   - `main.py` - 组装应用，注册路由和中间件

5. **测试层**
   - `tests/test_*.py` - 为每个端点生成单元测试
   - `tests/conftest.py` - 测试配置和 fixtures

6. **配置文件**
   - `requirements.txt` - Python 依赖包
   - `.env.example` - 环境变量示例
   - `README.md` - 项目使用说明

### 第三阶段：测试验证

#### 3.1 环境准备
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 3.2 运行测试
```bash
# 执行所有测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=app --cov-report=term-missing
```

#### 3.3 测试检查点
- [ ] 所有测试用例通过
- [ ] 代码覆盖率达标（建议 > 80%）
- [ ] 无 import 错误
- [ ] 数据库连接正常

### 第四阶段：应用运行

#### 4.1 启动服务
```bash
# 开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 4.2 功能验证
1. **健康检查**
   ```bash
   # 注意：访问 localhost 或 127.0.0.1 必须加上 --noproxy 参数
   curl --noproxy "*" http://localhost:8000/
   # 或
   curl --noproxy localhost http://localhost:8000/
   ```

2. **API 文档**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **端点测试**
   ```bash
   # 测试 CRUD 操作（记得加上 --noproxy）
   curl --noproxy "*" http://localhost:8000/api/v1/books
   ```
   - 验证数据持久化
   - 检查错误处理

#### 4.3 运行检查点
- [ ] 应用启动无错误
- [ ] API 文档正确生成
- [ ] 健康检查端点响应 200
- [ ] 所有端点可访问
- [ ] 数据库表已创建
- [ ] 数据操作正常

### 第五阶段：问题排查

#### 5.1 常见问题快速定位

**导入错误**
- 检查：所有目录是否包含 `__init__.py`
- 解决：添加缺失的 `__init__.py` 文件

**数据库连接失败**
- 检查：`DATABASE_URL` 环境变量
- 解决：配置正确的数据库连接字符串

**端口占用**
- 检查：`lsof -i :8000` (Linux/Mac) 或 `netstat -ano | findstr :8000` (Windows)
- 解决：终止占用进程或更换端口

**依赖冲突**
- 检查：`pip list` 查看已安装包版本
- 解决：清理环境重新安装 `pip install -r requirements.txt --force-reinstall`

### 第六阶段：交付确认

#### 6.1 最终检查清单
- [ ] 所有代码文件已生成
- [ ] 单元测试 100% 通过
- [ ] 应用正常启动运行
- [ ] API 文档可访问
- [ ] 主要功能测试通过
- [ ] README 文档完整

#### 6.2 输出报告
生成完成后，提供：
1. 生成文件清单
2. 测试执行报告
3. 应用访问信息
4. 后续维护建议

## 执行原则

1. **聚焦当前步骤** - 每个阶段专注于特定任务
2. **渐进式验证** - 每完成一个模块立即验证
3. **快速失败** - 遇到问题立即报告并修复
4. **保持简洁** - 生成最小可行的代码

## 成功标准

生成任务成功完成的标志：
- ✅ PSM 中所有模型都已实现
- ✅ PSM 中所有端点都已创建
- ✅ 所有测试用例通过
- ✅ 应用可以正常启动
- ✅ API 文档自动生成
- ✅ 核心功能验证通过