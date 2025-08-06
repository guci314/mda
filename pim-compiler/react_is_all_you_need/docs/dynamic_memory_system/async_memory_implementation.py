#!/usr/bin/env python3
"""异步动态记忆系统实现示例

展示如何实现真正的异步记忆更新，包括主进程通知机制。
"""

import asyncio
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class UpdateType(Enum):
    """更新类型"""
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    ENVIRONMENT_LEARNING = "environment_learning"
    ERROR_CORRECTION = "error_correction"
    PATTERN_DISCOVERED = "pattern_discovered"


@dataclass
class MemoryUpdate:
    """记忆更新数据结构"""
    type: UpdateType
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    source: str = "async_extraction"
    confidence: float = 1.0
    version: int = 1


class AsyncMemoryChannel:
    """异步记忆通信通道"""
    
    def __init__(self, capacity: int = 100):
        # 线程安全的队列
        self.updates_queue = queue.Queue(maxsize=capacity)
        self.subscribers: List[Callable] = []
        self.is_running = True
        
        # 启动消息分发线程
        self.dispatcher_thread = threading.Thread(
            target=self._dispatch_updates,
            daemon=True,
            name="memory_dispatcher"
        )
        self.dispatcher_thread.start()
    
    def publish(self, update: MemoryUpdate):
        """发布更新（非阻塞）"""
        try:
            self.updates_queue.put_nowait(update)
        except queue.Full:
            logger.warning("记忆更新队列已满，丢弃最旧的更新")
            # 移除最旧的更新
            try:
                self.updates_queue.get_nowait()
                self.updates_queue.put_nowait(update)
            except:
                pass
    
    def subscribe(self, callback: Callable[[MemoryUpdate], None]):
        """订阅更新通知"""
        self.subscribers.append(callback)
        
    def _dispatch_updates(self):
        """分发更新给所有订阅者"""
        while self.is_running:
            try:
                update = self.updates_queue.get(timeout=1)
                
                # 通知所有订阅者
                for subscriber in self.subscribers:
                    try:
                        subscriber(update)
                    except Exception as e:
                        logger.error(f"订阅者处理更新失败: {e}")
                        
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"分发更新时出错: {e}")
    
    def shutdown(self):
        """关闭通道"""
        self.is_running = False
        self.dispatcher_thread.join(timeout=5)


class AsyncMemoryExtractor:
    """异步记忆提取器"""
    
    def __init__(self, channel: AsyncMemoryChannel, llm_func: Callable):
        self.channel = channel
        self.llm_func = llm_func
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def extract_knowledge_async(self, messages: List[Any], context: Dict[str, Any]):
        """异步提取知识"""
        # 提交到线程池
        future = self.executor.submit(
            self._extract_knowledge_worker,
            messages,
            context
        )
        
        # 设置完成回调
        future.add_done_callback(self._on_extraction_complete)
        
        return future
    
    def _extract_knowledge_worker(self, messages: List[Any], context: Dict[str, Any]) -> str:
        """在工作线程中提取知识"""
        try:
            # 构建提取提示词
            prompt = self._build_extraction_prompt(messages, context)
            
            # 调用 LLM
            knowledge = self.llm_func(prompt)
            
            return knowledge
            
        except Exception as e:
            logger.error(f"知识提取失败: {e}")
            raise
    
    def _on_extraction_complete(self, future):
        """提取完成的回调"""
        try:
            knowledge = future.result()
            
            # 创建更新消息
            update = MemoryUpdate(
                type=UpdateType.KNOWLEDGE_EXTRACTION,
                content=knowledge,
                metadata={
                    'extraction_time': time.time(),
                    'success': True
                },
                timestamp=datetime.now()
            )
            
            # 发布更新
            self.channel.publish(update)
            
        except Exception as e:
            # 发布错误更新
            error_update = MemoryUpdate(
                type=UpdateType.ERROR_CORRECTION,
                content=f"知识提取失败: {str(e)}",
                metadata={
                    'error': str(e),
                    'success': False
                },
                timestamp=datetime.now(),
                confidence=0.0
            )
            self.channel.publish(error_update)
    
    def _build_extraction_prompt(self, messages: List[Any], context: Dict[str, Any]) -> str:
        """构建提取提示词"""
        return f"""
基于以下对话历史，提取关键知识和经验：

对话历史：
{self._format_messages(messages)}

上下文信息：
{json.dumps(context, ensure_ascii=False, indent=2)}

请提取：
1. 学到的新知识
2. 发现的模式
3. 需要记住的重要信息
"""
    
    def _format_messages(self, messages: List[Any]) -> str:
        """格式化消息历史"""
        formatted = []
        for msg in messages[-10:]:  # 只取最近10条
            if hasattr(msg, 'content'):
                formatted.append(f"- {msg.content[:200]}...")
        return "\n".join(formatted)


class MessageHistoryUpdater:
    """消息历史更新器 - 处理异步更新如何反映到主进程"""
    
    def __init__(self, agent):
        self.agent = agent
        self.pending_updates: List[MemoryUpdate] = []
        self.update_lock = threading.Lock()
        
    def on_memory_update(self, update: MemoryUpdate):
        """处理记忆更新"""
        with self.update_lock:
            self.pending_updates.append(update)
            
        # 根据更新类型决定处理方式
        if update.type == UpdateType.KNOWLEDGE_EXTRACTION:
            self._handle_knowledge_update(update)
        elif update.type == UpdateType.ENVIRONMENT_LEARNING:
            self._handle_environment_update(update)
        elif update.type == UpdateType.ERROR_CORRECTION:
            self._handle_error_correction(update)
            
    def _handle_knowledge_update(self, update: MemoryUpdate):
        """处理知识更新"""
        # 策略1：注入系统消息（立即可见）
        if self.agent.config.immediate_update_injection:
            self._inject_system_message(
                f"💡 新认知：{update.content[:100]}...",
                metadata={'update_id': id(update)}
            )
            
        # 策略2：更新上下文缓存（下次使用时生效）
        if hasattr(self.agent, 'knowledge_cache'):
            self.agent.knowledge_cache.append(update.content)
            
        # 策略3：触发 UI 更新（如果有 UI）
        if hasattr(self.agent, 'ui_callback'):
            self.agent.ui_callback('knowledge_updated', update)
            
    def _handle_environment_update(self, update: MemoryUpdate):
        """处理环境学习更新"""
        # 更新环境认知
        if hasattr(self.agent, 'env_cognition'):
            self.agent.env_cognition.apply_async_update(update)
            
    def _handle_error_correction(self, update: MemoryUpdate):
        """处理错误纠正"""
        error_msg_id = update.metadata.get('error_message_id')
        if error_msg_id and hasattr(self.agent.memory, 'correct_message'):
            # 标记之前的消息为已纠正
            self.agent.memory.correct_message(
                error_msg_id,
                correction=update.content
            )
            
    def _inject_system_message(self, content: str, metadata: Dict = None):
        """注入系统消息到对话历史"""
        try:
            # 创建系统消息
            from langchain_core.messages import SystemMessage
            
            system_msg = SystemMessage(
                content=content,
                additional_kwargs={
                    'injected': True,
                    'timestamp': datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            
            # 线程安全地添加到记忆
            if hasattr(self.agent, 'memory') and self.agent.memory:
                with self.agent._message_lock:
                    self.agent.memory.chat_memory.add_message(system_msg)
                    
                # 可选：在控制台显示
                if self.agent.config.show_memory_updates:
                    print(f"\n{content}\n")
                    
        except Exception as e:
            logger.error(f"注入系统消息失败: {e}")
            
    def get_pending_updates_summary(self) -> Optional[str]:
        """获取待处理更新的摘要"""
        with self.update_lock:
            if not self.pending_updates:
                return None
                
            summary_parts = []
            for update in self.pending_updates[-3:]:  # 最近3个更新
                if update.type == UpdateType.KNOWLEDGE_EXTRACTION:
                    summary_parts.append(f"- 新知识：{update.content[:50]}...")
                elif update.type == UpdateType.PATTERN_DISCOVERED:
                    summary_parts.append(f"- 发现模式：{update.content[:50]}...")
                    
            # 清空已处理的更新
            self.pending_updates.clear()
            
            if summary_parts:
                return "最近的认知更新：\n" + "\n".join(summary_parts)
                
        return None


class EnhancedReactAgent:
    """支持异步记忆更新的增强 Agent"""
    
    def __init__(self, config):
        self.config = config
        self._message_lock = threading.Lock()
        
        # 初始化异步记忆系统
        self.memory_channel = AsyncMemoryChannel()
        self.memory_extractor = AsyncMemoryExtractor(
            self.memory_channel,
            self._llm_extract_knowledge
        )
        self.history_updater = MessageHistoryUpdater(self)
        
        # 订阅记忆更新
        self.memory_channel.subscribe(self.history_updater.on_memory_update)
        
        # 知识缓存
        self.knowledge_cache = []
        
    def execute_task(self, task: str) -> str:
        """执行任务（支持异步记忆更新）"""
        # ... 执行任务的主逻辑 ...
        
        result = self._execute_main_task(task)
        
        # 异步提取知识
        self.memory_extractor.extract_knowledge_async(
            self.get_message_history(),
            {'task': task, 'result': result}
        )
        
        return result
        
    def _llm_extract_knowledge(self, prompt: str) -> str:
        """调用 LLM 提取知识"""
        # 这里是实际的 LLM 调用
        # return self.llm.invoke(prompt).content
        return f"模拟提取的知识：{prompt[:50]}..."
        
    def enhance_prompt_with_updates(self, original_prompt: str) -> str:
        """用最新的记忆更新增强提示词"""
        updates_summary = self.history_updater.get_pending_updates_summary()
        
        if updates_summary:
            return f"{original_prompt}\n\n{updates_summary}"
            
        return original_prompt
        
    def shutdown(self):
        """优雅关闭"""
        self.memory_channel.shutdown()
        self.memory_extractor.executor.shutdown(wait=True)


# 使用示例
def demo_async_memory():
    """演示异步记忆系统"""
    
    class Config:
        immediate_update_injection = True
        show_memory_updates = True
        
    # 创建 Agent
    agent = EnhancedReactAgent(Config())
    
    # 模拟任务执行
    print("执行任务：分析代码库")
    result = agent.execute_task("分析代码库结构")
    
    # 等待异步更新
    print("\n等待异步记忆更新...")
    time.sleep(2)
    
    # 执行下一个任务（会包含之前的更新）
    print("\n执行任务：生成文档")
    enhanced_prompt = agent.enhance_prompt_with_updates("生成项目文档")
    print(f"增强后的提示词：\n{enhanced_prompt}")
    
    # 关闭
    agent.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_async_memory()