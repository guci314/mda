"""
编译器提示词常量
"""

# PSM 生成提示词模板
PSM_GENERATION_PROMPT = """将 {pim_file} 文件中的 PIM 转换为 {platform} 平台的 PSM，并直接创建 {psm_file} 文件。不要询问，直接生成完整的PSM文档。

技术栈：
- 框架：{framework}
- 数据库：SQLite（默认）
- ORM：{orm} 2.0
- 数据验证：{validation_lib} v2

PSM 文档结构要求：
1. 数据模型定义（SQLAlchemy）
   - 使用 declarative_base()
   - 包含所有实体的表定义
   - 正确设置主键、外键关系
   - 使用 relationship() 定义关联

2. API Schema 定义（Pydantic）
   - 为每个实体创建 Base/Create/Update/InDB 模型
   - 使用 model_config = ConfigDict(from_attributes=True)
   - 定义请求和响应模型

3. CRUD 操作接口
   - 为每个实体定义标准 CRUD 方法
   - create, get, get_multi, update, delete

4. REST API 端点
   - 遵循 RESTful 设计原则
   - 使用正确的 HTTP 方法和状态码
   - 路径格式：/api/v1/实体名称（复数）

5. 服务层定义
   - 业务逻辑封装
   - 事务处理
   - 错误处理

输出格式：Markdown 文档，使用代码块标注语言类型。

重要：直接生成完整的PSM文档内容到 {psm_file} 文件中，不要只是描述计划或询问确认。"""

# 代码生成提示词
CODE_GENERATION_PROMPT = "根据 {psm_file} 文件生成 FastAPI 代码。参考 GEMINI_KNOWLEDGE.md 中的规范。创建所有必要的文件和文件夹。"

# 测试修复提示词模板
TEST_FIX_PROMPT = """运行 pytest 失败，需要修复测试错误。参考 GEMINI_KNOWLEDGE.md 中的规范。

这是第 {attempt} 次尝试（最多 5 次）。

错误信息：
{errors}

错误类型分析：
{error_types}

请分析错误原因并修复代码，确保：
1. 修复所有测试失败
2. 不要破坏已通过的测试
3. 保持代码质量和规范
4. 优先修复语法错误，然后是导入错误，最后是逻辑错误
5. **Pydantic v2 相关错误修复**：
   - 如果遇到 "Config" and "model_config" cannot be used together 错误：
     * 删除旧的 `class Config:` 内部类
     * 使用 `model_config = ConfigDict(...)` 替代
   - 如果遇到 BaseSettings 导入错误：
     * 使用 `from pydantic_settings import BaseSettings, SettingsConfigDict`
   - 如果遇到验证器错误：
     * 使用 `@field_validator` 而不是 `@validator`
     * 验证器方法需要 `@classmethod` 装饰器
"""

# 修复历史附加信息
FIX_HISTORY_APPEND = """

之前的修复尝试：
{fix_history}"""

# Lint 修复提示词（错误数量多）
LINT_FIX_MANY_ERRORS_PROMPT = """在当前目录中有 Python 代码需要修复 lint 错误。参考 GEMINI_KNOWLEDGE.md 中的规范。

错误信息（前20个）：
{errors}
...还有 {remaining_count} 个错误

请只修复以下类型的关键错误：
1. 语法错误（E9xx）
2. 缩进错误（E1xx）
3. 导入错误（E4xx）
4. 未定义变量（F821）

暂时忽略格式化相关的错误（如行太长、空格问题等），这些可以后续用自动化工具处理。
"""

# Lint 修复提示词（错误数量少）
LINT_FIX_FEW_ERRORS_PROMPT = """在当前目录中有 Python 代码需要修复 lint 错误。参考 GEMINI_KNOWLEDGE.md 中的规范。

错误信息：
{errors}

请修复所有 flake8 报告的问题，确保代码符合 PEP 8 规范。
重点修复会影响代码运行的错误，格式问题可以快速修复。
"""

# 应用启动修复提示词
STARTUP_FIX_PROMPT = """FastAPI 应用启动失败，需要修复错误。参考 GEMINI_KNOWLEDGE.md 中的规范。

这是第 {attempt} 次尝试（最多 10 次）。

错误信息：
{error_text}

错误类型分析：
{error_types}

请分析错误原因并修复代码，重点关注：
1. 导入错误 - 检查模块路径和 __init__.py 文件
2. 循环导入 - 使用 TYPE_CHECKING 和前向引用
3. 缺失的模块 - 检查所有文件是否创建
4. 属性错误 - 检查类和函数定义
5. 配置错误 - 检查 config.py 和环境变量

重要提示：
- 如果错误是端口占用（address already in use），你可以：
  1. 修改应用使用的端口（推荐）
  2. 使用命令 'kill -9 $(lsof -ti:端口号)' 杀死占用端口的进程（仅当确认是自己启动的进程时）
- 你有权限杀死自己启动的进程来解决端口占用问题

当前工作目录的绝对路径是: {project_dir}
"""

# 增量修复提示词
INCREMENTAL_FIX_PROMPT = """参考 GEMINI_KNOWLEDGE.md 中的规范。

{fix_template}

文件: {file_path}
具体错误: {error_message}
"""

# 文件特定修复提示词
FILE_SPECIFIC_FIX_PROMPT = """参考 GEMINI_KNOWLEDGE.md 中的规范。

文件 {file_path} 有以下测试错误需要修复：

{errors}

请仅修复这个文件中的错误，不要修改其他文件。
"""

# API 错误模式列表
API_ERROR_PATTERNS = [
    "status: INTERNAL",
    "code\":500",
    "Internal error has occurred",
    "API Error: got status: INTERNAL"
]

# 关键 lint 错误代码
CRITICAL_LINT_ERROR_CODES = {
    'E9',    # 语法错误
    'E1',    # 缩进错误
    'E4',    # 导入错误
    'F821',  # 未定义的名称
    'F822',  # 未定义的名称在 __all__ 中
    'F823',  # 局部变量在赋值前使用
    'F401',  # 导入但未使用（可能影响代码运行）
    'E999',  # 语法错误
}

# 错误类型映射
ERROR_TYPE_MAPPING = {
    "SyntaxError": "语法错误",
    "ImportError": "导入错误",
    "ModuleNotFoundError": "导入错误",
    "AssertionError": "断言失败",
    "TypeError": "类型错误",
    "AttributeError": "属性错误",
    "NameError": "名称错误",
    "cannot import name": "循环导入或名称错误",
    "Connection refused": "端口占用或服务未启动"
}

# 平台框架映射
PLATFORM_FRAMEWORKS = {
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring Boot",
    "express": "Express.js"
}

# 平台 ORM 映射
PLATFORM_ORMS = {
    "fastapi": "SQLAlchemy 2.0",
    "django": "Django ORM",
    "flask": "SQLAlchemy 2.0",
    "spring": "JPA/Hibernate",
    "express": "Sequelize or TypeORM"
}

# 平台验证库映射
PLATFORM_VALIDATORS = {
    "fastapi": "Pydantic v2",
    "django": "Django Forms/Serializers",
    "flask": "Marshmallow or Pydantic",
    "spring": "Bean Validation",
    "express": "Joi or Yup"
}

# 平台测试框架映射
PLATFORM_TEST_FRAMEWORKS = {
    "fastapi": "pytest",
    "django": "Django TestCase + pytest",
    "flask": "pytest",
    "spring": "JUnit 5",
    "express": "Jest or Mocha"
}