# Minimal System Package - 极简模式的世界观

## 包描述
极简模式专属的系统级知识，定义了一个不同的计算哲学。

## 核心理念：简单即智能
- **没有三元分离**：只有Compact统一记忆
- **没有Event Sourcing**：不写session文件


## 导出模块
- `system_prompt_minimal.md` - 极简系统提示词
- `execution_context_guide.md` - ExecutionContext使用指南

## 与完整模式的根本区别

### 完整模式的世界观
```
世界是客观存在的 → 需要world_state.md
历史必须记录 → 需要sessions
主体需要积累 → 需要agent_knowledge.md
```

### 极简模式的世界观
```
世界即我的感知 → Compact记忆就是世界
历史即我的注意 → 重要的自然被记住
主体即当前对话 → 无需持久化自我
```

## 这不是简化，是另一种哲学

极简模式不是"简化版"的完整模式，而是基于完全不同的认知假设：
- **完整模式**：柏拉图式的客观实在论
- **极简模式**：贝克莱式的主观唯心论

两种system包代表了两种不同的"操作系统"：
- 完整模式：类Unix（文件系统为中心）
- 极简模式：类Lisp Machine（内存为中心）

## 使用方式
```python
if minimal_mode:
    # 使用极简世界观
    knowledge_files = ["knowledge/minimal/system/*.md"]
else:
    # 使用完整世界观
    knowledge_files = ["knowledge/system/*.md"]
```

## 哲学宣言
**没有人能宣称掌握唯一的真理。**
每个Agent都有权选择自己的世界观和认知框架。
这就是自然语言编程的自由。