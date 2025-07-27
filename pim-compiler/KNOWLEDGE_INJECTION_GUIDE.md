# ReactAgent 先验知识注入指南

## 概述

ReactAgent v3 现已支持先验知识注入机制，使其成为一个领域无关的通用代码生成工具。通过在运行目录创建 `先验知识.md` 文件，可以为 Agent 注入特定领域的知识和最佳实践。

## 核心改进

### 1. 领域无关的系统提示词

之前：
```python
system_prompt = f"""你是一个专业的 {self.config.platform} 开发专家。
你的任务是根据 PSM 生成完整的 {self.config.platform} 应用代码。
```

现在：
```python
system_prompt = f"""你是一个专业的软件开发助手。
你的任务是根据提供的规范生成高质量的代码。
```

### 2. 动态知识加载

Agent 启动时会自动查找并加载 `先验知识.md`：

```python
def _load_prior_knowledge(self) -> str:
    """加载先验知识"""
    knowledge_path = Path(self.config.knowledge_file)
    if knowledge_path.exists():
        return knowledge_path.read_text(encoding='utf-8')
    return ""
```

## 使用方法

### 1. 创建先验知识文件

在项目目录创建 `先验知识.md`，包含领域特定的知识：

```markdown
# [领域名称] 先验知识

## 项目结构规范
...

## 代码生成规范
...

## 最佳实践
...
```

### 2. 运行 ReactAgent

```bash
# 使用默认先验知识文件
python direct_react_agent_v3_fixed.py --pim-file my_pim.md

# 指定其他知识文件
python direct_react_agent_v3_fixed.py \
    --pim-file my_pim.md \
    --knowledge-file django_knowledge.md
```

### 3. 通用 Agent 使用

```bash
# 执行任意任务
python direct_react_agent_v4_generic.py \
    --task "创建一个 Django REST API" \
    --knowledge-file django_knowledge.md \
    --output-dir output/django_api
```

## 示例：不同领域的先验知识

### FastAPI 应用（已提供）

```markdown
# FastAPI 代码生成先验知识

## 项目结构规范
...

## 代码生成规范
### 1. 主应用文件 (main.py)
...
```

### Django 应用示例

创建 `django_knowledge.md`：

```markdown
# Django 应用开发先验知识

## 项目结构规范

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   └── ...
├── requirements.txt
└── README.md
```

## Django 模型示例
...
```

### Vue.js 前端示例

创建 `vue_knowledge.md`：

```markdown
# Vue.js 前端开发先验知识

## 项目结构规范

```
my-vue-app/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── views/
│   ├── router/
│   ├── store/
│   ├── App.vue
│   └── main.js
├── package.json
└── vite.config.js
```

## 组件开发规范
...
```

## 高级用法

### 1. 多文件知识注入

可以创建知识目录结构：

```
knowledge/
├── fastapi_knowledge.md
├── django_knowledge.md
├── vue_knowledge.md
└── react_knowledge.md
```

使用时指定具体文件：

```bash
python direct_react_agent_v3_fixed.py \
    --knowledge-file knowledge/django_knowledge.md
```

### 2. 组合使用记忆和知识

```bash
# 使用持久化记忆 + 先验知识
python direct_react_agent_v3_fixed.py \
    --memory pro \
    --session-id my_project \
    --knowledge-file fastapi_knowledge.md
```

### 3. 创建领域特定包装脚本

创建 `generate_fastapi.sh`：

```bash
#!/bin/bash
python direct_react_agent_v3_fixed.py \
    --knowledge-file fastapi_knowledge.md \
    --output-dir output/fastapi \
    "$@"
```

## 先验知识编写指南

### 1. 结构化组织

```markdown
# [领域] 先验知识

## 概述
简要说明这个领域的特点

## 项目结构规范
标准的目录结构

## 代码规范
### 1. [组件类型1]
示例代码和说明

### 2. [组件类型2]
示例代码和说明

## 最佳实践
- 实践1
- 实践2

## 常见错误
- 错误1及解决方案
- 错误2及解决方案
```

### 2. 包含具体示例

不要只说规则，要给出具体代码示例：

```markdown
## 数据模型规范

### SQLAlchemy 模型示例
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    # ... 具体实现
```
```

### 3. 涵盖完整流程

从项目创建到测试运行的完整流程：

```markdown
## 生成流程

1. 创建项目结构
2. 生成核心文件
3. 生成业务代码
4. 创建测试
5. 运行验证
```

## 效果对比

### 使用先验知识前

Agent 只能根据通用软件开发知识生成代码，可能：
- 不符合框架最佳实践
- 缺少必要的配置文件
- 目录结构不标准

### 使用先验知识后

Agent 能够：
- ✅ 遵循框架特定的项目结构
- ✅ 使用推荐的设计模式
- ✅ 包含所有必要的配置
- ✅ 生成符合最佳实践的代码

## 总结

通过先验知识注入机制，ReactAgent v3 实现了：

1. **领域无关性**：核心 Agent 不绑定任何特定技术栈
2. **灵活性**：通过更换知识文件支持不同领域
3. **可扩展性**：用户可以创建自己的领域知识
4. **易用性**：只需创建一个 Markdown 文件即可

这使得 ReactAgent 成为一个真正通用的代码生成工具，可以适应各种不同的开发场景和技术栈。