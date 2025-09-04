#!/usr/bin/env python3
"""
元认知优化调试知识 - 基于历史案例
不需要重新生成bug代码，使用已有的错误模式
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from core.react_agent_minimal import ReactAgentMinimal

print("🧠 元认知优化调试知识（基于案例）")
print("=" * 60)

# 创建元认知Agent
meta_agent = ReactAgentMinimal(
    work_dir=".",
    name="meta_debug_optimizer",
    description="元认知专家 - 基于案例优化调试知识",
    model="kimi-k2-turbo-preview",
    knowledge_files=[
        "knowledge/meta_cognitive_simple.md",
        "knowledge/debug_error_patterns.md"  # 错误模式库
    ]
)

# 优化任务
optimization_task = """
# 元认知任务：基于86轮案例优化调试知识

## 背景
我们有一个真实案例：调试Agent花了86轮才修复所有单元测试。
主要问题已经总结在`knowledge/debug_error_patterns.md`中。

## 你的任务
1. **分析**`knowledge/mda/debugging_unified.md`当前结构
2. **对比**`knowledge/debug_error_patterns.md`中的高效模式
3. **重构**调试知识，融入以下改进：

### 必须添加的核心改进

#### 1. 快速启动模板（第1轮必做）
```python
# 标准测试运行命令 - 不要尝试多种方式
python -c "
import unittest
loader = unittest.TestLoader()
suite = loader.discover('tests')
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
# 解析具体错误
for error in result.errors + result.failures:
    print(f'错误: {error[0]}: {error[1]}')
"
```

#### 2. 错误分类决策（第2轮必做）
- Pydantic兼容性 → 批量搜索替换
- 导入错误 → 检查模块定义
- 路由404 → 检查路由注册

#### 3. 批量修复模板
```bash
# Pydantic v2批量修复
find app/ -name "*.py" -exec sed -i 's/\.dict()/\.model_dump()/g' {} \;

# 导入错误批量修复  
find app/ -name "*.py" -exec sed -i 's/from app.models import models/from app.models import Base/g' {} \;
```

## 优化目标
- **轮数**：20轮内完成（vs 原86轮）
- **策略**：先诊断、再分类、后批量修复
- **避免**：重复尝试相同操作

## 知识文件结构建议
```markdown
# 调试知识2.0

## 🚀 快速启动（1-3轮）
### 第1轮：标准诊断
[具体命令]

### 第2轮：错误分类
[分类模板]

### 第3轮：制定计划
[计划模板]

## 🔧 批量修复（4-15轮）
### Pydantic兼容性
[批量命令]

### 导入错误
[批量命令]

## ✅ 验证（16-20轮）
[验证命令]
```

## 成功标准
1. 知识文件包含具体的命令模板
2. 有明确的轮数预算
3. 批量修复优于逐个修复
4. 避免重复尝试

请直接修改`knowledge/mda/debugging_unified.md`，使其更高效、更实用。
"""

# 执行优化
result = meta_agent.execute(task=optimization_task)

print("\n" + "=" * 60)
print("✅ 元认知优化完成")
if result:
    print(f"\n优化要点：")
    print(result[:1000])
print("=" * 60)

# 显示优化前后对比
print("\n📊 预期效果对比：")
print("优化前：86轮完成调试")
print("优化后：<20轮完成调试")
print("效率提升：4倍以上")