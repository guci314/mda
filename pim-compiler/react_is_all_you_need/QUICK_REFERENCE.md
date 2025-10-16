# 快速参考卡片 🎴

## 📍 项目导航（最常用）

### 使用PROJECT_MAP.md导航
```
1. 打开 PROJECT_MAP.md
2. Command+Shift+V  → 进入预览模式
3. 点击蓝色链接    → 跳转到文件
4. Control+-       → 返回地图 ⭐⭐⭐
```

## ⌨️ VS Code导航快捷键

### 最重要的3个
```
Control+-          后退（返回上一页）⭐⭐⭐
Control+Shift+-    前进（到下一页）
Command+P          快速打开文件
```

### 文件跳转
```
Command+Shift+V    打开Markdown预览
Command+P          快速打开文件（模糊搜索）
Command+Shift+O    查看当前文件符号
Command+T          查看所有符号
```

### 代码导航
```
F12                跳转到定义
Command+Click      跳转到定义
Command+F12        查看所有引用
Control+-          返回上一个位置 ⭐
```

### 搜索
```
Command+F          文件内搜索
Command+Shift+F    全局搜索
```

## 🗺️ 核心文件位置

### Compact系统
- 压缩提示词: `knowledge/minimal/system/compact_prompt.md`
- 压缩实现: `core/react_agent_minimal.py:1424`
- 单元测试: `tests/test_compact_prompt.py`

### Agent核心
- 核心代码: `core/react_agent_minimal.py`
- 工具基类: `core/tool_base.py`
- 知识加载器: `core/knowledge_function_loader.py`

### 知识系统
- 系统提示词: `knowledge/minimal/system/system_prompt_minimal.md`
- 知识函数: `knowledge/knowledge_function_concepts.md`

## 🚀 快速操作

### 测试Compact提示词
```bash
cd tests
./quick_test.sh
# 或
python3.12 test_compact_prompt.py
```

### 创建新Agent
```python
from core.react_agent_minimal import ReactAgentMinimal

agent = ReactAgentMinimal(
    work_dir="work_dir",
    name="my_agent",
    knowledge_files=["knowledge/my_knowledge.md"]
)
```

## 💡 记忆技巧

### 只需记住这个
```
Control+-  = 后退 = 返回上一页 = 返回地图
```

这就够了！其他的可以慢慢学。

---

**提示**: 把这个文件固定在VS Code的侧边栏，随时查看！
