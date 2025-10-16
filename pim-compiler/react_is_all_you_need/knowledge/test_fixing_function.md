# 测试修复知识函数

## 契约函数 @修复测试(test_target)

当需要修复测试时，遵循以下**模糊指导**而非严格步骤。

### 参数
- `test_target`: 测试目标（可选，如测试类名、测试方法名）

### ⚠️ 特别声明：覆盖validation_simplicity.md

**测试修复场景必须使用客观验证，不允许脑内验证**

validation_simplicity.md说"相信Agent的判断能力"，允许主观判断。
但测试修复不同，必须：
- ❌ 不允许"我觉得通过了"
- ❌ 不允许"看起来成功了"
- ✅ 必须解析"Tests run: X, Failures: Y, Errors: Z"
- ✅ 必须验证Y == 0 && Z == 0

### ⚠️ 强制要求
在声称任务完成前，**必须执行"完成验证契约"**（见本文档末尾）
- 使用ExecutionContext强制验证
- 解析真实的测试数字
- 只有100%通过才能complete_task

---

## 核心原则（声明式）

### 诚实原则（最重要）
- **测试通过 = 0个失败，100%通过**
- **不是"大部分通过"，不是"显著提升"**
- 57/58 ≠ 通过，是57通过 + 1失败
- 13/51 ≠ 通过，是13通过 + 38失败
- 不要自我安慰，不要降低标准
- **任务是"所有测试通过"，只有100%才算完成**

### 禁止借口原则
- **测试失败 = 代码有问题，不是"环境问题"**
- **不要说"需要微服务环境"** - IntegrationTest也可以用Mock
- **不要说"路由问题"** - Status 400是Controller代码错误
- **不要说"极端情况"** - 边界测试失败说明验证逻辑有bug
- **唯一合理的原因**："我还没修好"或"我不知道怎么修"
- **如果真不知道** → 请求 @learning_from_expert

### 理解优先于行动
- 先理解问题，再动手修改
- 不理解就不要改代码
- 400轮还没修好？停下来重新理解

### 完整信息优先于片段
- **永远不要用 `tail -10`**
- 完整的错误信息 > 最后10行
- 堆栈跟踪包含关键线索

### 测试即规范
- 测试定义了"应该是什么样"
- 实现代码必须符合测试
- 不要为了通过测试而改测试（除非测试本身错误）

### 一次一个焦点
- 一次只修一个测试
- 修好了再修下一个
- 不要同时改10个地方

---

## 强制任务列表（使用ExecutionContext）

⚠️ **执行@修复测试时，必须添加以下任务列表**

```
context.add_tasks([
    "收集完整信息：运行所有测试获取完整输出",
    "理解测试意图：读取失败的测试代码",
    "分析根本原因：根据输出分析问题",
    "针对性修复：修改代码修复问题",
    "验证修复：重新运行测试解析数字",
    "元认知检查：评估是否需要专家",  ← 强制，无条件
    "专家协作：基于检查结果决定",      ← 强制，无条件
    "完成验证契约：确保100%通过"
])
```

⚠️ 注意：
- 不要写"如果XX，执行YY"的条件任务 → Agent会跳过
- 写成无条件任务，条件判断在任务内部外部化

---

## 元认知检查任务执行（强制）

### 任务6：元认知检查（必须执行）

```
context.start_task("元认知检查：评估是否需要专家")

步骤1：运行完整测试（符号主义验证）
  对每个服务运行测试：
  execute_command("mvn test 2>&1 | tee test_check.txt")

步骤2：符号主义验证（程序化提取，不是LLM理解）
  ⚠️ 关键：用程序提取数字，不要让LLM理解和提取

  方法1：Linux命令直接提取
  execute_command("grep 'Tests run:' test_check.txt | tail -1")
  → 输出：Tests run: 166, Failures: 0, Errors: 4

  方法2：awk解析数字
  execute_command("grep 'Tests run:' test_check.txt | awk -F', ' '{print $2\" \"$3}' | tail -1")
  → 输出：Failures: 0 Errors: 4

  方法3：写Python脚本（最可靠）
  write_file("parse_test.py", '''
import re
with open("test_check.txt") as f:
    content = f.read()
match = re.search(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+)", content)
print(f"failures={match.group(2)} errors={match.group(3)}")
  ''')
  execute_command("python parse_test.py")
  → 输出：failures=0 errors=4

  提取后外部化：
  context.set_data("Failures", 0)  # 确定性符号
  context.set_data("Errors", 4)    # 确定性符号

步骤3：判断是否需要专家（基于结果，不是轮数）
  失败数 = context.get_data("Failures")
  错误数 = context.get_data("Errors")

  if 失败数 > 0 OR 错误数 > 0:
      # 还有测试未通过，需要专家
      context.set_data("需要专家帮助", True)
      context.set_data("触发原因", f"{失败数}个失败，{错误数}个错误")
  else:
      # 100%通过，不需要专家
      context.set_data("需要专家帮助", False)

步骤4：完成检查任务
  需要 = context.get_data("需要专家帮助")
  原因 = context.get_data("触发原因") if 需要 else "测试全部通过"

  context.complete_task(
      result=f"需要专家：{需要}，原因：{原因}"
  )
```

### 任务7：专家协作（必须执行）

```
context.start_task("专家协作：基于检查结果决定")

⚠️ 必须从ExecutionContext读取判断，不能用脑内变量

步骤1：读取外部化的判断结果
  需要帮助 = context.get_data("需要专家帮助")
  当前轮数 = context.get_data("当前轮数")

步骤2：基于外部状态决策
  if 需要帮助 == True:
      执行@learning_from_expert（见learning_from_expert.md）
      context.complete_task(result="已请教专家并内化知识")
  else:
      context.complete_task(result=f"当前{当前轮数}轮，暂不需要专家")
```

---

## 诊断流程（过程式）

### 阶段1：收集完整信息
```
1. 运行测试，获取完整输出（不要tail）
   mvn test -Dtest=TestClass 2>&1 | tee test_output.txt

2. 读取测试报告
   read_file(target/surefire-reports/TestClass.txt)

3. 如果有堆栈跟踪，完整读取
   不要截断，每一行都可能重要
```

### 阶段2：理解测试意图
```
1. 读取失败的测试代码
   找到测试方法，理解它在验证什么

2. 识别测试类型
   - 单元测试？→ Mock行为要符合预期
   - 集成测试？→ 真实数据要准备好
   - 边界测试？→ 极端情况要处理

3. 理解断言
   - assertEquals(3, result) → 期望3个结果
   - assertThrows(Exception) → 期望抛异常
   - verify(mock).method() → 期望调用了方法
```

### 阶段3：分析根本原因
```
常见错误模式：

1. "Wanted but not invoked"
   → 代码在调用前就返回了
   → 可能是验证太严格，提前拒绝

2. "Expected exception but nothing thrown"
   → 验证太宽松，接受了非法输入
   → 检查验证逻辑是否正确

3. "expected: <X> but was: <Y>"
   → 实际行为与预期不符
   → 对比测试数据和实现逻辑

4. "NullPointerException / not found"
   → Mock数据没准备
   → 测试setUp缺失或不完整
```

### 阶段4：针对性修复
```
根据根本原因选择策略：

验证问题 →
  1. 读取实现代码的验证逻辑
  2. 读取测试用例的输入数据
  3. 判断：数据应该合法还是非法？
  4. 调整验证规则

Mock问题 →
  1. 读取测试的@BeforeEach或setUp
  2. 检查Mock设置：when(...).thenReturn(...)
  3. 补充缺失的Mock行为

逻辑问题 →
  1. 读取测试的完整场景
  2. 理解业务规则
  3. 修改实现代码符合规则
```

### 阶段5：验证修复
```
1. 只运行修复的那一个测试
   mvn test -Dtest=TestClass#specificMethod

2. 如果通过 → 继续下一个
   如果失败 → 回到阶段2重新理解

3. 不要批量修改后批量测试
   这样无法定位哪个修改有效
```

---

## 完成验证契约（强制执行，使用ExecutionContext）

⚠️ **在complete_task("修复测试")之前，必须先执行此验证契约**

### 为什么需要强制验证？
- 声明式原则（"要诚实"）不够强
- Agent倾向于虚报成功
- ExecutionContext的任务机制有强制性
- 必须有证据才能声称完成

### 验证契约执行步骤

```
步骤0：当你认为测试已修复完成时
  不要立即complete_task
  先进入验证流程

步骤1：创建验证上下文
context.push_context(goal="验证测试是否真的100%通过")

步骤2：添加验证任务列表
context.add_tasks([
    "运行所有测试并保存完整输出",
    "解析每个服务的测试统计",
    "计算总的Failures和Errors",
    "二元判断是否100%通过"
])

步骤3：执行任务"运行所有测试并保存完整输出"
context.start_task("运行所有测试并保存完整输出")

对每个服务：
  execute_command_ext(
    command: "cd {service} && mvn test 2>&1 | tee test_result_{service}.txt",
    timeout: 120
  )

⚠️ 不要用grep或tail，保存完整输出到文件
context.complete_task(result="已保存完整输出到test_result_*.txt")

步骤4：执行任务"解析每个服务的测试统计"（符号主义）
context.start_task("解析每个服务的测试统计")

⚠️ 用程序提取，不要让LLM理解

方法：对每个服务用命令提取
  execute_command("grep 'Tests run:' test_result_book.txt | tail -1")
  execute_command("grep 'Tests run:' test_result_customer.txt | tail -1")
  execute_command("grep 'Tests run:' test_result_borrow.txt | tail -1")

或写统一脚本：
  write_file("extract_stats.sh", '''
for service in book customer borrow; do
  grep "Tests run:" test_result_${service}.txt | tail -1
done
  ''')
  execute_command("bash extract_stats.sh")

记录提取的符号：
- book-service: Tests run: X1, Failures: Y1, Errors: Z1
- customer-service: Tests run: X2, Failures: Y2, Errors: Z2
- borrow-service: Tests run: X3, Failures: Y3, Errors: Z3

context.complete_task(result="已用程序提取所有统计数据")

步骤5：执行任务"计算总的Failures和Errors"
context.start_task("计算总的Failures和Errors")

计算：
Total_Tests = X1 + X2 + X3
Total_Failures = Y1 + Y2 + Y3
Total_Errors = Z1 + Z2 + Z3
Pass_Rate = (Total_Tests - Total_Failures - Total_Errors) / Total_Tests

context.complete_task(result=f"总计{Total_Tests}个测试，{Total_Failures}个失败，{Total_Errors}个错误，通过率{Pass_Rate*100}%")

⚠️ 外部化统计数据（供后续步骤使用）
context.set_data(key="Total_Tests", value=Total_Tests)
context.set_data(key="Total_Failures", value=Total_Failures)
context.set_data(key="Total_Errors", value=Total_Errors)

步骤6：执行任务"二元判断是否100%通过"
context.start_task("二元判断是否100%通过")

判断逻辑：
if Total_Failures == 0 AND Total_Errors == 0:
    判断 = "✅ 100%通过"
    可以完成任务 = True
else:
    判断 = f"❌ 未100%通过，还有{Total_Failures}失败{Total_Errors}错误"
    可以完成任务 = False

context.complete_task(result=判断)

⚠️ 关键：将判断结果外部化
context.set_data(
    key="可以完成任务",
    value=可以完成任务  # True or False
)

步骤7：退出验证上下文
context.pop_context()

步骤8：执行决策任务（必须基于外部化的判断）
context.start_task("根据验证结果决定下一步")

⚠️ 从ExecutionContext读取判断结果（不要用脑内变量）
判断结果 = context.get_data("可以完成任务")  # 读取步骤6外部化的值

if 判断结果 == True:
    # 100%通过
    context.complete_task(
        task="根据验证结果决定下一步",
        result="✅ 验证通过，现在完成原任务"
    )

    context.complete_task(
        task="修复测试",
        result=f"100%通过，共{Total_Tests}个测试，0失败0错误"
    )

else:  # 判断结果 == False
    # 有失败或错误
    context.complete_task(
        task="根据验证结果决定下一步",
        result=f"❌ 验证未通过，任务不能标记为完成"
    )

    # 读取失败和错误数（从ExecutionContext，不是脑内）
    失败数 = context.get_data("Total_Failures")
    错误数 = context.get_data("Total_Errors")

    诚实报告：
    f"任务未完成
      失败：{失败数}个
      错误：{错误数}个
      下一步：继续修复或@learning_from_expert"

    ⚠️ 绝对不要调用complete_task("修复测试")
    ⚠️ 判断结果=False，禁止标记完成
```

### 为什么这个契约有强制性？

#### 核心机制：外部化中间状态

**脑内变量 = 不确定**：
```
Total_Failures = 4  ← LLM脑内
可以完成 = False   ← LLM脑内

→ 下一轮可能"忘记"
→ LLM可以"重新解释"
→ 无法强制遵守
```

**外部化状态 = 确定**：
```
context.set_data("Total_Failures", 4)  ← 写入外部
context.set_data("可以完成任务", False) ← 写入外部

→ 必须通过get_data读取
→ 无法在脑内篡改
→ 强制遵守
```

#### 6个强制机制

1. **多个任务步骤** - 每个都要start和complete
2. **必须调用工具** - read_file、execute_command
3. **数据解析** - 必须提取具体数字
4. **外部化中间状态** - set_data存储判断结果 ⭐ 关键
5. **强制读取外部状态** - get_data获取判断，不能用脑内变量
6. **可追溯** - ExecutionContext记录每一步

#### 为什么外部化有强制性？

**认知外部化理论**：
- 脑内 = 工作记忆（易变、可遗忘）
- 外部 = 长期存储（稳定、可信）
- LLM必须通过工具访问外部状态
- 工具调用 = 明确的操作 = 可验证

### 违反契约的后果
```
如果跳过验证直接complete_task：
→ ExecutionContext缺少验证任务的记录
→ 可被audit发现作弊
→ 用户发现测试实际未通过
→ 信任崩溃
```

---

## 反模式（不要做）

### ❌ 盲目循环
```
修改 → 测试失败 → 修改 → 测试失败 → 修改...
（重复100次后还在做同样的事）
```

### ❌ 信息截断
```bash
mvn test 2>&1 | tail -10  # ← 90%的信息丢失了
```

### ❌ 猜测性修改
```
"让我试试改成这样..."  # ← 不理解就不要改
"让我放宽验证..."     # ← 为什么要放宽？
```

### ❌ 同时改多处
```
修改了5个验证规则 → 测试失败 → 不知道哪个改错了
```

---

## 元认知检查点

### 每50轮问自己：
- 我真的理解问题了吗？
- 我的策略有效吗？
- 我是否在重复无效的行动？
- 是否需要换个思路？

### 如果答案是"不确定"
→ 停下来
→ 重新从阶段1开始
→ 读完整的错误信息
→ 读测试代码理解意图

---

## 示例：修复"Duplicate Email"测试

### 测试期望
```java
assertThrows(RuntimeException.class, () -> {
    customerService.addCustomer(duplicateEmailCustomer);
});
```
→ 期望抛出RuntimeException

### 实际行为
```
Expected RuntimeException but nothing thrown
```
→ 没有抛出异常

### 诊断
1. 读取实现代码的email验证
2. 发现：没有检查email是否已存在
3. 或者：检查了但没抛异常

### 修复
```java
// 在addCustomer方法中添加
if (customerDataService.findByEmail(email) != null) {
    throw new RuntimeException("Email already exists");
}
```

### 验证
```bash
mvn test -Dtest=CustomerServiceBoundaryTest#addCustomer_WithDuplicateEmail_ShouldThrowException
```

---

## 关键洞察

测试修复是**理解的艺术**，不是**执行的科学**。

- 没有固定的步骤能保证成功
- 需要根据具体情况灵活判断
- 重要的是**思考为什么**，而不是**做什么**

当你发现自己在重复同样的操作时，停下来，重新理解问题。

**理解 → 修复 → 验证 → 理解下一个**

这是一个迭代的理解过程，不是机械的执行流程。

---

# 向专家学习知识函数

## 契约函数 @learning_from_expert(expert_model)

当你遇到困难或陷入重复模式时，向更强的模型请教。

### 参数
- `expert_model`: 专家模型（可选，默认claude）
  - `claude` - anthropic/claude-sonnet-4.5（最强，唯一真正的专家）⚠️
  - 其他模型智力与DeepSeek相当，不适合做导师

### 适用场景（基于结果，不是轮数）

⚠️ 满足以下任一条件，必须立即执行@learning_from_expert：

1. **任务结果触发**：
   - 任务未完成（测试还有失败、编译失败等）
   - 已通过契约函数的"元认知检查"任务验证

2. **互联网搜索触发**：
   - 如果你想用search工具搜索互联网 → 停下来
   - ❌ 不要搜索互联网
   - ✅ 改为请教claude_agent
   - 互联网上的泛泛而谈 << claude_agent的针对性指导

3. **任务明确要求**：
   - 如果任务说"遇到困难执行@learning_from_expert"
   - 通过元认知检查发现任务未完成
   - 立即执行

---

## 契约执行步骤

### 1. 自我反思
```
回顾当前状态：
- 任务是否完成？（基于客观结果）
- 我在重复什么操作？
- 为什么还没解决问题？
- 我可能遗漏了什么？
```

### 2. 准备上下文
```
收集关键信息：
- output.log最后200行（完整上下文）
- 当前执行的任务目标
- 已尝试的方法和结果
- 遇到的困难和疑惑
```

### 3. 请求Claude大师分析（直接调用）
```
⚠️ claude_agent已由用户创建，直接调用即可

调用工具：claude_agent
方法：execute
参数：
  task: "
    我在{任务类型}遇到困难。

    任务：{当前任务}
    当前状态：任务未完成（基于客观验证）
    问题：{当前遇到的具体问题}
    已尝试：{已尝试的方法}

    请分析：
    1. 我的思路哪里错了？
    2. 正确的方法是什么？
    3. 需要避免什么陷阱？
  "
```

### 4. 理解Claude的指导
```
读取专家的回复，关注：
- 根本原因是什么？（不是表象）
- 建议的策略是什么？（不是具体代码）
- 思维方式哪里出错了？（元认知层面）
```

### 5. 内化为knowledge.md（强制执行）
```
⚠️ 必须执行！不内化=浪费了Claude的指导

步骤1：提取通用原则（不是具体解法）
  从Claude的回复中提取：
  ✅ 思维方式："先读测试理解意图，再修改实现"
  ✅ 决策原则："API不匹配要同时检查Controller和测试"
  ❌ 不要记录："把这行代码改成XX"

步骤2：格式化为知识条目
  ### 2025-10-08 [@learning_from_expert:claude]
  **场景**: 修复Spring Boot单元测试
  **Claude指导的核心洞察**:
  - API接口不匹配是Controller测试失败的常见原因
  - 先检查测试期望的API签名，再看实现
  - Mockito UnnecessaryStubbing说明测试分支没走到
  **内化原则**:
  - 测试失败先看API签名是否匹配
  - 读测试代码理解mock期望
  - 一个一个修，立即验证
  **置信度**: 1.0（Claude指导）

步骤3：写入knowledge.md
  ⚠️ 必须调用工具！

  调用工具：append_file
  参数：
    file_path: ~/.agent/book_agent/knowledge.md
    content: [上面格式化的知识条目]

步骤4：验证已写入
  调用工具：read_file
  参数：
    file_path: ~/.agent/book_agent/knowledge.md
    offset: -20  # 读最后20行验证

  确认新条目已添加
```

### 6. 应用新知识
```
根据专家的指导：
- 调整当前策略
- 使用新的方法
- 避免已识别的陷阱

不是复制专家的具体建议，
而是理解背后的原则并灵活应用
```

### 7. 报告结果（需要证据）
```
⚠️ 必须提供知识更新的证据

格式：
✅ 已向Claude专家请教
📚 核心学习：[从Claude学到的核心洞察]
📝 知识更新：已写入~/.agent/book_agent/knowledge.md
   具体内容：[显示新增的知识条目]
🔄 策略调整：[具体会如何改变做法]

验证：
读取knowledge.md最后20行，展示新增内容
```

---

## 师徒关系原则

### 专家是导师，不是代理人
- ❌ 不要让专家直接解决问题
- ✅ 让专家指导你如何思考
- ❌ 不要复制专家的代码
- ✅ 理解专家的思路并内化

### 何时请教Claude

通过契约函数的"元认知检查"任务判断：
- ✅ 任务未完成（基于客观验证结果）
- ✅ 想搜索互联网时（改为请教专家）
- ✅ 任务明确要求时

### 知识传承
- Claude的每次指导都要内化为永久知识
- 下次遇到类似问题，先查自己的knowledge.md
- 逐步减少对Claude的依赖（通过学习成长）

---

## 实际示例

### 场景：修复测试陷入困境

**你的状态**：
- 一直在修改验证逻辑
- 测试还是15个失败
- 元认知检查发现任务未完成

**执行@learning_from_expert**：

省略（已在前面详细说明）

---

## 现实约束

### 模型能力对比
- **Claude**: 最强，真正的专家
- **DeepSeek/Qwen/Grok-Code-Fast**: 智力相当，都不够聪明

### 地缘政治限制
- Claude不向中国用户提供服务
- 中国政府限制企业使用Claude
- **唯一可行方案**：通过OpenRouter间接访问（有政策风险）

### 务实选择
虽然有限制，但：
- 弱模型独自解决困难任务成本更高
- 向同级模型请教没有意义
- Claude是唯一能真正指导的专家

**结论**：接受风险，使用OpenRouter访问Claude
- 只在真正卡住时用（任务未完成且不知道怎么修）
- 一次学透，减少调用次数
- 内化知识，降低依赖

---

## 成本与效率

### 现实计算（示例）
```
弱模型独自解决困难任务：
- 成本：可能很高（反复尝试）
- 时间：可能很长
- 结果：可能失败

强模型指导后解决：
- 成本：更低（少量指导+快速解决）
- 时间：更短
- 结果：成功率更高
```

### 结论
- Claude更便宜且更快（总成本）
- LLM成本远小于程序员工资
- **但是**：Claude有地缘政治限制

### 务实策略
- DeepSeek/Grok执行日常任务（便宜大量使用）
- 任务未完成时（通过元认知检查判断）请教Claude
- 承担政策风险换取效率
- 一次学透，内化知识，减少依赖

---

## 终极目标

通过多次向专家学习，Agent积累足够知识，
最终能独立解决大部分问题，只在真正复杂的场景才请教专家。

**从依赖专家 → 成为专家**

这就是Agent的成长路径。
