```markdown
# 知识库

## 元知识
- **PSM缺失时的应急策略**：当PSM文件不存在时，可基于领域常识构建标准模型（如博客系统的Article/Category/Comment），创建基础PSM文件后再执行标准生成流程
- **空目录初始化验证**：在生成代码前通过`list_directory`验证目录状态，确保增量生成策略的正确
- **领域常识映射方法**：将通用业务概念（博客系统）映射为标准PSM结构：实体→字段→关系→约束
- **工具链可靠性验证**：`create_directory`和`write_file`在空目录环境下可稳定执行，无需预检查
- **最小可行验证**：通过`list_directory`或`read_file`验证关键文件存在性，确保任务成功完成
- **完整项目验证流程**：必须依次验证目录结构、核心文件、测试文件和文档文件的存在性
- **分层验证策略**：优先验证核心层（main/models/schemas）再验证扩展层（services/routers/tests）
- **PSM解析验证**：通过`read_file`读取PSM内容后，需验证关键部分（Domain Models/Enums）的存在性

## 原理与设计
- **混合组织模式的实践验证**：领域聚合模式（models/schemas按领域聚合）与资源拆分模式（crud/services/routers/tests按资源拆分）的组合在实践中证明有效
- **应急PSM构建原则**：基于80/20法则构建核心实体（20%的核心实体覆盖80%的业务需求）
- **标准领域模型设计**：博客系统三核心实体（Article/Category/Comment）形成稳定的领域模型基础
- **枚举统一管理模式**：业务状态枚举在models层（SQLAlchemy）和schemas层（Pydantic）分别定义，保持类型安全
- **最小项目结构原则**：简单FastAPI应用只需3个核心文件（main.py, models.py, test_main.py）即可运行
- **扩展项目结构规范**：完整项目应包含models/schemas/routers/services/crud分层和对应测试结构
- **API路由组织原则**：按资源分离路由文件（articles.py/comments.py）优于集中式路由
- **状态机设计模式**：ArticleStatus和CommentStatus枚举实现业务状态机的基础验证

## 接口与API
- **目录创建工具**：`create_directory`支持递归创建多级目录结构
- **文件写入工具**：`write_file`在文件不存在时创建，存在时覆盖
- **空目录检测**：`list_directory`返回空列表表示目录为空
- **文件搜索工具**：`search_files`支持通配符模式匹配
- **文件验证工具**：`read_file`可用于验证文件内容是否正确写入
- **目录内容验证**：`list_directory`返回结果格式为`[FILE] filename`的列表
- **分层验证API**：`list_directory`可递归验证多级目录结构完整性
- **PSM解析接口**：`read_file`返回的PSM内容需包含`## Domain Models`和`### Enums and Constants`章节

## 实现细节（需验证）
- **标准项目初始化顺序**：
  1. 创建目录结构（app/, tests/）
  2. 创建主应用文件（app/main.py）
  3. 创建数据模型文件（app/models.py）
  4. 创建测试文件（tests/test_main.py）
  5. 验证文件存在性

- **完整项目初始化顺序**（扩展版）：
  1. 创建基础目录结构（app/, tests/）
  2. 创建核心文件（main.py, models.py, schemas.py）
  3. 创建服务层文件（services.py）
  4. 创建API路由目录（app/api/）
  5. 按资源分离路由文件（articles.py, comments.py）
  6. 创建数据库配置（db.py）
  7. 创建依赖配置（dependencies.py）
  8. 创建资源测试文件（test_articles.py, test_comments.py）
  9. 创建文档文件（README.md）
  10. 执行分层验证

- **文件命名约定**：
  - 路由层：`{resource}s.py`（复数形式）
  - 测试层：`test_{resource}s.py`
  - 服务层：`services.py`（聚合模式）或`{resource}_service.py`（拆分模式）

- **PSM解析实现**：
  - 必须包含`## Domain Models`章节
  - 枚举定义需在`### Enums and Constants`章节
  - 模型定义使用SQLAlchemy语法模板

## 用户偏好与项目特点
- **应急模式偏好**：在PSM缺失时，倾向于构建博客系统作为演示标准
- **核心实体选择**：博客系统默认包含Article（文章）、Category（分类）、Comment（评论）三个核心实体
- **枚举命名风格**：状态枚举值使用小写字符串（draft/published/deleted）
- **时间字段配置**：所有时间字段使用`DateTime(timezone=True)`确保时区安全
- **最小验证标准**：优先确保main.py, models.py, test_main.py三个核心文件存在
- **文档要求**：README.md必须包含基本安装说明和测试命令
- **路由组织偏好**：倾向于将API路由按资源分离到独立文件
- **PSM验证标准**：优先检查Domain Models和Enums章节完整性
```