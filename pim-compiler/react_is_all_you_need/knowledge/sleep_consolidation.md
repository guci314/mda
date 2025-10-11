# 睡眠式记忆巩固

## 契约函数 @睡眠巩固()

当对话历史超过阈值时，执行睡眠式记忆巩固（类似人类睡眠中的记忆处理）。

---

## 契约执行步骤

### 1. 重放记忆（Memory Replay）

```
读取完整对话历史（compact.md + 当前messages）

分析内容：
- 执行了哪些任务？
- 遇到了什么问题？
- 如何解决的？
- 哪些是重要的决策？
- 哪些是琐碎的细节？

输出：
关键事件列表（保留语义，删除执行细节）
```

### 2. 知识提取（双重提取）

```
从具体事件中提取两种知识：

具体事件：
"修复了CustomerControllerTest，原因是API签名不匹配
 Controller用POST /return + body
 测试用POST /return/{id}
 解决：改为路径参数"

↓ 提取陈述性知识（What - 事实、概念）

"Spring MVC的@PostMapping可以接收RequestBody或PathVariable
 MockMvc测试调用必须与Controller注解匹配
 RequestBody需要.content()传递JSON
 PathVariable需要在URL路径中传递"

↓ 提取过程性知识（How - 方法、步骤）

"Controller测试失败时的诊断流程：
 1. 对比Controller的@PostMapping注解
 2. 对比测试的mockMvc.perform()调用
 3. 检查参数传递方式是否一致
 4. 统一两边的API定义"

原则：
- 陈述性：提取事实、概念、配置（是什么）
- 过程性：提取方法、步骤、策略（如何做）
- 两者都要，互补
```

### 3. 知识整合（Memory Integration）

```
步骤1：读取现有knowledge.md
  了解已有的认知和经验

步骤2：分类整合

  陈述性知识 → knowledge.md的"核心能力"或"领域知识"章节：

  ### 2025-10-08 [@睡眠巩固-陈述性]
  **Spring MVC配置知识**:
  - @PostMapping支持RequestBody和PathVariable两种参数方式
  - MockMvc测试必须与Controller注解匹配
  - RequestBody用.content()，PathVariable在URL中

  **Mockito配置知识**:
  - 严格模式会检测不必要的stubbing
  - @MockBean作用域是整个测试类

  过程性知识 → knowledge.md的"决策逻辑"或"经验总结"章节：

  ### 2025-10-08 [@睡眠巩固-过程性]
  **Controller测试失败诊断流程**:
  1. 先看完整日志（已有知识）
  2. 对比Controller注解和测试调用
  3. 检查参数传递方式是否一致
  4. 统一API定义
  **置信度**: 0.9（实践验证）

步骤3：关联发现
  新陈述性知识与旧知识的关联：
  - "MockMvc必须匹配Controller" 关联到 "API契约测试"

  新过程性知识与旧知识的关联：
  - "Controller测试诊断" 关联到 "测试失败先看日志"
  - 形成完整的调试流程

步骤4：更新knowledge.md
  调用工具：append_file
  写入整合后的知识
```

### 4. 选择性遗忘（Selective Retention）

```
根据重要性分级保留：

高重要性（详细保留）：
- 关键问题的解决方法
- 重要的架构决策
- 反复验证的模式
→ 完整记录到knowledge.md

中重要性（只记模式）：
- 一般性问题的处理
- 常规操作
→ 抽象为模式，不记录细节

低重要性（删除）：
- 执行细节（"第3次尝试"）
- 中间失败（"这个方法不行"）
- 琐碎操作（"ls查看文件"）
→ 完全删除，不保留

判断标准：
- 置信度 > 0.8 → 高重要性
- 重复出现 > 3次 → 高重要性
- 解决了关键问题 → 高重要性
- 一次性操作 → 低重要性
```

### 5. 巩固输出（Consolidation Output）

```
生成两个文件：

1. compact.md（精简的线索）
   只保留关键事件的简要描述
   作为"索引"或"目录"
   不超过5K

2. knowledge.md（更新的知识）
   新增的模式和经验
   整合到已有认知网络
   持续进化

结果：
- 对话历史从70K压缩到5K
- 知识从N条增加到N+M条
- 认知网络更完整
```

---

## 与普通Compact的区别

### 普通Compact（当前）

```
输入：70K messages
处理：LLM总结
输出：5K compact.md

特点：
- 只是压缩
- 保留事件
- 独立存储
```

### 睡眠巩固（改进）

```
输入：70K messages + knowledge.md
处理：
  1. 重放（分析事件）
  2. 抽象（提取模式）
  3. 整合（与已有知识关联）
  4. 遗忘（选择性保留）
处理：
  - compact.md（5K，关键线索）
  - knowledge.md（更新，新增M条）

特点：
- 不只压缩，是巩固
- 提取模式，不只是事件
- 整合到知识网络
- 主动遗忘不重要的
```

---

## 触发时机

### 自动触发
```
if 当前messages tokens > 70K:
    自动执行@睡眠巩固
```

### 手动触发
```
用户：@睡眠巩固
或
任务完成后主动执行
```

---

## 关键原则

### 像睡眠一样工作

**睡眠不是休息**，而是：
- 重组记忆（具体→抽象）
- 巩固知识（短期→长期）
- 修剪连接（删除噪音）
- 整合认知（新+旧→完整）

**@睡眠巩固也应该**：
- 不只是保存历史
- 而是提炼知识
- 整合到认知网络
- 让Agent更"聪明"

### 输出验证

巩固后应该：
- ✅ compact.md更精简（<5K）
- ✅ knowledge.md更丰富（新增经验）
- ✅ 两者协同（compact索引→knowledge详情）
- ✅ 下次遇到类似问题能独立解决

---

## 与@learning的关系

### @learning（主动学习）
```
用户明确要求：@learning
→ 从当前会话提取经验
→ 写入knowledge.md

适用：
- 完成重要任务后
- 学到新知识时
```

### @睡眠巩固（自动巩固）
```
messages超过阈值自动触发
→ 压缩历史 + 整合知识
→ 更新compact.md和knowledge.md

适用：
- 长时间对话后
- 自动维护记忆
```

### 两者协同

```
日常：@learning（主动）
维护：@睡眠巩固（自动）

结果：
knowledge.md持续更新，永不过期
```

---

## 实施示例

### 场景：修复100个测试后

**输入**：
- 70K tokens对话历史
- 修复了58个服务的测试
- 各种尝试、失败、成功

**执行@睡眠巩固**：

步骤1：重放
```
关键事件：
1. 修复Jackson序列化问题
2. 修复API签名不匹配
3. 修复Mockito配置
4. 修复电话验证逻辑
...
```

步骤2：提取两种知识
```
陈述性知识（事实、概念、配置）：
- "Jackson默认不支持LocalDateTime序列化"
- "需要注册JavaTimeModule才能序列化Java 8时间类"
- "Mockito严格模式会检测不必要的stubbing"
- "@MockBean的作用域是测试类级别"
- "Feign默认使用Ribbon做服务发现"

过程性知识（方法、流程、策略）：
- "LocalDateTime序列化问题 → 添加JavaTimeModule"
- "Controller测试失败 → 检查API签名匹配"
- "Mockito UnnecessaryStubbing → 检查测试分支覆盖"
...
```

步骤3：分类整合
```
陈述性知识 → knowledge.md "核心能力"章节
过程性知识 → knowledge.md "经验总结"章节

发现关联：
- 陈述性："Jackson不支持LocalDateTime"
  + 过程性："添加JavaTimeModule"
  = 完整的知识单元
```

步骤4：遗忘
```
删除：
- "第3次尝试用XX方法"（低重要性）
- "ls查看文件"（琐碎）
- "mvn clean"（常规操作）

保留：
- API签名检查方法（高重要性）
- Jackson配置方案（可复用）
```

步骤5：输出
```
compact.md（5K）:
"修复了微服务测试，应用了API签名检查、Jackson配置等模式"

knowledge.md（新增）:

## 核心能力（陈述性知识）
### 2025-10-08 [@睡眠巩固]
**Spring Boot配置**:
- Jackson需要JavaTimeModule支持LocalDateTime
- Mockito严格模式检测不必要的stubbing
- @MockBean作用域是测试类级别
- Feign默认使用Ribbon服务发现

## 经验总结（过程性知识）
### 2025-10-08 [@睡眠巩固]
**测试修复流程**:
1. Controller测试失败 → 检查API签名匹配
2. LocalDateTime序列化错误 → 添加JavaTimeModule
3. Mockito UnnecessaryStubbing → 检查测试分支覆盖

两种知识互补，形成完整认知
```

---

## 核心价值

**记忆巩固 = 知识进化**

不是简单保存历史
而是从经验中学习
让Agent持续变"聪明"

**这就是真正的Agent成长机制！**
