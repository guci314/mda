# React Is All You Need - 项目地图 🗺️

> 这是项目的"静态注意力机制"，帮助快速定位关键文件和理解架构

## ⚡ 快速开始（3步）

```
1. Command+Shift+V    # 打开此文件的预览模式
2. 点击蓝色链接        # 跳转到目标文件
3. Control+-          # 返回上一页（地图）⭐
```

**关键快捷键记住这个**: `Control+-` = 后退 = 返回地图

💡 **快速参考**: 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 获取所有快捷键


### Agent核心
- [react_agent_minimal.py](core/react_agent_minimal.py) - ⭐ 核心Agent（500行）
- [tool_base.py](core/tool_base.py) - 工具基类
- [knowledge_function_loader.py](core/knowledge_function_loader.py) - 知识函数加载器

### 知识系统
- [knowledge/minimal/system/](knowledge/minimal/system/) - 系统提示词
- [knowledge/core/](knowledge/core/) - 核心概念
- [KNOWLEDGE_FUNCTION_REFACTOR.md](knowledge/KNOWLEDGE_FUNCTION_REFACTOR.md) - 知识函数重构文档

---

## 🎯 核心概念索引

### 基于注意力机制的压缩

[compact_wiki.md](compact_wiki.md)

### 知识函数系统
**位置**: `knowledge/` + `core/knowledge_function_loader.py`
**概念**: `knowledge/knowledge_function_concepts.md`

**两种类型**:
- 契约函数（强制ExecutionContext）
- 软约束函数（可选ExecutionContext）

### ExecutionContext
**实现**: `core/tools/execution_context.py`
**用途**: 外部化Agent的思考状态

---

## 🗑️ 可以忽略的目录

以下是历史遗留/实验性文件，可以忽略：

```
.vscode/                    # VS Code配置
__pycache__/                # Python缓存
*.pyc                       # 编译文件
notebooks/                  # 实验性notebook
.notes/                     # 临时笔记
output_logs/                # 旧日志
```

**建议**: 添加到 `.gitignore` 或 `.vscodeignore`

---

## 🔍 快速搜索

### 按功能找文件

| 功能 | 文件 |
|------|------|
| Compact压缩 | [react_agent_minimal.py](core/react_agent_minimal.py) (第1424行) |
| 系统提示词构建 | [react_agent_minimal.py](core/react_agent_minimal.py) (第728行) |
| 知识文件加载 | [react_agent_minimal.py](core/react_agent_minimal.py) (第794行) |
| Compact提示词 | [compact_prompt.md](knowledge/minimal/system/compact_prompt.md) |
| Compact测试 | [test_compact_prompt.py](tests/test_compact_prompt.py) |

### 按概念找文件

| 概念 | 主要文件 | 相关文件 |
|------|---------|----------|
| 注意力机制 | [compact_prompt.md](knowledge/minimal/system/compact_prompt.md) | [react_agent_minimal.py](core/react_agent_minimal.py) (第1424行) |
| 知识函数 | [knowledge_function_concepts.md](knowledge/knowledge_function_concepts.md) | [knowledge_function_loader.py](core/knowledge_function_loader.py) |
| ExecutionContext | [execution_context.py](core/tools/execution_context.py) | [system_prompt_minimal.md](knowledge/minimal/system/system_prompt_minimal.md) |
| Agent创建 | [create_agent_tool.py](core/tools/create_agent_tool.py) | [react_agent_minimal.py](core/react_agent_minimal.py) |

---

## 📖 决策记录（ADR风格）

### 为什么Compact用API而不是Agent?

**决策**: Compact通过直接API调用执行，不经过Agent

**原因**:
1. **避免递归**: Agent压缩自己的历史会产生复杂递归
2. **基础设施层**: 内存管理是基础设施，不是业务逻辑
3. **性能考虑**: 直接调用更快
4. **确定性**: temperature=0保证稳定

**位置**: `react_agent_minimal.py:1507-1519`

### 为什么是L0-L4五层?

**决策**: 压缩策略使用5层（L0-L4）

**原因**:
1. **基于香农编码**: 信息量 → 压缩率
2. **足够表达**: 覆盖"必须保留"到"完全删除"
3. **简单易理解**: 不过度复杂
4. **实践验证**: 单元测试证明有效

**位置**: `compact_prompt.md:67-165`

### 为什么系统提示词在前，知识文件在后?

**决策**: 系统提示词模板在前，知识文件通过占位符插入在后

**原因**:
1. **优先级**: 系统提示词是"宪法"，优先级最高
2. **通用性**: 系统提示词对所有Agent通用
3. **可定制**: 知识文件针对特定Agent

**位置**: `react_agent_minimal.py:728-791`

---

## 🚀 快速操作

### 修改Compact提示词后验证
```bash
# 1. 编辑提示词
code knowledge/minimal/system/compact_prompt.md

# 2. 运行测试（30秒）
cd tests && ./quick_test.sh

# 3. 查看结果
cat compact_test_report.json | jq '.avg_score'
```

### 创建新的Agent
```python
from core.react_agent_minimal import ReactAgentMinimal

agent = ReactAgentMinimal(
    work_dir="work_dir",
    name="my_agent",
    knowledge_files=["knowledge/my_knowledge.md"]
)
```

### 运行Compact测试
```bash
cd tests
python3.12 test_compact_prompt.py
```

---

## 🔗 外部资源

- [CLAUDE.md](../CLAUDE.md) - 项目配置和核心理念
- [知识函数重构文档](knowledge/KNOWLEDGE_FUNCTION_REFACTOR.md)
- [两阶段执行模型](knowledge/TWO_PHASE_EXECUTION_MODEL.md)

---

## 📝 更新日志

| 日期 | 更新 | 影响文件 |
|------|------|---------|
| 2025-01-13 | 创建Compact单元测试 | `test_compact_prompt.py` |
| 2025-01-13 | 优化系统提示词顺序 | `react_agent_minimal.py:728` |
| 2025-01-13 | 创建项目地图 | `PROJECT_MAP.md` (本文件) |

---

## 💡 使用技巧

### VS Code中的导航（最重要！）

#### 1. 在Markdown预览中点击链接跳转
```
1. 打开 PROJECT_MAP.md
2. 点击右上角的预览图标（或 Command+Shift+V）
3. 点击任何蓝色链接跳转到文件
4. 使用 Control+- 返回上一页 ⭐
5. 使用 Control+Shift+- 前进到下一页
```

**关键快捷键**：
- `Command+Shift+V` - 打开Markdown预览
- `Control+-` - 后退（返回上一页）⭐⭐⭐
- `Control+Shift+-` - 前进（到下一页）
- 点击链接即可跳转

#### 2. 快速打开文件
```
Command+P          # 输入文件名快速打开（模糊搜索）
Command+Shift+O    # 查看当前文件的符号（函数/类）
Command+T          # 查看工作区所有符号
```

#### 3. 代码跳转
```
F12                # 跳转到定义
Command+Click      # 点击跳转到定义
Command+F12        # 查看所有引用
Control+-          # 返回上一个位置 ⭐
```

### 配合Bookmarks扩展（可选）
安装 **Bookmarks** 扩展后：
- `Command+Alt+K` 标记当前位置
- `Command+Alt+J` 跳转到上一个书签
- `Command+Alt+L` 跳转到下一个书签

---

**更新**: 2025-01-13
**维护者**: 请在修改重要文件后更新此地图
