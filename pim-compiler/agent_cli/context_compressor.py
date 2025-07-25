"""
三层注意力上下文压缩器

使用任务、步骤计划和当前动作作为注意力机制，
智能压缩上下文以保持在 LLM 上下文窗口限制内。
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import SecretStr

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """步骤状态（与 core_v2_new.py 保持一致）"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FileContent:
    """文件内容记录"""
    content: str
    timestamp: float
    size: int
    path: str


class ThreeLayerContextCompressor:
    """三层注意力上下文压缩器
    
    三层注意力：
    1. 任务层：整体任务目标
    2. 步骤层：执行计划和进度
    3. 动作层：当前正在执行的具体动作
    """
    
    def __init__(
        self,
        llm_client,
        context_size_limit: int = 30 * 1024,  # 30KB
        recent_file_window: int = 3,  # 保护最近3个文件
        compression_ratio_target: float = 0.3  # 目标压缩到30%
    ):
        self.llm_client = llm_client
        self.context_size_limit = context_size_limit
        self.recent_file_window = recent_file_window
        self.compression_ratio_target = compression_ratio_target
        
    def should_compress(self, context: Dict[str, Any]) -> bool:
        """判断是否需要压缩上下文"""
        size = self._calculate_context_size(context)
        return size > self.context_size_limit
        
    def _calculate_context_size(self, context: Dict[str, Any]) -> int:
        """计算上下文大小（字节）"""
        # 将上下文序列化为 JSON 字符串来估算大小
        try:
            context_str = json.dumps(context, ensure_ascii=False)
            return len(context_str.encode('utf-8'))
        except Exception as e:
            logger.warning(f"Failed to calculate context size: {e}")
            return 0
            
    def compress_with_attention(
        self,
        context: Dict[str, Any],
        task: str,
        step_plan: List[Any],  # Step 对象列表
        current_step: Any,  # 当前 Step 对象
        current_action: str
    ) -> Dict[str, Any]:
        """使用三层注意力压缩上下文"""
        logger.info(f"Starting context compression. Current size: {self._calculate_context_size(context)} bytes")
        
        # 1. 分离可压缩和不可压缩的内容
        compressible, protected = self._separate_content(context)
        
        # 2. 如果没有可压缩内容，直接返回
        if not compressible:
            logger.info("No compressible content found")
            return context
            
        # 3. 构建压缩提示词
        compression_prompt = self._build_compression_prompt(
            compressible, task, step_plan, current_step, current_action
        )
        
        # 4. 调用 LLM 进行压缩
        try:
            compressed_content = self._invoke_llm_compression(compression_prompt)
            
            # 5. 合并压缩后的内容和受保护的内容
            new_context = self._merge_compressed_context(
                compressed_content, protected, context
            )
            
            new_size = self._calculate_context_size(new_context)
            logger.info(f"Compression completed. New size: {new_size} bytes")
            
            return new_context
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            # 压缩失败时返回原始上下文
            return context
            
    def _separate_content(self, context: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """分离可压缩和受保护的内容"""
        compressible = {}
        protected = {}
        
        # 处理文件内容
        if "file_contents" in context:
            file_contents = context["file_contents"]
            
            # 按时间戳排序，找出最近的文件
            sorted_files = sorted(
                file_contents.items(),
                key=lambda x: x[1].get("timestamp", 0),
                reverse=True
            )
            
            # 保护最近的文件
            for i, (path, content) in enumerate(sorted_files):
                if i < self.recent_file_window:
                    if "file_contents" not in protected:
                        protected["file_contents"] = {}
                    protected["file_contents"][path] = content
                else:
                    if "file_contents" not in compressible:
                        compressible["file_contents"] = {}
                    compressible["file_contents"][path] = content
                    
        # 其他内容都可以压缩
        for key, value in context.items():
            if key not in ["file_contents", "task", "created_files"]:
                compressible[key] = value
            elif key in ["task", "created_files"]:
                # 这些是关键信息，始终保护
                protected[key] = value
                
        return compressible, protected
        
    def _build_compression_prompt(
        self,
        compressible: Dict[str, Any],
        task: str,
        step_plan: List[Any],
        current_step: Any,
        current_action: str
    ) -> str:
        """构建压缩提示词"""
        # 格式化步骤计划
        steps_text = "\n".join([
            f"- {step.name}: {step.description} ({step.status.value})"
            for step in step_plan
        ])
        
        # 格式化可压缩内容
        content_text = json.dumps(compressible, ensure_ascii=False, indent=2)
        
        prompt = f"""请压缩以下上下文信息，保持最重要的内容。

【任务目标】
{task}

【执行计划】
{steps_text}

【当前位置】
- 当前步骤：{current_step.name}
- 当前动作：{current_action}

【压缩要求】
1. 保留与任务目标直接相关的核心信息
2. 考虑执行计划中所有步骤的需求，特别是：
   - 文件路径和名称
   - 关键配置信息
   - API 端点和参数
   - 重要的数据结构
3. 保留最近操作的结果和状态
4. 移除重复、冗余和过时的内容
5. 保持信息的逻辑完整性

【需要压缩的内容】
{content_text}

请返回压缩后的 JSON 格式内容，确保：
1. 保持原有的数据结构
2. 关键信息不丢失
3. 后续步骤仍能正常执行

直接返回 JSON，不要包含其他说明文字。"""
        
        return prompt
        
    def _invoke_llm_compression(self, prompt: str) -> Dict[str, Any]:
        """调用 LLM 进行压缩"""
        messages = [
            SystemMessage(content="你是一个专业的上下文压缩专家，擅长识别和保留关键信息。"),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm_client.invoke(messages)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # 尝试解析 JSON
        try:
            # 清理可能的 markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            compressed = json.loads(content.strip())
            return compressed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse compressed content as JSON: {e}")
            logger.debug(f"Raw response: {content}")
            # 返回空字典，让原始内容保留
            return {}
            
    def _merge_compressed_context(
        self,
        compressed: Dict[str, Any],
        protected: Dict[str, Any],
        original: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并压缩后的内容和受保护的内容"""
        # 从原始上下文开始，保持所有键
        new_context = original.copy()
        
        # 更新压缩的内容
        for key, value in compressed.items():
            if key == "file_contents" and key in new_context:
                # 特殊处理文件内容，只更新被压缩的部分
                new_context[key].update(value)
            else:
                new_context[key] = value
                
        # 确保受保护的内容不被覆盖
        for key, value in protected.items():
            new_context[key] = value
            
        # 添加压缩标记
        new_context["_compressed"] = True
        new_context["_compression_time"] = time.time()
        
        return new_context
        
    def get_compression_stats(self, original: Dict[str, Any], compressed: Dict[str, Any]) -> Dict[str, Any]:
        """获取压缩统计信息"""
        original_size = self._calculate_context_size(original)
        compressed_size = self._calculate_context_size(compressed)
        
        return {
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": compressed_size / original_size if original_size > 0 else 1.0,
            "space_saved": original_size - compressed_size,
            "space_saved_percentage": (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        }