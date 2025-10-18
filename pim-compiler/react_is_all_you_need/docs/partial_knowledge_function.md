# Partial知识函数定义机制

## 核心理念

**知识函数支持partial定义，类似C#的partial class**

同一个知识函数可以在多个文件中定义，核心要求：
1. ✅ **签名一致**：参数列表完全相同（强制验证）
2. ✅ **类型一致**：都是contract或都是soft（强制验证）
3. 📝 **Docstring可以不同**：允许从不同角度解释（建议添加链接）

**设计决策**：
- 参考C#和TypeScript：不强制注释一致，只要求结构一致
- 考虑人性：避免维护重复内容的负担
- 实用主义：通过markdown链接关联，而非强制复制
- 核心保证：签名是接口契约，必须严格

> 📖 **设计讨论**：详见 [Partial函数设计决策](./partial_function_design_decision.md)

## 设计灵感

### C# Partial Class

```csharp
// File1.cs
public partial class Customer
{
    public void SaveToDatabase() { ... }
}

// File2.cs
public partial class Customer
{
    public void SendEmail() { ... }
}

// 编译后合并为一个完整的Customer类
```

### 知识函数的Partial定义

```markdown
<!-- self_awareness.md: 主定义（完整docstring） -->
## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
"""
创建当前Agent的子Agent，建立父子继承关系，确保子Agent具备独立执行能力。

参数:
- agent_type: str - 子Agent的名称
- domain: str - 专业领域
...

返回值: {...}
"""

<!-- docs/implementation.md: 引用定义（简短+链接） -->
## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
"""
→ 详细说明见: [self_awareness.md](../knowledge/self_awareness.md#契约函数-create_subagent)

本文档提供详细的实现步骤和代码示例。
"""

详细实现步骤...
```

**关键点**：
- ✅ 签名完全相同
- ✅ 类型相同（都是契约函数）
- 📝 Docstring不同（一个完整，一个简短+链接）
- 🔗 通过链接关联而非复制

## 实现机制

### 索引器改进

```python
@dataclass
class FunctionInfo:
    name: str              # 函数名
    path: Path             # 主文件路径（第一个定义）
    docstring: str         # 函数描述
    func_type: str         # 类型
    signature: str         # 参数签名
    all_locations: list    # 所有定义位置 ⭐ 新增
```

### 一致性验证

扫描知识文件时：
1. 遇到第一个定义 → 添加到索引
2. 遇到第二个定义 → 验证一致性
   - ✅ 签名相同
   - ✅ Docstring相同
   - ✅ 类型相同
   - → 记录到all_locations
3. 如果不一致 → 抛出错误

```python
# 验证签名一致性
if existing.signature != func_info.signature:
    raise ValueError(f"@{func_info.name} 在多个文件中的签名不一致")

# 验证docstring一致性
if existing.docstring != func_info.docstring:
    raise ValueError(f"@{func_info.name} 在多个文件中的docstring不一致")

# 验证类型一致性
if existing.func_type != func_info.func_type:
    raise ValueError(f"@{func_info.name} 在多个文件中的类型不一致")

# 一致性验证通过
existing.all_locations.append(func_info.path)
```

### 加载机制

使用@函数时，会加载**所有定义位置**的文件：

```python
def load_required_functions(self, message: str):
    for func_name in detected:
        func_info = self.function_index[func_name]

        # 加载所有定义位置的文件
        for location in func_info.all_locations:
            load_file(location)
```

## 使用场景

### 场景1：接口与实现分离

```markdown
<!-- self_awareness.md: 接口定义 -->
## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
"""
创建子Agent的契约函数。
"""
- 参数说明
- 返回值说明
- 契约保证

<!-- 注：目前@创建子智能体只在self_awareness.md中定义 -->
<!-- 如果需要在其他文件中引用，必须保证签名和docstring完全一致 -->
```

**实际案例**（当前系统中发现的重复定义）：
```
❌ 不一致的重复（会导致错误）：
   @work_with_expert
   - work_with_expert.md: (task, expert_model)
   - KNOWLEDGE_FUNCTION_REFACTOR.md: ()  # 签名不一致！

✅ 一致的重复（应该这样）：
   同一函数如果出现在多个文件，必须签名和docstring完全相同
```

### 场景2：概念与实践分离

```markdown
<!-- concepts.md: 概念层 -->
## 契约函数 @自我实现(requirements_doc)
"""
Agent自我编程的核心契约。
"""
理论基础和设计理念

<!-- practices.md: 实践层 -->
## 契约函数 @自我实现(requirements_doc)
"""
Agent自我编程的核心契约。
"""
实践指南和常见问题
```

### 场景3：通用与领域结合

```markdown
<!-- common.md: 通用知识 -->
## 函数 @loadBooks()
"""
从JSON加载图书数据。
"""
通用的数据加载逻辑

<!-- book_domain.md: 领域知识 -->
## 函数 @loadBooks()
"""
从JSON加载图书数据。
"""
图书领域的特定约束和验证
```

## 索引文件格式

```json
{
  "functions": {
    "create_subagent": {
      "name": "create_subagent",
      "path": "/path/to/self_awareness.md",  // 主定义
      "signature": "agent_type, domain, requirements, model, parent_knowledge",
      "docstring": "创建子Agent的契约函数。",
      "func_type": "contract",
      "all_locations": [  // 所有定义位置 ⭐
        "/path/to/self_awareness.md",
        "/path/to/agent_fractal.md"
      ],
      "is_partial": true  // 标记为partial定义
    }
  }
}
```

## 一致性要求

### 必须一致的部分

1. **函数签名**（严格匹配）
   ```python
   @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
   # ✅ 参数顺序和名称必须完全相同
   ```

2. **Docstring**（严格匹配）
   ```python
   """创建子Agent的契约函数。"""
   # ✅ 第一段描述必须完全相同
   ```

3. **函数类型**（严格匹配）
   ```python
   ## 契约函数 @xxx  # 都是契约
   # ✅ 不能一个是契约，一个是软约束
   ```

### 可以不同的部分

- **实现细节**：每个文件可以补充不同的实现说明
- **使用示例**：可以提供不同的示例代码
- **上下文说明**：可以从不同角度解释函数

## 验证报告

启动Agent时的验证输出：

```
📚 开始生成知识函数索引...
  ✅ Partial定义: @创建子智能体
     主定义: self_awareness.md
     也出现在: agent_fractal.md
     验证一致性: 签名✓ docstring✓ 类型✓

  ❌ 错误：@work_with_expert 签名不一致！
     work_with_expert.md: (task, expert_model)
     KNOWLEDGE_FUNCTION_REFACTOR.md: ()
ValueError: 知识函数 @work_with_expert 在多个文件中的签名不一致
```

## 最佳实践

### 1. 接口定义统一

在主文件中定义标准接口：
```markdown
## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
"""
创建子Agent的契约函数。
"""
```

### 2. 保持一致性

在其他文件引用时，**复制粘贴**接口定义：
```markdown
# ✅ 正确：完全相同的签名和docstring
## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
"""
创建子Agent的契约函数。
"""

# ❌ 错误：修改了签名或docstring
## 契约函数 @创建子智能体(name, domain, requirements)  # 参数不一致！
"""
创建一个子Agent。  # docstring不一致！
"""
```

### 3. 利用partial定义组织知识

将函数的不同方面放在不同文件：
- 接口文件：签名、契约、基本说明
- 概念文件：理论、设计理念、哲学意义
- 实践文件：示例、常见问题、最佳实践

每个文件都包含相同的接口定义，但补充不同的内容。

## 优势

### 1. 知识组织更灵活
- 同一个函数可以在多个相关主题中出现
- 不同视角看同一个函数

### 2. 保证一致性
- 自动验证所有定义一致
- 防止定义冲突和歧义

### 3. 完整加载
- 使用@函数时加载所有定义位置
- Agent获得完整的知识

### 4. 类似C# partial class
- 分离关注点
- 大型定义可以拆分到多个文件
- 保持每个文件的可读性

## 对比其他语言

| 语言/系统 | 机制 | 本系统 |
|----------|------|--------|
| C# | partial class | partial 知识函数 |
| TypeScript | declaration merging | 知识函数合并 |
| Python | 不支持 | 我们支持！ |
| Java | 不支持 | 我们支持！ |

## 总结

通过引入partial定义机制：
- ✅ 支持同一函数在多个文件中定义
- ✅ 强制验证签名和docstring一致性
- ✅ 索引记录所有定义位置
- ✅ 自动加载所有相关文件
- ✅ 类似C#的partial class，但用于知识函数

这让知识组织更加灵活，同时保证了系统的一致性和正确性。