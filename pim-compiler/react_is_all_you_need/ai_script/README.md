# AI临时脚本目录

## 用途

**AI的探索和验证空间**

- 猜想验证脚本
- 探索性代码
- 临时测试
- 概念验证（PoC）
- API探索

## 特点

- ✅ **临时性**：可能随时失效或删除
- ✅ **探索性**：用于验证想法，不是正式代码
- ✅ **隔离性**：不污染项目其他目录
- ✅ **AI专用**：AI可以自由创建和删除

## 不应该放这里

- ❌ 正式的测试文件（应该在tests/）
- ❌ 生产代码（应该在core/）
- ❌ 用户要求的脚本（应该在用户指定位置）
- ❌ 重要的工具（应该在core/tools/）

## 应该放这里

- ✅ 验证Context栈是否工作的脚本
- ✅ 测试某个API调用的脚本
- ✅ 探索新功能的原型代码
- ✅ 临时的数据处理脚本

## 示例

```python
# ai_script/verify_context_stack.py
# 临时验证脚本：测试Context栈

from core.tools.context_stack import ContextStack

stack = ContextStack()
ctx1 = stack.push("test1")
print(f"Push: depth={stack.depth}")

ctx2 = stack.push("test2")
print(f"Push: depth={stack.depth}")

stack.pop()
print(f"Pop: depth={stack.depth}")
```

## 生命周期

```
创建：AI需要验证某个想法
      ↓
使用：运行验证，得到结果
      ↓
处理：
  - 验证成功 → 可能转为正式代码
  - 验证失败 → 删除或保留作为记录
  - 临时需求 → 用完即删
```

## 清理策略

**AI会定期清理**：
- 失效的脚本
- 已完成验证的脚本
- 不再需要的探索代码

**保留**：
- 有参考价值的验证脚本
- 可能重复使用的工具脚本

## 与其他目录的对比

| 目录 | 用途 | 稳定性 | 重要性 |
|------|------|--------|--------|
| **core/** | 正式代码 | 稳定 | 高 |
| **tests/** | 正式测试 | 稳定 | 高 |
| **ai_script/** | 临时探索 | 不稳定 | 低 |
| **docs/** | AI思考记录 | 累积 | 中 |

## 注意

⚠️ 这个目录的内容可能随时变化
⚠️ 不要依赖这里的脚本（它们是临时的）
⚠️ 这是AI的工作空间，不是交付物
