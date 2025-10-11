# 自动触发专家指导机制

## 问题

Agent不会主动请教专家，即使：
- 执行了100+轮还未完成
- 重复同样操作50轮
- 任务明确说"遇到困难请教"

## 根本原因

### Agent缺少自我监控
```
Agent不知道：
- 我执行了多少轮？
- 我是否在重复？
- 我是否应该请教？
```

### "困难"是主观的
```
什么叫"遇到困难"？
→ 没有客观标准
→ Agent不会触发
```

---

## 解决方案：客观触发条件

### 在@修复测试函数中添加自动检查

```
每10轮检查一次：

步骤1：检查执行轮数
  从output.log或内部计数器获取当前轮数

步骤2：检查是否重复
  对比最近10轮的操作：
  - 如果连续5轮都在运行相同命令 → 重复
  - 如果连续5轮都在修改相同文件 → 重复

步骤3：触发条件判断
  if 执行轮数 > 50 and 发现重复模式:
      自动触发 @learning_from_expert

  if 执行轮数 > 100:
      强制触发 @learning_from_expert
```

---

## 客观重复检测

### 方法1：命令重复检测
```
记录最近10轮执行的命令
计算重复次数

例如：
轮1: mvn test -Dtest=CustomerServiceTest
轮2: edit_file(CustomerService.java)
轮3: mvn test -Dtest=CustomerServiceTest
轮4: edit_file(CustomerService.java)
轮5: mvn test -Dtest=CustomerServiceTest

检测到：重复模式（测试→编辑→测试）执行了5次
→ 陷入循环
→ 触发 @learning_from_expert
```

### 方法2：任务进度停滞检测
```
记录任务完成进度

例如修复测试：
轮10：5/13通过
轮20：6/13通过
轮30：6/13通过 ← 进度停滞
轮40：7/13通过

检测到：10轮内进度变化 < 2
→ 陷入瓶颈
→ 触发 @learning_from_expert
```

### 方法3：错误重复检测
```
记录最近的错误信息

例如：
轮15: "Expected exception but nothing thrown"
轮18: "Expected exception but nothing thrown"
轮22: "Expected exception but nothing thrown"

检测到：相同错误出现3次
→ 策略无效
→ 触发 @learning_from_expert
```

---

## 实施方案

### 在每个契约函数中添加监控

```markdown
## 契约函数 @修复测试(test_target)

...原有内容...

### 自动专家触发机制

每10轮执行以下检查：

1. 获取当前轮数
   从output.log统计"🤔 思考第X轮"的次数

2. 检查重复模式
   对比最近10轮的工具调用
   如果有5次以上相同模式 → 重复

3. 触发判断
   if 轮数 > 50 and 重复模式:
       执行 @learning_from_expert

   if 轮数 > 100:
       强制执行 @learning_from_expert

4. 触发后清零计数，避免重复触发
```

---

## 简化版：轮数触发

**最简单的触发机制**：

```
每个契约函数开头添加：

if 当前轮数 > 50:
    检查是否已请教过专家
    if 未请教:
        自动执行 @learning_from_expert
        continue执行原任务
```

---

## 元认知自检

Agent应该定期问自己：
```
每10轮：
- 我执行了多少轮了？
- 我是否在重复同样的操作？
- 如果超过50轮，我是否应该请教专家？
```

这需要在知识文件中明确告诉Agent：
```
### 元认知检查点（每10轮）

检查当前轮数：
统计output.log中"🤔 思考第X轮"

if 当前轮数 % 10 == 0:
    问自己：
    - 轮数是否超过50？
    - 是否在重复操作？
    - 是否应该请教专家？

    if 应该请教 and 未请教:
        立即执行 @learning_from_expert
```

---

## 关键洞察

**Agent不会主动自省**，需要：
1. 明确的触发条件（轮数>50）
2. 简单的检查方法（统计思考轮数）
3. 强制的执行要求（必须执行）

**自动触发 > 期待自觉**
