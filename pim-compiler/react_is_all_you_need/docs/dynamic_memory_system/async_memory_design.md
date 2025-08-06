# 异步动态记忆系统设计

## 现状分析

当前系统已经实现了基础的异步知识提取：
- 使用 `threading.Thread` 在后台提取知识
- 非守护线程确保任务完成
- 程序退出时等待所有线程完成

### 现有问题
1. **单向通信**：知识提取完成后无法通知主进程
2. **无法更新消息历史**：提取的知识不能反馈到当前对话
3. **缺乏实时性**：必须等到下次初始化才能使用新知识
4. **错误处理简单**：异步任务失败时主进程无感知

## 改进方案：真正的异步动态记忆

### 核心架构

```python
import asyncio
from asyncio import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum


class MemoryUpdateType(Enum):
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    ENVIRONMENT_COGNITION = "environment_cognition"
    PATTERN_RECOGNITION = "pattern_recognition"
    ERROR_CORRECTION = "error_correction"


@dataclass
class MemoryUpdate:
    """记忆更新消息"""
    type: MemoryUpdateType
    content: str
    metadata: dict
    timestamp: datetime
    confidence: float = 1.0
    
    
class AsyncMemorySystem:
    """异步动态记忆系统"""
    
    def __init__(self, agent_name: str, callback: Optional[Callable] = None):
        self.agent_name = agent_name
        self.update_callback = callback  # 主进程回调
        
        # 异步通信队列
        self.update_queue = Queue()
        self.pending_updates = []
        
        # 线程池用于 CPU 密集型任务
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # 启动异步事件循环
        self.loop = asyncio.new_event_loop()
        self.loop_thread = Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        
    def _run_event_loop(self):
        """在独立线程中运行事件循环"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._process_updates())
        
    async def _process_updates(self):
        """持续处理记忆更新"""
        while True:
            try:
                update = await self.update_queue.get()
                await self._handle_update(update)
            except Exception as e:
                logger.error(f"处理更新时出错: {e}")
                
    async def _handle_update(self, update: MemoryUpdate):
        """处理单个更新"""
        # 1. 持久化更新
        await self._persist_update(update)
        
        # 2. 通知主进程（如果有回调）
        if self.update_callback:
            try:
                self.update_callback(update)
            except Exception as e:
                logger.error(f"回调执行失败: {e}")
                
    def extract_knowledge_async(self, messages: List[BaseMessage]):
        """异步提取知识"""
        asyncio.run_coroutine_threadsafe(
            self._extract_knowledge(messages),
            self.loop
        )
        
    async def _extract_knowledge(self, messages: List[BaseMessage]):
        """知识提取的异步实现"""
        # 在线程池中执行 CPU 密集型任务
        knowledge = await self.loop.run_in_executor(
            self.executor,
            self._extract_knowledge_sync,
            messages
        )
        
        # 创建更新消息
        update = MemoryUpdate(
            type=MemoryUpdateType.KNOWLEDGE_EXTRACTION,
            content=knowledge,
            metadata={
                'message_count': len(messages),
                'extraction_method': 'llm_summary'
            },
            timestamp=datetime.now()
        )
        
        # 放入更新队列
        await self.update_queue.put(update)
```

### 主进程集成

```python
class EnhancedGenericReactAgent:
    """增强的 Agent，支持异步记忆更新通知"""
    
    def __init__(self, config, name=None):
        # ... 原有初始化 ...
        
        # 初始化异步记忆系统
        self.async_memory = AsyncMemorySystem(
            agent_name=self.name,
            callback=self._on_memory_update
        )
        
        # 消息历史的线程安全更新
        self._message_lock = threading.Lock()
        
    def _on_memory_update(self, update: MemoryUpdate):
        """处理异步记忆更新的回调"""
        if update.type == MemoryUpdateType.KNOWLEDGE_EXTRACTION:
            # 选项1：添加系统消息到历史
            self._inject_system_message(
                f"[记忆更新] 已提取新知识：{update.content[:100]}..."
            )
            
            # 选项2：更新内部状态
            self._refresh_knowledge_cache()
            
        elif update.type == MemoryUpdateType.ERROR_CORRECTION:
            # 纠正之前的错误信息
            self._correct_previous_message(update.metadata['error_id'])
            
    def _inject_system_message(self, content: str):
        """线程安全地注入系统消息"""
        with self._message_lock:
            system_msg = SystemMessage(
                content=content,
                metadata={
                    'injected': True,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # 根据记忆类型决定注入方式
            if self.memory and hasattr(self.memory, 'chat_memory'):
                # 添加到记忆中（会在下次交互时可见）
                self.memory.chat_memory.add_message(system_msg)
            
            # 可选：立即在界面显示
            if self.config.show_memory_updates:
                print(f"\n💭 {content}\n")
```

### 实时更新策略

#### 策略1：系统消息注入
```python
def _on_knowledge_extracted(self, knowledge: str):
    """知识提取完成时的处理"""
    # 创建一个特殊的系统消息
    update_msg = SystemMessage(
        content="我刚刚总结了一些新的认知，这将帮助我更好地理解后续任务。",
        metadata={
            'type': 'knowledge_update',
            'summary': knowledge[:200]
        }
    )
    
    # 注入到对话历史
    self.memory.chat_memory.add_message(update_msg)
```

#### 策略2：上下文增强
```python
def _enhance_context_with_updates(self, original_context: str) -> str:
    """用最新的记忆更新增强上下文"""
    if not self.pending_memory_updates:
        return original_context
        
    updates_summary = self._summarize_updates(self.pending_memory_updates)
    
    enhanced = f"""
{original_context}

## 最近的认知更新
{updates_summary}
"""
    
    # 清空已处理的更新
    self.pending_memory_updates.clear()
    
    return enhanced
```

#### 策略3：动态知识注入
```python
class DynamicKnowledgeInjector:
    """动态知识注入器"""
    
    def __init__(self, agent):
        self.agent = agent
        self.injection_points = {
            'before_tool_call': self._inject_before_tool,
            'after_tool_call': self._inject_after_tool,
            'on_error': self._inject_on_error
        }
        
    def _inject_before_tool(self, tool_name: str, args: dict):
        """在工具调用前注入相关知识"""
        relevant_knowledge = self.agent.async_memory.get_relevant_knowledge(
            context=f"tool:{tool_name}",
            args=args
        )
        
        if relevant_knowledge:
            # 添加到工具调用的上下文中
            return {
                **args,
                '_knowledge_context': relevant_knowledge
            }
        return args
```

### 并发控制和一致性

```python
class MemoryConsistencyManager:
    """记忆一致性管理器"""
    
    def __init__(self):
        self.version = 0
        self.update_log = []
        self.conflict_resolver = ConflictResolver()
        
    def apply_update(self, update: MemoryUpdate) -> bool:
        """应用更新并处理冲突"""
        with self.update_lock:
            # 检查更新是否与现有知识冲突
            conflicts = self.detect_conflicts(update)
            
            if conflicts:
                # 解决冲突
                resolved = self.conflict_resolver.resolve(
                    update, 
                    conflicts,
                    strategy='newest_wins'  # 或 'highest_confidence'
                )
                
                if not resolved:
                    return False
                    
            # 应用更新
            self.version += 1
            self.update_log.append({
                'version': self.version,
                'update': update,
                'timestamp': datetime.now()
            })
            
            return True
```

### 优雅降级和错误处理

```python
class ResilientAsyncMemory:
    """弹性异步记忆系统"""
    
    def __init__(self):
        self.fallback_mode = False
        self.error_count = 0
        self.max_errors = 3
        
    async def update_memory(self, content: Any):
        """带降级的记忆更新"""
        try:
            if self.fallback_mode:
                # 降级模式：同步更新
                self._update_sync(content)
                return
                
            # 正常异步更新
            await self._update_async(content)
            
            # 成功后重置错误计数
            self.error_count = 0
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"异步更新失败 ({self.error_count}/{self.max_errors}): {e}")
            
            if self.error_count >= self.max_errors:
                # 切换到降级模式
                self.fallback_mode = True
                logger.warning("切换到同步记忆更新模式")
                
                # 同步更新
                self._update_sync(content)
```

## 实施建议

### 第一阶段：基础异步通知
1. 实现更新队列和回调机制
2. 在 Agent 中添加更新处理器
3. 支持简单的系统消息注入

### 第二阶段：智能更新集成
1. 实现上下文增强
2. 添加知识相关性检测
3. 支持动态知识注入

### 第三阶段：高级特性
1. 冲突检测和解决
2. 版本控制
3. 优雅降级

## 配置选项

```python
class AsyncMemoryConfig:
    # 是否显示记忆更新
    show_memory_updates: bool = True
    
    # 更新注入策略
    injection_strategy: str = "system_message"  # 或 "context_enhancement"
    
    # 并发配置
    max_concurrent_updates: int = 3
    update_timeout: int = 30  # 秒
    
    # 冲突解决策略
    conflict_resolution: str = "newest_wins"  # 或 "highest_confidence"
    
    # 降级配置
    enable_fallback: bool = True
    max_error_before_fallback: int = 3
```

## 使用示例

```python
# 创建支持异步更新通知的 Agent
config = ReactAgentConfig(
    async_memory=True,
    show_memory_updates=True,
    injection_strategy="system_message"
)

agent = EnhancedGenericReactAgent(config)

# 执行任务时，异步更新会实时反馈
agent.execute_task("分析这个代码库")

# 输出示例：
# > 正在分析代码库...
# > 发现 Python 项目，主要使用 FastAPI
# 
# 💭 [记忆更新] 已识别项目类型：FastAPI Web 服务
# 
# > 继续分析 API 结构...
# 
# 💭 [记忆更新] 发现的模式：RESTful API 设计，遵循 OpenAPI 规范
```

这种设计让动态记忆真正"活"起来，能够实时影响 Agent 的行为。