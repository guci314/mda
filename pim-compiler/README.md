# PIM Compiler v3.0

将平台无关模型（PIM）自动转换为可执行代码的智能编译器，完全基于 Gemini CLI 实现。

## 特性

- 🚀 **一键编译**：从业务模型直接生成可运行的代码
- 🤖 **纯 AI 驱动**：使用 Gemini CLI 完成整个编译流程
- 🎯 **多平台支持**：FastAPI、Django、Flask、Spring Boot、Express.js
- 🔧 **自动修复**：自动运行测试并修复常见问题
- 📦 **完整项目**：生成包含测试、文档、配置的完整项目
- ⚡ **实时进度**：编译过程中显示文件生成进度
- 🧠 **智能理解**：理解自然语言业务描述，无需学习特殊语法

## 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/your-repo/pim-compiler.git
cd pim-compiler

# 运行安装脚本
./install.sh

# 或手动安装
pip install requests python-dotenv
chmod +x pim-compiler
```

### 2. 配置

创建 `.env` 文件配置 Gemini：

```bash
# Gemini API 配置
GEMINI_API_KEY=your-api-key
# 或使用 Google API Key
GOOGLE_API_KEY=your-google-api-key

# 可选：指定模型
GEMINI_MODEL=gemini-2.0-flash-exp  # 或 gemini-2.5-pro
```

### 3. 创建 PIM 文件

创建一个描述业务模型的 Markdown 文件，例如 `todo.md`：

```markdown
# 待办事项管理系统

## 业务描述
一个简单的任务管理系统，帮助用户跟踪待办事项。

## 业务实体

### 待办事项 (Todo)
用户需要完成的任务。

属性：
- 标题：任务的简短描述
- 描述：详细说明（可选）
- 状态：待办/完成
- 优先级：高/中/低
- 截止日期：应完成日期

## 业务服务

### 待办事项服务
- 创建待办事项
- 更新待办事项
- 标记为完成
- 删除待办事项
- 查询待办事项（支持按状态、优先级筛选）
```

### 4. 编译

```bash
# 基本用法
./pim-compiler todo.md

# 指定输出目录
./pim-compiler todo.md -o ./my-todo-app

# 生成 Django 项目
./pim-compiler todo.md -p django

# 跳过自动测试（更快）
./pim-compiler todo.md --no-test

# 显示详细日志
./pim-compiler todo.md -v
```

### 5. 运行生成的代码

```bash
# 进入生成的项目目录
cd output/generated/todo

# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py  # FastAPI
# 或
python manage.py runserver  # Django

# 访问 API 文档
# FastAPI: http://localhost:8000/docs
# Django: http://localhost:8000/api/docs
```

## 命令行选项

```
pim-compiler [选项] PIM文件

选项：
  -h, --help            显示帮助信息
  -o OUTPUT             输出目录（默认：./output）
  -p PLATFORM           目标平台：fastapi, django, flask, spring, express
  --model MODEL         Gemini 模型（默认：从环境变量读取）
  --no-test             跳过自动测试和修复
  --no-lint             跳过代码检查
  -v, --verbose         显示详细日志
  --version             显示版本信息
```

## PIM 文件格式

PIM（Platform Independent Model）文件使用 Markdown 格式编写，描述业务领域模型。

### 基本结构

```markdown
# 系统名称

## 业务描述
系统的整体描述和目标。

## 业务实体
定义系统中的核心实体及其属性。

### 实体名称
实体的描述。

属性：
- 属性1：描述
- 属性2：描述

## 业务服务
定义系统提供的业务功能。

### 服务名称
服务的方法列表：
- 方法1：描述
- 方法2：描述

## 业务规则（可选）
描述特殊的业务约束和规则。

## 业务流程（可选）
描述复杂的业务流程。
```

### 完整示例

查看 `examples/` 目录中的示例：
- `blog.md` - 博客系统
- `ecommerce.md` - 电商系统  
- `task_manager.md` - 任务管理系统

## 生成的项目结构

### FastAPI 项目（默认）

```
generated/project_name/
├── app/                  # 或 src/
│   ├── __init__.py
│   ├── main.py          # 应用入口
│   ├── models/          # SQLAlchemy 数据模型
│   ├── schemas/         # Pydantic 数据验证
│   ├── api/             # API 路由
│   ├── services/        # 业务逻辑
│   └── core/            # 核心配置
├── tests/               # 单元测试
├── alembic/             # 数据库迁移
├── .env.example         # 环境变量示例
├── .gitignore           # Git 忽略文件
├── requirements.txt     # Python 依赖
└── README.md           # 项目文档
```

### 生成的代码特性

- ✅ 现代 Python（类型提示、async/await）
- ✅ RESTful API 设计
- ✅ 自动生成 OpenAPI 文档
- ✅ 数据库迁移支持（Alembic）
- ✅ 完整的 CRUD 操作
- ✅ 输入验证和错误处理
- ✅ 日志记录（使用 loguru）
- ✅ 单元测试框架
- ✅ 环境变量配置
- ✅ Docker 支持（如果需要）

## 工作原理

```
PIM (Markdown)
    ↓
[Gemini CLI 读取并理解]
    ↓
PSM (Platform Specific Model)
    ↓
[Gemini CLI 生成代码]
    ↓
完整的项目代码
    ↓
[自动测试和修复]
    ↓
可运行的应用
```

1. **PIM 解析**：Gemini CLI 读取并理解 Markdown 格式的业务模型
2. **PSM 生成**：生成包含技术细节的平台特定模型
3. **代码生成**：基于 PSM 生成完整的项目代码
4. **质量保证**：自动运行 lint 和测试，修复常见问题

## 高级用法

### 批量编译

```bash
# 编译目录下所有 PIM 文件
for pim in models/*.md; do
    ./pim-compiler "$pim" -o "output/$(basename $pim .md)"
done
```

### CI/CD 集成

```yaml
# GitHub Actions 示例
- name: Compile PIM to Code
  run: |
    ./pim-compiler model.md -o ./generated --no-test
    cd generated
    pip install -r requirements.txt
    pytest
```

### 自定义平台配置

通过环境变量自定义生成行为：

```bash
# 自定义数据库
export PIM_DATABASE=mysql

# 自定义认证方式  
export PIM_AUTH_TYPE=jwt

# 运行编译
./pim-compiler model.md
```

## 性能指标

基于实际测试：
- 简单模型（<5个实体）：2-3 分钟
- 中等模型（5-10个实体）：3-5 分钟  
- 复杂模型（>10个实体）：5-7 分钟

编译时间分配：
- PSM 生成：~40%
- 代码生成：~60%

## 常见问题

### Q: 编译失败怎么办？
A: 
1. 检查 `.env` 文件中的 API 密钥
2. 确保网络连接正常
3. 使用 `-v` 查看详细错误信息
4. 检查 PIM 文件格式是否正确

### Q: 生成的代码质量如何？
A: 生成的代码：
- 遵循行业最佳实践
- 包含完整的错误处理
- 有适当的日志记录
- 包含单元测试
- 可直接用于生产环境

### Q: 可以修改生成的代码吗？
A: 当然！生成的代码完全属于你，可以自由修改和扩展。建议：
1. 先运行生成的代码确保正常
2. 使用版本控制跟踪修改
3. 保留原始 PIM 文件以便重新生成

### Q: 支持哪些数据库？
A: 
- 开发环境：SQLite（默认）
- 生产环境：PostgreSQL（推荐）
- 其他：MySQL、MariaDB（通过修改配置）

### Q: 如何处理认证和授权？
A: 生成的代码包含基础认证框架，你可以根据需要扩展：
- JWT 令牌认证
- Session 认证
- OAuth2 集成

## 版本历史

- v3.0.0 - 完全基于 Gemini CLI，移除其他 LLM 依赖
- v2.0.0 - 添加多 LLM 支持和代码生成
- v1.0.0 - 初始版本

## 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

### 开发环境设置

```bash
# 克隆仓库
git clone <repo-url>
cd pim-compiler

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 支持

- 📧 Email: support@pim-compiler.com
- 💬 Discord: [加入社区](https://discord.gg/pim-compiler)
- 📚 文档：[在线文档](https://docs.pim-compiler.com)
- 🐛 问题：[GitHub Issues](https://github.com/your-repo/pim-compiler/issues)

## 致谢

- [Google Gemini](https://gemini.google.com/) - AI 模型
- [Gemini CLI](https://github.com/google/gemini-cli) - AI 代理引擎
- 所有贡献者和用户

---

**Made with ❤️ by the PIM Compiler Team**