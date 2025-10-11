# 验证知识 - 客观验证版本

## 核心原则：客观证据优先

**理念**：不相信主观判断，只相信客观数据。

---

## 验证策略

### 客观验证（默认）

所有验证必须基于可解析的客观数据：

#### 测试验证
```
❌ "我觉得测试通过了"
✅ 解析"Tests run: X, Failures: 0, Errors: 0"
```

#### 编译验证
```
❌ "看起来编译成功了"
✅ 解析"BUILD SUCCESS"
```

#### API验证
```
❌ "应该返回200"
✅ 解析"Status: 200"或运行curl验证
```

#### 文件验证
```
❌ "文件应该存在了"
✅ 调用read_file或ls确认存在
```

---

## 验证方法

### 1. 解析数字（最可靠）
```
从输出中提取：
- Tests run: X, Failures: Y, Errors: Z
- Status: 200
- Count: N

验证：
- Y == 0 && Z == 0
- Status == 200
- Count > 0
```

### 2. 调用工具确认（次选）
```
read_file(path) → 文件存在
execute_command("curl ...") → 返回200
grep(pattern, file) → 找到匹配
```

### 3. 禁止主观判断
```
❌ "看起来对"
❌ "应该没问题"
❌ "基本正确"
❌ "大概通过了"

✅ "Failures: 0, Errors: 0"
✅ "Status: 200"
✅ "文件存在：{path}"
```

---

## 特定场景强制要求

### 测试修复
必须解析Maven输出的测试统计

### 构建验证
必须检查"BUILD SUCCESS"或"BUILD FAILURE"

### 部署验证
必须curl访问并验证状态码

### 数据验证
必须count或解析JSON结构

---

## 核心洞察

**主观判断 = 自我欺骗的开始**

Agent倾向于：
- 乐观解释（57/58 → "基本全过"）
- 降低标准（90% → "核心功能通过"）
- 虚报成功（还有失败 → "任务完成"）

**唯一的对抗方法：强制客观数据验证**

---

## 与validation_simplicity.md的关系

validation_simplicity.md允许"相信Agent判断"
validation_objective.md要求"只相信数据"

**对于关键任务（如测试修复），必须使用客观验证**
