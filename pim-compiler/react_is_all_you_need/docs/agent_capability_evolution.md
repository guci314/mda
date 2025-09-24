# Agent能力进化：为什么要更新agent_knowledge.md

## 核心洞察

**创建子Agent不只是历史事件，它改变了父Agent的能力边界。**

## 具体例子：订单Agent创建库存Agent

### 创建前的能力
```markdown
# agent_knowledge.md (创建前)
## 我的能力
- 接收订单
- 验证订单格式
- 计算订单金额
- 保存订单信息
```

### 创建库存Agent后
```markdown
# agent_knowledge.md (创建后 - 必须更新！)
## 我的能力
- 接收订单
- 验证订单格式
- 计算订单金额
- 保存订单信息
- **库存验证：通过库存Agent检查商品可用性** ✨
- **库存扣减：订单确认时自动扣减库存** ✨
- **库存查询：实时获取商品库存状态** ✨
```

### 能力的实质性改变

| 场景 | 创建前 | 创建后 |
|------|--------|--------|
| 处理订单 | 只能记录订单 | 可以验证库存并扣减 |
| 订单验证 | 只验证格式 | 验证格式+库存充足性 |
| 系统集成 | 独立运作 | 与库存系统联动 |

## 双重记录原则

### 1. experience.md（历史维度）
记录**事件**：
```markdown
## 创建历史
- 2024-01-01 10:30: 创建库存Agent
  - 原因：需要管理商品库存
  - 配置：使用MongoDB存储
  - 位置：~/.agent/inventory_agent/
```

### 2. agent_knowledge.md（能力维度）
记录**能力变化**：
```markdown
## 协作能力
- inventory_agent：库存管理
  - check_stock(sku): 检查库存
  - reserve_stock(sku, qty): 预留库存
  - deduct_stock(sku, qty): 扣减库存
```

## 判断标准：什么时候更新agent_knowledge.md？

### ✅ 需要更新的情况

1. **能力扩展**：
   - 创建了提供新功能的子Agent
   - 例：订单Agent创建库存Agent

2. **工作流改变**：
   - 子Agent改变了处理流程
   - 例：创建审批Agent后，订单需要审批

3. **接口新增**：
   - 可以调用新的服务
   - 例：创建通知Agent后，可以发送通知

### ❌ 不需要更新的情况

1. **纯执行任务**：
   - 子Agent只是执行一次性任务
   - 例：创建临时的数据迁移Agent

2. **独立运作**：
   - 子Agent完全独立，不影响父Agent
   - 例：创建独立的报表Agent

3. **替换实现**：
   - 只是换了个实现方式，能力没变
   - 例：用新Agent替代旧Agent

## 更新模板

### experience.md模板
```markdown
## [日期] 创建 [Agent名称]
- **目的**：[为什么创建]
- **功能**：[主要功能]
- **配置**：[关键配置]
- **集成点**：[如何协作]
```

### agent_knowledge.md模板
```markdown
## 扩展能力（通过子Agent）

### [子Agent名称]
- **能力域**：[如库存管理、用户认证等]
- **接口**：
  - `功能1(参数)`: 描述
  - `功能2(参数)`: 描述
- **使用场景**：
  - 场景1：如何使用
  - 场景2：如何使用
```

## 实际案例

### 案例1：电商系统
```
订单Agent
├── 创建 → 库存Agent（能力+）
├── 创建 → 支付Agent（能力+）
├── 创建 → 物流Agent（能力+）
└── 创建 → 通知Agent（能力+）

每次创建都扩展了订单处理能力！
```

### 案例2：数据处理
```
ETL Agent
├── 创建 → 抽取Agent（能力+）
├── 创建 → 转换Agent（能力+）
├── 创建 → 加载Agent（能力+）
└── 创建 → 监控Agent（能力+）

形成了完整的数据处理能力！
```

## 设计原理

### 为什么需要双重记录？

1. **关注点分离**：
   - experience = What happened（发生了什么）
   - knowledge = What I can do now（现在能做什么）

2. **时间vs能力**：
   - experience关注时间线
   - knowledge关注能力集

3. **调试vs使用**：
   - experience帮助调试和回溯
   - knowledge指导当前行为

### 生物类比

这就像生物进化：
- **基因突变**（创建子Agent） → 记录在DNA（agent_knowledge.md）
- **生活经历**（创建事件） → 记录在记忆（experience.md）

## 最佳实践

### 1. 创建时立即更新
```python
# 创建子Agent
inventory_agent = create_agent(...)

# 立即更新两个文件
update_experience("创建了库存Agent...")
update_knowledge("新增库存管理能力...")
```

### 2. 定期审查能力
```python
def review_capabilities():
    # 检查所有子Agent
    children = find_my_children()

    # 确保knowledge.md是最新的
    for child in children:
        ensure_capability_documented(child)
```

### 3. 能力继承
```markdown
# 父Agent的agent_knowledge.md
## 我的核心能力
- 订单处理
- 库存管理（通过inventory_agent）

# 创建子Agent时，子Agent应该知道：
"你的父Agent具有订单处理能力，可以调用"
```

## 结论

**创建子Agent = 能力进化**

这不仅是历史事件，更是能力的扩展。正确的做法是：

1. ✅ 在experience.md记录创建事件（When & Why）
2. ✅ 在agent_knowledge.md更新能力（What & How）
3. ✅ 保持两者同步，确保Agent知道自己的完整能力

记住：
> "Every child agent created is a new capability gained."
> "每个创建的子Agent都是获得的新能力。"