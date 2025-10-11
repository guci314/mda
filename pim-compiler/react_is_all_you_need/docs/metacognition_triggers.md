# 元认知触发机制

## 核心问题

Agent缺少自我监控能力：
- 不知道自己执行了多少轮
- 不知道自己是否在重复
- 不知道何时该求助

## 解决方案：强制元认知检查

### 在每个契约函数中添加检查任务

所有契约函数（@修复测试、@切换模型等）的任务列表必须包含：

```
tasks = [
    "主要工作任务1",
    "主要工作任务2",
    ...
    "元认知检查：评估是否需要专家",  ← 无条件，必须执行
    "专家协作：基于检查结果决定"     ← 无条件，必须执行
]
```

⚠️ 不要写成"如果XX，执行YY"的条件任务
→ Agent会跳过

✅ 写成无条件任务，但在任务内部检查条件（外部化）
→ Agent必须执行


### 元认知检查任务的执行步骤

```
步骤1：启动检查任务
context.start_task("元认知检查：是否需要专家帮助")

步骤2：获取当前轮数（外部化）
从output.log统计：grep "🤔 思考第" | tail -1
或使用内部计数器

context.set_data("当前轮数", 轮数)

步骤3：判断触发条件（外部化）
触发条件检查：
- 轮数 > 50 ?
- 发现重复模式？（连续10轮改同一文件）
- 多次失败？（同一测试失败3次）

if 满足任一条件:
    context.set_data("需要专家帮助", True)
    context.set_data("触发原因", "执行轮数超过50")
else:
    context.set_data("需要专家帮助", False)

步骤4：完成检查任务
判断结果 = context.get_data("需要专家帮助")
context.complete_task(
    result=f"需要专家：{判断结果}，当前轮数：{轮数}"
)

步骤5：根据判断执行
需要帮助 = context.get_data("需要专家帮助")

if 需要帮助 == True:
    context.start_task("执行@learning_from_expert")
    # 调用claude_agent...
    context.complete_task(result="已请教专家并内化知识")
else:
    # 继续主要任务
```

---

## 触发条件配置

## 判断标准：基于任务结果，不是过程指标

### 错误的判断方式
```
❌ 轮数 > 50 → 需要专家
  问题：多微服务系统几千轮都正常
  误判：轮数多 ≠ 遇到困难

❌ 执行时间 > 1小时 → 需要专家
  问题：大项目本来就慢
  误判：慢 ≠ 卡住
```

### 正确的判断方式（基于任务结果）

#### 测试修复任务
```
符号主义验证（程序化，不是LLM理解）：
  运行mvn test 2>&1 | tee test.txt

  用程序提取符号：
  execute_command("grep 'Tests run:' test.txt | tail -1 | awk -F', ' '{print $2\" \"$3}'")
  → 输出：Failures: 0 Errors: 4

  或写脚本：
  python parse_maven.py test.txt
  → 输出：0 4

  外部化：
  context.set_data("Failures", 0)  # 程序提取的数字
  context.set_data("Errors", 4)

判断：
  失败数 = context.get_data("Failures")
  错误数 = context.get_data("Errors")

  if 失败数 > 0 OR 错误数 > 0:
      context.set_data("需要专家", True)
  else:
      context.set_data("需要专家", False)
```

#### 编译任务
```
外部化验证：
  运行mvn compile → 解析结果
  context.set_data("编译结果", "SUCCESS" or "FAILURE")

判断：
  结果 = context.get_data("编译结果")
  if 结果 == "FAILURE":
      需要专家 = True
```

#### 部署任务
```
外部化验证：
  curl服务健康检查 → 解析状态码
  context.set_data("健康检查", 200 or 503)

判断：
  状态 = context.get_data("健康检查")
  if 状态 != 200:
      需要专家 = True
```

### 核心原则

**判断"需要帮助"的依据 = 任务的客观结果**

不是：
- ❌ 执行了多少轮
- ❌ 用了多长时间
- ❌ 操作了多少次

而是：
- ✅ 任务是否完成
- ✅ 结果是否符合标准
- ✅ 客观数据说明什么

---

## 多层协同

### 层1：代码层（基础设施）
```python
# react_agent_minimal.py
def execute(self, task):
    self.round_count = 0

    for round in range(max_rounds):
        self.round_count += 1

        # 自动监控
        if self.round_count == 50:
            print(f"⚠️ 已执行{self.round_count}轮，建议检查是否需要专家帮助")

        # 主循环...
```

### 层2：知识文件（规则定义）
```markdown
metacognition_triggers.md:
- 定义触发条件
- 定义检查方法
- 定义如何外部化
```

### 层3：契约函数（强制执行）
```markdown
@修复测试的任务列表：
- 必须包含"元认知检查"任务
- 使用ExecutionContext外部化判断
- 强制读取外部状态
```

### 层4：Description（LLM提示）
```python
claude_agent.description:
"在执行超过50轮时调用..."
```

---

## 实践模板

### 任何契约函数都应该包含

```
## 契约函数 @XXX

### 任务列表模板

context.add_tasks([
    "主任务1",
    "主任务2",
    ...
    "元认知检查：评估是否需要专家",  ← 必须
    "条件执行：如果需要，调用@learning_from_expert"  ← 必须
])

### 元认知检查执行

步骤1：获取轮数并外部化
  统计或读取 → context.set_data("轮数", X)

步骤2：判断并外部化
  检查条件 → context.set_data("需要专家", True/False)

步骤3：强制读取并执行
  if context.get_data("需要专家") == True:
      @learning_from_expert
```

---

## 关键洞察

**触发机制不是单点设计，而是系统工程**

需要：
1. **代码监控** - 提供轮数等基础数据
2. **知识规则** - 定义什么叫"困难"
3. **ExecutionContext** - 强制检查和外部化
4. **Description** - 提示LLM何时调用

**四层协同 → 可靠触发**

---

## 当前状态问题

book_agent执行50轮了，为什么没触发？

可能原因：
1. 任务列表没有"元认知检查"任务 ← 最可能
2. 知识文件改了但Agent用的是旧状态
3. 代码层没有监控和提示

解决：
- 立即：让Agent重新开始并使用新知识文件
- 长期：所有契约函数强制包含元认知检查任务
