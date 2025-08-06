# World Overview 生成指南

当工作目录中不存在 `world_overview.md` 文件时，请按以下步骤生成：

## 1. 分析目录结构

首先判断是否为git仓库，选择合适的方法：

### 方法A：Git仓库（推荐）
```bash
# 检查是否为git仓库
git rev-parse --git-dir 2> /dev/null

# 如果是git仓库，使用git ls-files获取文件列表
git ls-files | head -50  # 查看前50个文件了解结构

# 获取目录结构
git ls-files | xargs -n1 dirname | sort -u | head -20

# 统计文件类型
git ls-files | grep -E '\.(py|js|java|go|rs|cpp)$' | wc -l
```

### 方法B：非Git仓库或需要查看完整结构
```bash
eza . --tree -L 3 -I '.venv|venv|env|__pycache__|*.pyc|.git|node_modules|.pytest_cache|.mypy_cache'
```

了解：
- 目录的整体结构和层级
- 主要文件类型分布
- 关键目录的用途

注意：优先使用git ls-files，因为它只显示项目实际管理的文件。

## 2. 识别项目类型

根据特征文件判断项目类型：
- `package.json` → Node.js/前端项目
- `requirements.txt` / `setup.py` → Python项目
- `pom.xml` / `build.gradle` → Java项目
- `Cargo.toml` → Rust项目
- `go.mod` → Go项目
- 其他特征文件

## 3. 收集关键信息

### 必读文件（按优先级）
1. `README.md` - 项目说明
2. `LICENSE` - 许可证信息
3. 配置文件 - 了解项目配置
4. 文档目录 - 查看是否有架构文档

### 代码结构
- 识别主要源代码目录
- 找出入口文件
- 理解模块组织方式

## 4. 生成 world_overview.md

使用以下模板生成文件：

```markdown
# World Overview

生成时间：[YYYY-MM-DD HH:MM:SS]
生成者：[Agent名称]

## 目录概况

[简要描述这个目录是什么，如：这是一个Python Web应用项目]

## 项目类型

- 类型：[如：Python/FastAPI Web应用]
- 主要语言：[如：Python 3.8+]
- 框架/库：[列出主要依赖]

## 目录结构

获取目录结构的推荐方法：

### Git仓库：
```bash
# 方法1：显示目录层级（推荐）
git ls-files | sed 's|[^/]*/|  |g' | sort -u | head -30

# 方法2：只显示目录
git ls-files | xargs -n1 dirname | sort -u | grep -v '^\.$' | sed 's|^|./|' | head -20

# 方法3：树形结构（如果需要）
git ls-files | xargs -n1 dirname | sort -u | sed 's|[^/]*/|  |g'
```

### 非Git仓库：
```bash
eza . --tree -L 3 -I '.venv|venv|env|__pycache__|*.pyc|.git'
```

```
[展示主要目录结构，优先显示版本控制的文件]
```

## 关键文件

| 文件 | 说明 |
|------|------|
| [文件名] | [用途说明] |

## 主要组件

[列出识别到的主要功能模块或组件]

## 快速导航

- 源代码：`[路径]`
- 测试代码：`[路径]`
- 文档：`[路径]`
- 配置：`[路径]`

## 特殊说明

[任何需要注意的特殊情况或发现]

## 更新记录

- [YYYY-MM-DD] 初次生成
```

## 5. 生成原则

1. **简洁准确**：只记录最重要的信息
2. **面向导航**：帮助快速定位关键内容
3. **保持中立**：客观描述，不做主观评价
4. **适度深入**：不需要分析每个文件，抓住整体结构
5. **及时更新**：发现重大变化时更新此文件

## 6. 特殊情况处理

### 空目录
如果目录完全为空，生成最简版本：
```markdown
# World Overview

生成时间：[时间]

## 目录概况

这是一个空目录，等待初始化。
```

### 超大项目
如果文件过多（>1000个），只关注：
- 顶层目录结构（使用 `eza . --tree -L 2` 只显示2层）
- README 和文档
- 主要配置文件
- 可以对特定子目录单独分析：`eza ./src --tree -L 3`

### 非代码目录
如果是文档库、数据目录等：
- 按文件类型统计
- 识别组织方式
- 突出内容特点

## 7. 示例场景

### Python项目示例
```markdown
# World Overview

生成时间：2024-01-15 10:30:00
生成者：code_analyzer

## 目录概况

这是一个基于FastAPI的RESTful API项目，提供用户管理和认证服务。

## 项目类型

- 类型：Python Web API
- 主要语言：Python 3.8+
- 框架/库：FastAPI, SQLAlchemy, Pydantic

## 目录结构

```
.
├── src/
│   ├── api/          # API路由
│   ├── models/       # 数据模型
│   └── services/     # 业务逻辑
├── tests/            # 测试文件
├── docs/             # API文档
└── requirements.txt  # 依赖列表
```
[以下省略...]
```