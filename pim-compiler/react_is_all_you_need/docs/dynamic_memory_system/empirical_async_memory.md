# 经验主义的异步记忆系统

## 核心理念

**不要预先设计，要在使用中演化。**

就像美国法律系统：
- 宪法很简短，只定义基本框架
- 通过判例逐步明确细节
- 在冲突中发现问题
- 通过修正案适应变化

## 最简实现（MVP）

### v0.1 - 最朴素的异步记忆

```python
class SimpleAsyncMemory:
    """最简单的异步记忆 - 先跑起来再说"""
    
    def __init__(self, agent):
        self.agent = agent
        self.updates = []  # 就是个列表，没那么多花样
        
    def extract_async(self, messages):
        """异步提取 - 就是开个线程"""
        def worker():
            try:
                # 提取知识
                knowledge = self.agent.llm.extract(messages)
                # 存起来
                self.updates.append(knowledge)
                # 打印出来让用户知道
                print(f"\n💭 学到了：{knowledge[:50]}...\n")
            except:
                pass  # 失败就失败了，下次再说
                
        Thread(target=worker).start()
```

**就这么简单！**

## 实际使用中发现的问题

### 问题1：更新太频繁，刷屏了
```python
# 用户反馈："能不能别一直打印？"
# 修正：加个开关
if self.agent.config.show_updates:  # 加的第一个配置
    print(f"\n💭 {knowledge[:50]}...\n")
```

### 问题2：重要的更新被淹没了
```python
# 用户反馈："错误修正应该更明显"
# 修正：简单分类
if "错误" in knowledge or "修正" in knowledge:
    print(f"\n🚨 重要：{knowledge}\n")  # 红色警告
else:
    print(f"\n💭 {knowledge[:50]}...\n")  # 普通学习
```

### 问题3：想要关掉但又想知道学了什么
```python
# 用户反馈："能不能最后告诉我学了什么？"
# 修正：添加总结
def summarize_learning(self):
    if self.updates:
        print(f"\n📚 本次对话学到了 {len(self.updates)} 条新知识")
        for i, update in enumerate(self.updates[-3:], 1):
            print(f"  {i}. {update[:60]}...")
```

## 演化历程

### v0.2 - 基于反馈的第一次改进
```python
class AsyncMemoryV2:
    def __init__(self, agent):
        self.agent = agent
        self.updates = []
        self.errors_found = []  # 分开存错误
        
    def extract_async(self, messages):
        Thread(target=self._worker, args=(messages,)).start()
        
    def _worker(self, messages):
        try:
            knowledge = self.agent.llm.extract(messages)
            
            # 简单分类（基于实际使用经验）
            if self._looks_like_error(knowledge):
                self.errors_found.append(knowledge)
                if self.agent.config.show_errors:  # 错误默认显示
                    print(f"\n🚨 {knowledge}\n")
            else:
                self.updates.append(knowledge)
                # 普通更新默认不显示了（太吵）
                
        except Exception as e:
            # 记录失败，但不阻塞
            self.agent.debug_log(f"提取失败: {e}")
```

### v0.3 - 解决实际痛点
```python
# 用户反馈："异步更新完成后，下个问题能用上吗？"
# 实际问题：异步更新无法影响当前对话

class AsyncMemoryV3:
    def __init__(self, agent):
        self.agent = agent
        self.pending = []  # 待处理的更新
        self.applied = []  # 已应用的更新
        
    def check_pending_updates(self):
        """在生成回复前检查有无新更新"""
        if self.pending:
            # 发现的简单策略：直接加到系统提示里
            new_knowledge = "\n".join(self.pending)
            self.agent.system_prompt += f"\n\n最新认知：\n{new_knowledge}"
            
            self.applied.extend(self.pending)
            self.pending.clear()
```

## 经验总结

### 1. 不要预设使用方式
- ❌ "用户可能需要三种更新策略"
- ✅ "先打印出来，看看用户怎么说"

### 2. 从最简单的开始
- ❌ 发布-订阅模式、消息队列、优先级
- ✅ 一个列表 + 一个线程

### 3. 基于实际反馈改进
- 用户说太吵 → 加开关
- 用户说看不到重要信息 → 简单分类
- 用户说想要总结 → 加总结

### 4. 接受不完美
- 线程可能失败 → 没关系，记个日志
- 分类可能不准 → 没关系，用户会告诉我们
- 更新可能冲突 → 没关系，最新的覆盖旧的

## 当前版本（基于6个月使用经验）

```python
class EmpiricalAsyncMemory:
    """经验主义的异步记忆 - 每一行都是血泪史"""
    
    def __init__(self, agent):
        self.agent = agent
        self.updates = []
        
        # 这些配置都是用户要求加的
        self.show_errors = True      # 错误必须显示（教训）
        self.show_learning = False   # 学习过程太吵（经验）
        self.batch_summary = True    # 最后总结挺有用（反馈）
        
    def extract_async(self, messages):
        """保持简单，能用就行"""
        def worker():
            try:
                knowledge = self._extract(messages)
                self._handle_update(knowledge)
            except Exception as e:
                # 早期崩溃太多次，现在都是静默失败
                self.agent.log_error(e)
                
        # 不要守护线程，让它跑完（踩过的坑）
        Thread(target=worker, daemon=False).start()
        
    def _handle_update(self, knowledge):
        """处理方式都是用出来的"""
        self.updates.append(knowledge)
        
        # 规则1：包含"错误"、"修正"、"实际上"的要立即显示
        # （来自一次严重的bug，用户基于错误信息操作了半小时）
        if any(word in knowledge for word in ["错误", "修正", "实际上"]):
            print(f"\n🚨 {knowledge}\n")
            
        # 规则2：用户明确要求看学习过程
        elif self.agent.user_preferences.get("verbose_learning"):
            print(f"\n💭 {knowledge[:80]}...\n")
            
        # 规则3：其他的都静默处理，最后总结
        # （这是最受欢迎的模式）
    
    def apply_to_next_turn(self):
        """下一轮对话时应用更新"""
        if not self.updates:
            return
            
        # 最简单有效的方法：直接告诉 LLM
        summary = f"基于之前的对话，我学到了：\n"
        summary += "\n".join(f"- {u}" for u in self.updates[-5:])
        
        # 注入到下一个 prompt
        return summary
```

## 未来演化方向

不是计划，而是预测可能的需求：

1. **如果用户抱怨更新太慢**
   → 可能会加个"紧急"标记

2. **如果用户想要撤销某个学习**
   → 可能会加个简单的撤销功能

3. **如果多个用户协作使用**
   → 可能需要处理并发更新

但是现在？**够用就好。**

## 核心洞察

经验主义的系统设计：
- 📝 每个功能都有故事
- 🔧 每行代码都解决过实际问题  
- 🎯 没有"以防万一"的代码
- ✅ 接受"够用就好"

就像判例法：
- 遇到新案例（新问题）
- 做出判决（简单解决）
- 成为先例（代码模式）
- 后续改进（修正案）

**这就是真正的敏捷。**