# Partial函数设计决策：只验证签名

## 设计问题

**是否强制要求partial定义的docstring完全一致？**

## 讨论过程

### 方案对比

| 方案 | 验证要求 | 优点 | 缺点 |
|------|---------|------|------|
| 严格方案 | 签名+docstring+类型都一致 | 完全一致 | 维护成本高，人容易忘 |
| 方案1 ⭐ | 只验证签名+类型 | 实用，符合人性 | docstring可能不同步 |

### 参考成熟语言

#### C# Partial Class
```csharp
// File1.cs
public partial class Customer
{
    /// <summary>Save customer data</summary>
    public void Save() { }
}

// File2.cs
public partial class Customer
{
    /// <summary>Different comment is OK</summary>
    public void Notify() { }
}
```
**关键**：C# **不要求注释一致**，只要求结构一致。

#### TypeScript Declaration Merging
```typescript
// file1.d.ts
interface User {
    /** User ID */
    id: string;
}

// file2.d.ts
interface User {
    /** Can have different comment */
    name: string;
}
```
**关键**：TypeScript **不强制注释一致**。

#### Java多个.class文件
```java
// 同一个类可以在多个jar包中
lib-1.0.jar  → com.example.MyClass (旧注释)
lib-2.0.jar  → com.example.MyClass (新注释)
// CLASSPATH决定使用哪个，注释可以不同
```

## 最终决策：方案1

**只验证核心：签名 + 类型**

### 核心验证（强制）
```python
signature_match = existing.signature == func_info.signature  # 必须一致
type_match = existing.func_type == func_info.func_type      # 必须一致
```

### 允许不同
```python
# docstring可以不同
if not docstring_match:
    print("📝 docstring不同（允许，建议添加链接到主定义）")
```

## 理由

### 1. 符合人性
- 人类容易忘记在多处同步更新docstring
- 维护重复内容是负担
- 通过链接关联比强制复制更实用

### 2. 参考成熟语言
- C# partial class不要求注释一致
- TypeScript declaration merging允许注释补充
- Java多版本共存不要求文档一致

### 3. 实用主义
- **签名是接口契约** - 必须严格
- **类型是语义保证** - 必须严格
- **Docstring是辅助说明** - 可以灵活

### 4. 鼓励链接而非复制

**推荐模式**：
```markdown
<!-- 主定义 -->
## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
"""
完整的docstring...
"""

<!-- 引用定义 -->
## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
"""
→ 详细说明见: [self_awareness.md](../knowledge/self_awareness.md#create_subagent)
本文档关注实现细节...
"""
```

## 实现效果

### Partial定义被正确识别
```
✅ Partial定义: @创建子智能体
   主定义: test_partial_function.md
   也出现在: self_awareness.md
   验证核心: 签名✓ 类型✓
   📝 docstring不同（允许，建议添加链接到主定义）
```

### 索引记录完整信息
```json
{
  "create_subagent": {
    "signature": "agent_type, domain, requirements, model, parent_knowledge",
    "all_locations": [
      "test_partial_function.md",
      "self_awareness.md"
    ],
    "is_partial": true
  }
}
```

### Agent加载所有位置
```
使用@创建子智能体时
→ 加载 test_partial_function.md（引用+链接）
→ 加载 self_awareness.md（主定义）
→ Agent获得完整知识
```

## 发现的Partial定义

通过这个机制，发现系统中已经存在的partial定义：

1. **@创建子智能体** - 测试文件 + self_awareness.md
2. **@修复测试** - auto_trigger_expert.md + test_fixing_function.md
3. **@睡眠巩固** - sleep_consolidation.md + KNOWLEDGE_FUNCTION_REFACTOR.md

这些都是签名和类型一致，但docstring不同的情况。

## 设计原则总结

### 必须一致（强制验证）
- ✅ **函数名** - 同一个@函数
- ✅ **签名** - 参数列表相同
- ✅ **类型** - contract/soft相同

### 允许不同（鼓励链接）
- 📝 **Docstring** - 可以从不同角度解释
- 🔗 **建议添加链接** - 关联主定义和引用定义
- 💡 **补充说明** - 每个文件可以补充不同内容

### Unix哲学
- 不删除旧版本
- PATH优先级控制
- 警告而非错误
- 向后兼容

## 结论

**接受人性的局限，通过机制而非强制保证质量**

- 签名一致：核心契约，必须严格
- Docstring灵活：允许不同，鼓励链接
- 类型一致：语义保证，必须严格
- 实用主义：降低维护成本，提高易用性

这是"完美主义"和"实用主义"之间的正确平衡点。