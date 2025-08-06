#!/usr/bin/env python3
"""
MVP 异步记忆 - 真正的最小可行版本

设计原则：
1. 能跑就行
2. 有问题再改
3. 用户驱动演化
"""

from threading import Thread
import time


class MVPAsyncMemory:
    """v0.0.1 - 最最简单的异步记忆"""
    
    def __init__(self, agent):
        self.agent = agent
        self.learnings = []  # 就一个列表
        
    def learn_async(self, task_result):
        """开个线程学习，完事儿"""
        def learn():
            # 假装在学习（实际调用 LLM）
            time.sleep(1)
            learning = f"从'{task_result[:30]}...'学到了一些东西"
            self.learnings.append(learning)
            print(f"\n💡 {learning}\n")
            
        Thread(target=learn).start()


# 实际使用第一天就会遇到的问题
class MVPAsyncMemoryV2:
    """v0.0.2 - 用户说太吵了"""
    
    def __init__(self, agent):
        self.agent = agent  
        self.learnings = []
        self.quiet = True  # 默认安静（基于投诉）
        
    def learn_async(self, task_result):
        def learn():
            learning = f"从任务中学到：{task_result[:50]}..."
            self.learnings.append(learning)
            
            if not self.quiet:  # 加了个开关
                print(f"\n💡 {learning}\n")
                
        Thread(target=learn).start()


# 一周后的版本
class MVPAsyncMemoryWeek1:
    """v0.1.0 - 基于一周的实际使用"""
    
    def __init__(self, agent):
        self.agent = agent
        self.learnings = []
        self.errors_corrected = []  # 用户要求：错误要特别处理
        
    def learn_async(self, task_result, task_type="normal"):
        def learn():
            try:
                # 真实的提取逻辑（之前是假的）
                learning = self.agent.extract_knowledge(task_result)
                
                # 基于实际使用发现的分类需求
                if "错误" in learning or task_type == "error":
                    self.errors_corrected.append(learning)
                    print(f"\n🔴 纠正：{learning}\n")  # 错误必须显示
                else:
                    self.learnings.append(learning)
                    # 普通学习不显示（太多人投诉）
                    
            except:
                # 静默失败（崩溃太多次了）
                pass
                
        Thread(target=learn).start()
        
    def get_summary(self):
        """用户要的功能：看看学了啥"""
        if not self.learnings and not self.errors_corrected:
            return "本次对话没有新的学习"
            
        summary = []
        if self.errors_corrected:
            summary.append(f"纠正了 {len(self.errors_corrected)} 个错误")
        if self.learnings:
            summary.append(f"学到了 {len(self.learnings)} 条新知识")
            
        return " | ".join(summary)


# 一个月后的版本（当前稳定版）
class StableAsyncMemory:
    """v1.0.0 - 经过实战检验的版本"""
    
    def __init__(self, agent):
        self.agent = agent
        self.updates = []
        
        # 这些默认值都是血泪教训
        self.show_errors = True      # 必须的，出过大事
        self.show_learning = False   # 默认关，太吵
        self.show_summary = True     # 大家都喜欢
        self.max_summary_items = 3   # 超过3条没人看
        
    def extract_async(self, context):
        """主方法 - 保持简单"""
        Thread(
            target=self._extract_worker,
            args=(context,),
            daemon=False  # 不能是守护线程，会丢失更新
        ).start()
        
    def _extract_worker(self, context):
        """工作线程 - 所有复杂逻辑都在这里"""
        try:
            # 提取
            result = self.agent.llm_extract(context)
            
            # 存储
            self.updates.append({
                'content': result,
                'time': time.time(),
                'type': self._classify(result)  # 简单分类
            })
            
            # 显示（基于类型）
            if self._should_show(result):
                self._display(result)
                
        except Exception as e:
            # 记录但不崩溃
            if hasattr(self.agent, 'logger'):
                self.agent.logger.error(f"异步提取失败: {e}")
                
    def _classify(self, content):
        """简单粗暴的分类"""
        content_lower = content.lower()
        if any(word in content_lower for word in ['错误', 'error', '修正', 'fix']):
            return 'error'
        elif any(word in content_lower for word in ['模式', 'pattern', '发现']):
            return 'insight'
        else:
            return 'knowledge'
            
    def _should_show(self, content):
        """是否显示 - 基于经验的规则"""
        update_type = self._classify(content)
        
        if update_type == 'error':
            return self.show_errors  # 错误通常要显示
        else:
            return self.show_learning  # 其他的看配置
            
    def _display(self, content):
        """显示更新 - 用户体验优化"""
        update_type = self._classify(content)
        
        # 不同类型不同颜色（用户反馈）
        icons = {
            'error': '🚨',
            'insight': '💡', 
            'knowledge': '📝'
        }
        
        icon = icons.get(update_type, '💭')
        
        # 限制长度（没人想看长文本）
        display_content = content[:100] + '...' if len(content) > 100 else content
        
        print(f"\n{icon} {display_content}\n")
        
    def apply_updates(self, prompt):
        """应用更新到下一轮对话"""
        if not self.updates:
            return prompt
            
        # 最简单有效的方法
        recent = self.updates[-3:]  # 只用最近的
        update_text = "\n".join([
            f"- {u['content'][:80]}..." 
            for u in recent
        ])
        
        # 直接加到 prompt 里
        return f"{prompt}\n\n[最近的学习]\n{update_text}"
        
    def show_summary(self):
        """显示总结 - 最受欢迎的功能"""
        if not self.updates:
            return
            
        print("\n" + "="*50)
        print(f"📚 本次对话的学习总结（共 {len(self.updates)} 项）")
        print("="*50)
        
        # 按类型分组
        by_type = {}
        for u in self.updates:
            type_name = u['type']
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append(u)
            
        # 显示每种类型
        for type_name, items in by_type.items():
            print(f"\n{type_name.title()} ({len(items)}项):")
            for item in items[:self.max_summary_items]:
                print(f"  • {item['content'][:60]}...")
                
        print("\n" + "="*50 + "\n")


# ===== 使用示例 =====

if __name__ == "__main__":
    # 模拟 Agent
    class MockAgent:
        def extract_knowledge(self, text):
            return f"学到了关于'{text[:20]}'的知识"
            
        def llm_extract(self, context):
            import random
            types = [
                "发现了代码中的错误：变量名拼写错误",
                "学到了新的设计模式：单例模式", 
                "理解了项目结构：MVC架构"
            ]
            return random.choice(types)
    
    agent = MockAgent()
    memory = StableAsyncMemory(agent)
    
    # 模拟使用
    print("=== 异步记忆系统演示 ===\n")
    
    # 执行任务
    memory.extract_async("分析代码库结构")
    time.sleep(0.5)
    
    memory.extract_async("发现了一个 bug")
    time.sleep(0.5)
    
    memory.extract_async("学习设计模式")
    time.sleep(0.5)
    
    # 显示总结
    memory.show_summary()
    
    # 应用到下一轮
    new_prompt = memory.apply_updates("请继续分析")
    print(f"增强后的提示词：\n{new_prompt}")


"""
演化历史：

v0.0.1 (第1天)
- 就一个线程 + 一个列表
- 问题：太吵，刷屏

v0.0.2 (第2天)  
- 加了个 quiet 开关
- 问题：错误信息也被静音了

v0.1.0 (第1周)
- 分离错误和普通学习
- 加了 get_summary()
- 问题：还是有点吵

v0.2.0 (第2周)
- 默认静音，只显示错误
- 优化了显示格式
- 问题：如何应用到下一轮对话

v0.3.0 (第3周)
- 加了 apply_updates()
- 限制了显示长度
- 问题：分类太粗糙

v1.0.0 (第1个月)
- 稳定版本
- 简单但有效的分类
- 用户满意的默认值
- 受欢迎的总结功能

未来可能的演化（基于用户反馈）：
- 如果有人要求持久化 -> 加个保存到文件
- 如果有人要求过滤 -> 加个简单的过滤器
- 如果有人要求优先级 -> 加个 important 标记

但是现在？它工作得很好。
"""