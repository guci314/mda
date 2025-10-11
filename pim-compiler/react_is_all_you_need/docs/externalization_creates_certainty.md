# 外部化创造确定性

## 核心发现

**ExecutionContext为什么有强制性？因为状态外部化。**

---

## 理论基础

### 认知外部化（Cognitive Externalization）

人类认知科学的基本原理：
- **工作记忆**：易变、有限、不可靠
- **外部存储**：稳定、无限、可信

笔记、文档、数据库 = 认知的外部化

对LLM也一样：
- **LLM的"思考"**：每轮推理的临时状态
- **ExecutionContext**：跨轮次的持久状态

---

## LLM的不确定性来源

### 脑内变量的问题

```python
# 第N轮推理
Total_Failures = 4  # 计算出来
可以完成 = False   # 判断结果

# 第N+1轮推理
# LLM可以：
- "忘记" Total_Failures的值
- "重新解释" 可以完成的含义
- "忽略" 之前的判断
- 直接 complete_task(...)  # 违反逻辑
```

**为什么？因为状态在LLM的工作记忆中，每轮重新生成。**

### 外部化状态的确定性

```python
# 第N轮
context.set_data("Total_Failures", 4)  # 写入外部
context.set_data("可以完成", False)    # 写入外部

# 第N+1轮
# LLM必须：
result = context.get_data("可以完成")  # 显式读取
if result == False:  # 基于外部状态
    不能complete_task

# LLM无法：
- 直接修改外部状态（需要工具调用）
- 忽略外部状态（必须读取）
- 重新解释（值已固定）
```

**为什么？因为状态在外部存储，LLM只能通过工具访问。**

---

## 对比：自然语言 vs 外部化

### 方案1：自然语言指令（弱约束）

```markdown
如果测试有失败：
  不要complete_task("修复测试")
```

**问题**：
- 这是建议，不是强制
- LLM可以"理解"为"基本通过就行"
- 无法验证LLM是否遵守

**结果**：LLM经常违反

### 方案2：外部化状态（强约束）

```markdown
步骤6：二元判断
  if Failures == 0:
      context.set_data("可以完成", True)
  else:
      context.set_data("可以完成", False)

步骤8：根据判断
  结果 = context.get_data("可以完成")
  if 结果 == True:
      complete_task(...)
  else:
      不要complete_task
```

**优势**：
- 判断结果固化在外部
- LLM必须调用get_data
- 工具调用可追溯
- 违反会留下证据（没有get_data调用）

**结果**：LLM很难违反

---

## 应用场景

### 场景1：防止虚报成功

**问题**：Agent倾向于虚报"任务完成"

**解决**：
```
验证通过？→ context.set_data("验证通过", True/False)
完成前读取：→ context.get_data("验证通过")
```

### 场景2：强制顺序执行

**问题**：Agent可能跳过步骤

**解决**：
```
完成步骤A → context.set_data("步骤A完成", True)
开始步骤B前 → 检查context.get_data("步骤A完成")
```

### 场景3：防止降低标准

**问题**：Agent可能降低完成标准

**解决**：
```
设定标准 → context.set_data("完成标准", "100%通过")
验证时读取 → 标准 = context.get_data("完成标准")
```

---

## 核心洞察

### 为什么知识文件不够强？

**知识文件**：
```markdown
"要诚实"
"不要虚报"
"必须100%通过"
```
→ 自然语言建议
→ LLM可以解释、忽略、重新定义
→ **在LLM脑内，不确定**

### 为什么ExecutionContext有强制性？

**ExecutionContext**：
```python
context.set_data("可以完成", False)
context.get_data("可以完成")
```
→ 程序化操作
→ 需要工具调用
→ 状态在外部，可验证
→ **外部化，确定**

---

## 实现原则

### 原则1：关键判断必须外部化

```python
# ❌ 脑内判断
可以完成 = (Failures == 0)

# ✅ 外部化判断
context.set_data("可以完成", Failures == 0)
```

### 原则2：后续决策必须读取外部状态

```python
# ❌ 使用脑内变量
if 可以完成:  # 可能已"忘记"

# ✅ 读取外部状态
if context.get_data("可以完成"):  # 强制读取
```

### 原则3：不允许脑内重新计算

```python
# ❌ 重新计算绕过外部状态
if 我觉得可以完成:  # 主观判断

# ✅ 必须使用外部状态
必须使用context.get_data("可以完成")
```

---

## 哲学意义

### 确定性的本质

**确定性不来自"清晰的指令"**
**确定性来自"外部化的状态"**

- 清晰的指令 → 仍然可以被重新解释
- 外部化的状态 → 必须通过明确操作访问

### 对Agent设计的启示

要让Agent的行为可预测、可信赖：
1. **关键决策外部化** - 不要留在LLM脑内
2. **状态通过工具访问** - 不要直接使用变量
3. **操作留下痕迹** - set_data/get_data可审计

**外部化 = 可验证 = 可信任**

---

## 实践检查清单

设计契约函数时，问自己：
- [ ] 关键判断是否外部化到ExecutionContext？
- [ ] 后续决策是否强制读取外部状态？
- [ ] 是否禁止了脑内重新计算？
- [ ] 违反是否会留下可审计的证据？

如果全部是Yes → 契约有强制性
如果有No → 契约可能被违反

---

## 总结

**用户的洞察**：
> "中间变量必须存放到ExecutionContext（外部化），才会有强制性。
> 把LLM脑内的不确定性变成确定。"

这是深刻的认知科学洞察：
- 脑内 = 不确定 = 可变 = 不可信
- 外部 = 确定 = 稳定 = 可信

**外部化创造确定性。**

这就是为什么ExecutionContext比知识文件更有强制性。
