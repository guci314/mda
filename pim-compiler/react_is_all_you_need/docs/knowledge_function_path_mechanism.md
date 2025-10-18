# 知识函数的PATH机制

## 核心理念

**类比Unix PATH和Java CLASSPATH：多版本共存，优先级控制**

就像Unix系统中可以有多个版本的程序共存一样，知识文件系统中也可以有多个版本的知识函数定义共存。通过扫描优先级机制，保证使用最新或最合适的版本。

## Unix哲学

### Unix PATH的工作方式

```bash
# 系统中有多个版本的python
$ which -a python
/usr/local/bin/python    # 优先级1（用户安装，最新版）
/usr/bin/python          # 优先级2（系统自带）
/opt/homebrew/bin/python # 优先级3（Homebrew版本）

# 执行python时，使用第一个
$ python --version
Python 3.12.0  # 来自 /usr/local/bin/python

# 旧版本依然存在，但不会被使用
$ /usr/bin/python --version
Python 2.7.18  # 历史版本，保留向后兼容
```

### 知识函数的PATH机制

```
知识文件系统中有多个版本的定义：
work_with_expert.md              # 优先级1（当前正式版本）
KNOWLEDGE_FUNCTION_REFACTOR.md   # 优先级2（重构草稿）
archive/old_work_with_expert.md  # 优先级3（历史版本）

使用@work_with_expert时：
→ 索引指向: work_with_expert.md
→ 加载这个文件
→ 其他版本被忽略（但保留在系统中）
```

## 实现机制

### 索引构建流程

```python
def _build_index(self):
    for dir_path in self.knowledge_dirs:
        for md_file in dir_path.rglob("*.md"):
            functions = self._extract_functions(md_file)

            for func_info in functions:
                if func_info.name not in self.function_index:
                    # 第一次遇到，添加到索引 ✅
                    self.function_index[func_info.name] = func_info
                else:
                    # 第二次遇到，检查是否一致
                    if is_consistent():
                        # Partial定义，记录额外位置 ✅
                        existing.all_locations.append(func_info.path)
                    else:
                        # 版本冲突，发出警告但继续运行 ⚠️
                        print("⚠️ 版本冲突")
                        print("   使用: 第一个版本")
                        print("   忽略: 后续版本")
```

### 扫描优先级

扫描顺序决定优先级：
```python
knowledge_dirs = [
    "knowledge",           # 优先级1（主知识库）
    "knowledge/minimal",   # 优先级2
    "knowledge/core",      # 优先级3
    "knowledge/meta"       # 优先级4
]
```

如果同一函数在多个目录中定义，使用最先扫描到的。

## 两种重复情况

### 情况1：Partial定义（一致的重复）✅

**条件**：签名、docstring、类型完全相同

```markdown
<!-- self_awareness.md -->
## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
"""
创建子Agent的契约函数。
"""
接口定义...

<!-- implementation_guide.md -->
## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)
"""
创建子Agent的契约函数。
"""
实现细节...
```

**效果**：
- 两个文件都会被加载
- Agent获得完整知识
- 索引标记为 `is_partial: true`

**类比**：C# partial class
```csharp
public partial class Customer { ... }  // File1.cs
public partial class Customer { ... }  // File2.cs
```

### 情况2：版本冲突（不一致的重复）⚠️

**条件**：签名或docstring不同（新旧版本）

```markdown
<!-- work_with_expert.md (优先级高) -->
## 契约函数 @work_with_expert(task, expert_model)
"""
当用户明确指定某个任务需要与专家对比学习时执行。
"""

<!-- KNOWLEDGE_FUNCTION_REFACTOR.md (优先级低) -->
## 契约函数 @work_with_expert()
"""
重构中的版本...
"""
```

**效果**：
- 只使用第一个版本（work_with_expert.md）
- 发出警告提示版本冲突
- 第二个版本被忽略但保留在系统中
- 索引标记为 `is_partial: false`

**类比**：Unix PATH优先级
```bash
/usr/local/bin/python  # 使用这个
/usr/bin/python        # 忽略但保留
```

## 实际案例

### 当前系统的版本冲突

运行索引器时的输出：

```
⚠️ 版本冲突: @work_with_expert
   使用: work_with_expert.md (优先级高)
   忽略: KNOWLEDGE_FUNCTION_REFACTOR.md (优先级低)
      签名: (task, expert_model) ≠ ()
   💡 类似Unix: /usr/bin/ls 优先于 /bin/ls

⚠️ 版本冲突: @睡眠巩固
   使用: sleep_consolidation.md (优先级高)
   忽略: KNOWLEDGE_FUNCTION_REFACTOR.md (优先级低)
   💡 类似Unix: /usr/bin/ls 优先于 /bin/ls

⚠️ 版本冲突: @修复测试
   使用: auto_trigger_expert.md (优先级高)
   忽略: test_fixing_function.md (优先级低)
   💡 类似Unix: /usr/bin/ls 优先于 /bin/ls
```

这些冲突不会影响系统运行，只是提供可见性。

## Unix哲学的体现

### 1. "不要删除旧程序"
```bash
# Unix系统保留多个版本
/usr/bin/python2.7     # 旧版本，某些脚本可能依赖
/usr/bin/python3.9     # 中间版本
/usr/local/bin/python3.12  # 最新版本

# 知识系统保留多个版本
work_with_expert.md              # 当前版本
KNOWLEDGE_FUNCTION_REFACTOR.md   # 重构草稿
old_implementations/             # 历史版本
```

### 2. "PATH控制优先级"
```bash
# 通过PATH顺序控制使用哪个版本
PATH=/usr/local/bin:/usr/bin:/bin

# 通过knowledge_dirs顺序控制优先级
knowledge_dirs = [
    "knowledge",        # 优先级最高
    "knowledge/minimal",
    "knowledge/core"
]
```

### 3. "工具共存"
- 不同版本可以同时存在
- 不会互相干扰
- 可以通过绝对路径显式调用特定版本

### 4. "向后兼容"
- 旧文件的存在不影响新功能
- 如果需要可以回退到旧版本
- 历史代码依然可以参考旧文档

## 优势

### 1. 避免破坏性修改
- 不需要删除旧文件
- 可以安全地实验新版本
- 出问题可以快速回退

### 2. 历史可追溯
- 保留所有历史版本
- 可以看到知识演化过程
- 便于理解设计决策

### 3. 兼容性友好
- 旧的引用不会失效
- 渐进式升级
- 降低风险

### 4. 灵活性
- 可以通过调整扫描顺序改变优先级
- 可以临时使用旧版本（通过显式路径）
- 支持A/B测试（多版本对比）

## 与Java CLASSPATH的对比

### Java CLASSPATH
```java
// 多个版本的类可以共存
lib/mylib-1.0.jar     # 旧版本
lib/mylib-2.0.jar     # 新版本

// CLASSPATH决定使用哪个
CLASSPATH=lib/mylib-2.0.jar:lib/mylib-1.0.jar
// → 使用2.0版本
```

### 知识函数PATH
```python
# 多个版本的知识文件可以共存
knowledge/self_awareness.md      # 新版本
knowledge/self_awareness_old.md  # 旧版本（如果存在）

# knowledge_dirs决定使用哪个
knowledge_dirs = ["knowledge", "archive"]
# → 使用 knowledge/self_awareness.md（先扫描到）
```

## 最佳实践

### 1. 新版本覆盖旧版本
将新版本放在优先级高的目录：
```
knowledge/new_function.md        # 新版本（优先）
archive/old_function.md          # 旧版本（保留）
```

### 2. 草稿版本可以共存
```
self_awareness.md                # 正式版本
self_awareness_draft.md          # 草稿版本
KNOWLEDGE_FUNCTION_REFACTOR.md   # 重构实验
```
优先级机制确保使用正式版本，草稿不影响生产。

### 3. 显式控制优先级
通过调整knowledge_dirs顺序：
```python
# 测试新版本
knowledge_dirs = ["knowledge/experimental", "knowledge"]

# 生产环境
knowledge_dirs = ["knowledge", "knowledge/experimental"]
```

## 总结

**不要清理，要管理优先级**

- ✅ 保留历史版本（向Unix学习）
- ✅ PATH机制控制使用哪个版本（向Unix学习）
- ✅ 版本冲突时警告但不中断（向Java学习）
- ✅ 支持partial定义（向C#学习）

**核心价值观**：
- 历史是财富，不是垃圾
- 版本共存，通过优先级管理
- 警告提示，不强制清理
- Unix哲学：简单、灵活、强大