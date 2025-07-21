# 架构变更记录

## 变更概述

将 PIM 编译器从传统的结构化数据模型架构简化为直接处理 Markdown 的 LLM 驱动架构。

## 删除的组件

### 1. 数据模型文件
- ❌ `src/models/pim_model.py` - PIM 数据结构
- ❌ `src/models/psm_model.py` - PSM 数据结构  
- ❌ `src/models/ir_model.py` - 中间表示
- ❌ `src/models/` - 整个目录

### 2. 相关测试
- ❌ `tests/test_pim_test.py` - 模型测试
- ❌ `tests/test_structure.py` - 结构测试

## 简化后的架构

### 核心流程
```
PIM.md → DeepSeekCompiler → PSM.md → DeepSeekCompiler → Code
```

### 主要组件
1. **BaseCompiler** - 抽象基类，定义编译流程
2. **DeepSeekCompiler** - 具体实现，调用 LLM
3. **CompilerConfig** - 编译器配置
4. **CLI** - 命令行工具

### 关键方法
- `_transform_pim_to_psm()` - 使用 LLM 转换 PIM 到 PSM
- `_generate_code_from_psm()` - 使用 LLM 生成代码
- 缓存机制保持不变

## 优势

1. **代码简化**
   - 删除了 3 个复杂的数据模型文件
   - 删除了大量序列化/反序列化代码
   - 整体代码量减少约 70%

2. **更符合 LLM 特性**
   - LLM 天然理解 Markdown
   - 无需固定的 schema
   - 更灵活的输入输出格式

3. **易于维护**
   - 减少了抽象层次
   - 提示词驱动，易于调整
   - 专注于核心功能

## 迁移指南

如果从旧版本迁移：

1. 不再需要定义数据模型类
2. 直接编写 Markdown 格式的 PIM
3. 编译器会生成 Markdown 格式的 PSM
4. 所有业务逻辑通过提示词控制

## 示例对比

### 旧方法
```python
# 需要定义复杂的数据结构
entity = PIMEntity(
    name="User",
    attributes=[
        PIMAttribute(name="email", constraints=["unique"])
    ]
)
model = PIMModel(entities=[entity])
```

### 新方法
```markdown
# 直接写 Markdown
## 业务实体
- 用户：邮箱（唯一）
```

## 总结

这次重构充分利用了 LLM 的自然语言处理能力，将复杂的编译器简化为一个优雅的文档转换工具。代码更少，功能不减，真正体现了"少即是多"的设计理念。