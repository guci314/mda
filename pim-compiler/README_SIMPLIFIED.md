# PIM Compiler (简化版)

基于 LLM 的 PIM（平台无关模型）编译器，直接处理 Markdown 文档。

## 核心理念

- **无需复杂数据模型**：直接让 LLM 处理 Markdown
- **PIM → PSM → Code**：全程使用自然语言文档
- **简单高效**：减少不必要的抽象层

## 架构

```
PIM.md → LLM → PSM.md → LLM → Code
         ↑              ↑
      提示词模板     提示词模板
```

## 特性

- 🚀 **智能转换**: 使用 DeepSeek LLM 理解业务语言
- 📝 **Markdown 驱动**: PIM 和 PSM 都是 Markdown 文档
- ⚡ **LLM 缓存**: 避免重复调用，提高效率
- 🎯 **多平台支持**: FastAPI、Spring、Django、Flask

## 快速开始

### 1. 安装

```bash
cd pim-compiler
pip install -r requirements.txt
export DEEPSEEK_API_KEY=your-api-key
```

### 2. 编写 PIM (Markdown)

```markdown
# 用户管理系统

## 业务实体
- 用户：用户名（唯一）、邮箱、密码

## 业务服务  
- 注册用户
- 用户登录
```

### 3. 编译到 PSM

```bash
./pimc compile user_management.md
```

生成的 PSM 示例：

```markdown
# 用户管理系统 (FastAPI)

## 数据模型
- User:
  - username: str (unique=True, max_length=50)
  - email: EmailStr
  - password_hash: str

## API 端点
- POST /api/users/register
- POST /api/users/login
```

### 4. 生成代码（可选）

```bash
./pimc generate user_management.md --code-output ./generated
```

## 文件结构

```
pim-compiler/
├── src/
│   ├── compiler/
│   │   ├── core/
│   │   │   ├── base_compiler.py    # 简化的基类
│   │   │   └── compiler_config.py
│   │   └── transformers/
│   │       └── deepseek_compiler.py # LLM 调用逻辑
│   └── cli/
│       └── main.py                  # CLI 工具
├── examples/                        # 示例 PIM 文件
├── prompts/                         # 提示词模板
└── tests/
```

## 为什么简化？

### 传统方法（过度工程化）
- 需要 PIMModel、PSMModel、IRModel 等复杂数据结构
- 大量的序列化/反序列化代码
- 固定的 schema 限制灵活性

### 新方法（LLM 时代）
- LLM 直接理解和处理 Markdown
- 无需中间数据结构
- 更灵活、更简单、更符合 LLM 工作方式

## 提示词示例

### PIM → PSM 转换提示词
```
将下面的 PIM 转换为 FastAPI 平台的 PSM：
- 保持 Markdown 格式
- 添加数据类型、API 路由等技术细节
- 保留所有业务逻辑
```

### PSM → Code 生成提示词
```
根据 PSM 生成 FastAPI 代码：
- 生成完整可运行的代码
- 遵循最佳实践
- 包含所有必要文件
```

## 优势

1. **简单性**：代码量减少 70%
2. **灵活性**：Markdown 格式自由，易于扩展
3. **可读性**：PIM 和 PSM 都是人类可读的文档
4. **LLM 友好**：充分利用 LLM 的自然语言理解能力

## 许可证

MIT License