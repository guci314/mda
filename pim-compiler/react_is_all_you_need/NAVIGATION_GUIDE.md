# 项目导航指南 🧭

> 解决"项目文件太多，找不到重点"的问题

## ⚡ 立即可用（0成本）

```
1. 打开 PROJECT_MAP.md
2. Command+Shift+V（进入预览模式）
3. 点击蓝色链接跳转
4. Control+- 返回地图 ⭐
```

**只需记住一个快捷键**: `Control+-` = 后退

---

## 🎯 核心思路：静态注意力机制

传统做法：在所有文件中搜索 ❌
**更好的做法**：建立文件索引，快速定位 ✅

---

## 📚 三种导航方案

### 方案1: PROJECT_MAP.md（推荐，最简单）

**文件**: `PROJECT_MAP.md`

**特点**:
- ✅ 无需安装扩展
- ✅ 纯Markdown，易维护
- ✅ 包含决策记录（ADR）
- ✅ VS Code原生支持链接跳转

**正确使用方法**:
```bash
# 1. 打开地图
code PROJECT_MAP.md

# 2. 切换到预览模式（重要！）
Command+Shift+V

# 3. 点击蓝色链接跳转
# 不需要 Command+Click，直接点击即可

# 4. 返回地图
Control+-  # 后退到上一页
```

**⭐ 关键要点**:
- 必须在**预览模式**下使用（`Command+Shift+V`）
- 直接**点击链接**，不需要Command+Click
- 使用 `Control+-` 返回上一页

**优势**:
- 项目地图 = 静态注意力机制
- 标记重要文件，过滤垃圾文件
- 包含"为什么"（决策记录）

---

### 方案2: VS Code Bookmarks（快速标记）

**安装**: VS Code扩展 `Bookmarks`

**使用**:
```
Command+Alt+K  # 标记当前位置
Command+Alt+J  # 上一个书签
Command+Alt+L  # 下一个书签
Command+Alt+I  # 列出所有书签
```

**建议标记**:
- `react_agent_minimal.py:1424` - Compact压缩
- `compact_prompt.md` - 压缩提示词
- `test_compact_prompt.py` - 单元测试
- `PROJECT_MAP.md` - 项目地图

**优势**:
- 快速跳转到常用位置
- 可以跨文件
- 支持标签分类

---

### 方案3: Foam（最接近Wikipedia，适合复杂项目）

**安装**: VS Code扩展 `Foam`

**特点**:
- 支持双向链接 `[[文件名]]`
- 自动生成关系图
- 类似Obsidian/Roam Research

**创建Wiki**:
```markdown
# COMPACT_WIKI.md

## 核心文件
- [[compact_prompt.md]] - 压缩提示词
- [[react_agent_minimal.py]] - Agent实现
- [[test_compact_prompt.py]] - 单元测试

## 概念关系
[[compact_prompt.md]] → [[react_agent_minimal.py]] → [[test_compact_prompt.py]]
```

**使用**:
- 双击 `[[文件名]]` 跳转
- 右键 "Show Graph" 查看关系图

**优势**:
- 真正的wiki系统
- 可视化文件关系
- 适合构建知识库

**缺点**:
- 需要学习成本
- 需要额外维护

---

## 🗑️ 过滤垃圾文件

已创建配置文件：

### 1. `.vscodeignore`
隐藏常见垃圾文件：
- `__pycache__/`
- `*.pyc`
- `output_logs/`
- `.notes/`

### 2. `.vscode/settings.json`
配置文件浏览器排除规则：
```json
{
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/output_logs": true
  }
}
```

**效果**: 文件浏览器不显示这些文件

---

## ⚡ VS Code快捷键（必会）

### 文件导航
```
Command+P          # 快速打开文件（模糊搜索）
Command+Shift+O    # 查看当前文件符号（函数/类）
Command+T          # 查看工作区所有符号
```

### 跳转
```
F12                # 跳转到定义
Command+F12        # 查看所有引用
Command+Click      # Markdown中跳转链接
```

### 搜索
```
Command+F          # 文件内搜索
Command+Shift+F    # 全局搜索
Command+Shift+H    # 全局替换
```

### 多光标
```
Option+Click       # 添加光标
Command+D          # 选中下一个相同词
```

---

## 🎨 推荐的VS Code扩展

### 必装
1. **Markdown All in One**
   - 增强Markdown编辑
   - 支持TOC、快捷键

2. **Bookmarks**
   - 标记重要位置
   - 快速跳转

3. **Python** (Microsoft官方)
   - 代码补全、类型检查

### 可选
1. **Foam**
   - Wiki系统
   - 双向链接

2. **Todo Tree**
   - 高亮TODO、FIXME
   - 生成任务列表

3. **Indent Rainbow**
   - 彩虹缩进
   - 提高可读性

4. **GitLens**
   - 查看代码历史
   - 了解"谁改的"

---

## 💡 使用建议

### 新手流程（0成本）
1. ✅ 打开 `PROJECT_MAP.md`
2. ✅ 配置 `.vscode/settings.json`（已创建）
3. ✅ 学习 `Command+P` 快速打开文件
4. ✅ 使用 `Command+Click` 跳转

### 进阶流程（+书签）
1. ✅ 安装 Bookmarks 扩展
2. ✅ 标记常用文件/函数
3. ✅ 使用 `Command+Alt+K/J/L` 跳转

### 高级流程（+Wiki）
1. ✅ 安装 Foam 扩展
2. ✅ 创建 `COMPACT_WIKI.md`
3. ✅ 使用 `[[双向链接]]`
4. ✅ 查看关系图

---

## 📊 方案对比

| 特性 | PROJECT_MAP | Bookmarks | Foam |
|------|-------------|-----------|------|
| 学习成本 | 无 | 低 | 中 |
| 维护成本 | 低 | 无 | 中 |
| 跳转速度 | 中 | 快 | 快 |
| 可视化 | ❌ | ❌ | ✅ |
| 关系图 | ❌ | ❌ | ✅ |
| 无需扩展 | ✅ | ❌ | ❌ |

**推荐组合**: PROJECT_MAP + Bookmarks

---

## 🚀 快速开始

### 1分钟设置
```bash
# 1. 打开项目地图
code PROJECT_MAP.md

# 2. 加载VS Code配置（已自动生效）
# .vscode/settings.json

# 3. 安装Bookmarks扩展（可选）
# VS Code扩展市场搜索 "Bookmarks"

# 4. 开始导航！
Command+P → 输入文件名 → 回车
```

---

## 🎯 实战案例

### 场景1: 修改Compact提示词
```
1. Command+P → "compact_prompt"
2. 编辑文件
3. Command+P → "test_compact"
4. 运行测试验证
```

### 场景2: 追踪Compact实现
```
1. 打开 PROJECT_MAP.md
2. 查找 "Compact压缩机制"
3. Command+Click "react_agent_minimal.py:1424"
4. F12 查看调用的函数
```

### 场景3: 理解设计决策
```
1. 打开 PROJECT_MAP.md
2. 查找 "决策记录"
3. 阅读 "为什么Compact用API?"
```

---

## 📝 维护建议

### PROJECT_MAP.md 更新频率
- 添加新的核心文件 → 立即更新
- 修改重要函数位置 → 立即更新
- 添加设计决策 → 建议记录
- 日常小修改 → 不需要更新

### 保持地图简洁
- ✅ 只记录**重要**文件
- ✅ 只记录**核心**概念
- ❌ 不要记录所有文件
- ❌ 不要记录实现细节

---

## 🤝 团队协作

如果团队使用：
1. **必须**维护 `PROJECT_MAP.md`
2. **建议**统一使用 Bookmarks
3. **可选**使用 Foam（需培训）

---

**更新**: 2025-01-13
**提示**: 这个文档本身也在 PROJECT_MAP.md 中索引！
