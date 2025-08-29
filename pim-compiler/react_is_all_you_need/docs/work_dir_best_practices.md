# Work Directory 最佳实践

## 问题描述
当使用相对路径作为 `work_dir` 时，如果 Agent 已经在某个目录下运行，可能会创建嵌套的目录结构。例如：
- 当前目录：`/path/to/my_project`
- Agent 使用：`work_dir="my_project"`
- 结果：创建了 `/path/to/my_project/my_project/.notes`

## 最佳实践

### 1. 使用绝对路径（推荐）
```python
from pathlib import Path
import os

# 获取当前脚本所在目录的绝对路径
current_dir = Path(__file__).parent.absolute()
work_dir = current_dir / "output" / "project_name"

# 或使用 os.path
work_dir = os.path.abspath("./output/project_name")

# 创建 Agent
agent = ReactAgentMinimal(
    work_dir=str(work_dir),  # 使用绝对路径
    window_size=50,
    max_rounds=30
)
```

### 2. 使用当前目录
如果希望在当前目录下工作：
```python
agent = ReactAgentMinimal(
    work_dir=".",  # 使用当前目录
    window_size=50,
    max_rounds=30
)
```

### 3. 在 Jupyter Notebook 中
```python
import os
from pathlib import Path

# 获取 notebook 所在目录
notebook_dir = Path.cwd()
work_dir = notebook_dir / "output" / "experiment"

agent = ReactAgentMinimal(
    work_dir=str(work_dir.absolute()),
    window_size=50,
    max_rounds=30
)
```

### 4. 项目级别的路径管理
```python
# 在项目根目录创建一个 config.py
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "output"

# 确保输出目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_work_dir(name: str) -> Path:
    """获取工作目录的绝对路径"""
    work_dir = OUTPUT_DIR / name
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir
```

使用配置：
```python
from config import get_work_dir

agent = ReactAgentMinimal(
    work_dir=str(get_work_dir("my_experiment")),
    window_size=50,
    max_rounds=30
)
```

## 常见错误示例

### ❌ 错误：硬编码相对路径
```python
agent = ReactAgentMinimal(
    work_dir="my_project",  # 可能创建嵌套目录
    window_size=50
)
```

### ❌ 错误：假设当前目录
```python
agent = ReactAgentMinimal(
    work_dir="./output/test",  # 依赖于执行位置
    window_size=50
)
```

### ✅ 正确：使用绝对路径
```python
from pathlib import Path

work_dir = Path("/home/user/projects/my_project").absolute()
agent = ReactAgentMinimal(
    work_dir=str(work_dir),
    window_size=50
)
```

## 笔记系统路径
Agent 会在 `work_dir` 下创建 `.notes` 目录：
- `{work_dir}/.notes/experience.md` - 经验库
- `{work_dir}/.notes/task_state.md` - 任务状态
- `{work_dir}/.notes/environment.md` - 环境知识

确保 `work_dir` 使用绝对路径可以避免笔记文件位置混乱。

## 调试路径问题
如果发现路径嵌套问题：
```python
# 检查实际创建的路径
from pathlib import Path

work_dir = Path("my_project")
print(f"相对路径: {work_dir}")
print(f"绝对路径: {work_dir.absolute()}")
print(f"笔记目录: {work_dir.absolute() / '.notes'}")

# 列出目录结构
for p in work_dir.rglob("*"):
    print(p)
```

## 总结
- **始终使用绝对路径**作为 `work_dir`
- 使用 `Path.absolute()` 或 `os.path.abspath()` 转换路径
- 在项目中统一管理路径配置
- 避免硬编码相对路径