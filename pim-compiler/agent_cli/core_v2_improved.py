"""
Agent CLI v2.0 - 改进版，集成文件缓存优化
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from .core import LLMConfig, ActionType
from .executors import LangChainToolExecutor
from .file_cache_optimizer import FileCacheOptimizer, integrate_cache_with_action_decider
from .path_validator import PathValidator, integrate_path_validator_with_executor
from .dependency_analyzer import DependencyAnalyzer, integrate_dependency_analyzer
from .decision_optimizer import DecisionOptimizer, DecisionContext, DecisionStrategy, create_quick_checker
from .file_content_manager import FileContentManager, MergeStrategy

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr

# 导入其他必要模块
try:
    from .context_compressor import ThreeLayerContextCompressor
    COMPRESSION_AVAILABLE = True
except ImportError:
    COMPRESSION_AVAILABLE = False

try:
    from .enhanced_logging import init_diagnostic_logger, get_diagnostic_logger
    DIAGNOSTIC_LOGGING_AVAILABLE = True
except ImportError:
    DIAGNOSTIC_LOGGING_AVAILABLE = False

logger = logging.getLogger(__name__)

# 复用原有的数据结构
from .core_v2_new import (
    StepStatus,
    Action,
    Step
)

# 使用改进的规划器
from .improved_planner import (
    IMPROVED_PLANNER_SYSTEM_PROMPT,
    IMPROVED_PLANNER_HUMAN_PROMPT,
    MilestoneBasedPlanner
)


class AgentCLI_V2_Improved:
    """改进版 Agent CLI - 集成文件缓存优化和路径验证"""
    
    def __init__(
        self,
        llm_config: LLMConfig,
        use_langchain_tools: bool = True,
        enable_dynamic_planning: bool = True,
        max_actions_per_step: int = 10,
        enable_context_compression: bool = True,
        context_size_limit: int = 30 * 1024,
        recent_file_window: int = 3,
        enable_diagnostic_logging: bool = True,
        diagnostic_log_file: str = "agent_cli_diagnostics.log",
        enable_file_cache: bool = True,  # 启用文件缓存优化
        file_cache_ttl: int = 3600,  # 文件缓存时效（秒）
        enable_path_validation: bool = True,  # 启用路径验证
        project_root: Optional[str] = None,  # 项目根目录
        enable_dependency_analysis: bool = True,  # 启用依赖分析
        enable_decision_optimization: bool = True,  # 启用决策优化
        decision_strategy: str = "smart",  # 决策策略: always, batch, smart, milestone
        enable_file_content_management: bool = True,  # 启用文件内容管理
        file_merge_strategy: str = "merge_smart"  # 文件合并策略
    ):
        # 初始化基本配置
        self.llm_config = llm_config
        self.use_langchain_tools = use_langchain_tools
        self.enable_dynamic_planning = enable_dynamic_planning
        self.max_actions_per_step = max_actions_per_step
        self.enable_context_compression = enable_context_compression and COMPRESSION_AVAILABLE
        self.context_size_limit = context_size_limit
        self.recent_file_window = recent_file_window
        self.enable_file_cache = enable_file_cache
        
        # 初始化 LLM 客户端
        if llm_config.provider == "openrouter":
            self.llm_client = ChatOpenAI(
                api_key=SecretStr(llm_config.api_key) if llm_config.api_key else None,
                base_url=llm_config.base_url,
                model=llm_config.model,
                temperature=llm_config.temperature,
                default_headers={
                    "HTTP-Referer": "https://github.com/pim-compiler",
                    "X-Title": "PIM Compiler Agent CLI"
                },
                max_tokens=1000
            )
        else:
            self.llm_client = ChatOpenAI(
                api_key=SecretStr(llm_config.api_key) if llm_config.api_key else None,
                base_url=llm_config.base_url,
                model=llm_config.model,
                temperature=llm_config.temperature,
                max_tokens=1000
            )
        self.output_parser = StrOutputParser()
        
        # 初始化执行器
        self.executor = LangChainToolExecutor()
        
        # 上下文
        self.context: Dict[str, Any] = {
            "file_contents": {}
        }
        
        # 初始化文件缓存优化器
        self.file_cache = None
        if self.enable_file_cache:
            self.file_cache = FileCacheOptimizer(cache_ttl=file_cache_ttl)
            logger.info(f"File cache optimizer enabled (TTL: {file_cache_ttl}s)")
            
        # 初始化路径验证器
        self.path_validator = None
        self.enable_path_validation = enable_path_validation
        if self.enable_path_validation:
            self.path_validator = PathValidator(project_root=project_root)
            # 集成到执行器
            integrate_path_validator_with_executor(
                self.executor, self.path_validator, self.context
            )
            logger.info(f"Path validator enabled (root: {project_root or 'CWD'})")
            
        # 初始化依赖分析器
        self.dependency_analyzer = None
        self.enable_dependency_analysis = enable_dependency_analysis
        if self.enable_dependency_analysis:
            self.dependency_analyzer = DependencyAnalyzer()
            logger.info("Dependency analyzer enabled")
            
        # 初始化决策优化器
        self.decision_optimizer = None
        self.enable_decision_optimization = enable_decision_optimization
        if self.enable_decision_optimization:
            strategy_map = {
                "always": DecisionStrategy.ALWAYS,
                "batch": DecisionStrategy.BATCH,
                "smart": DecisionStrategy.SMART,
                "milestone": DecisionStrategy.MILESTONE
            }
            strategy = strategy_map.get(decision_strategy, DecisionStrategy.SMART)
            self.decision_optimizer = DecisionOptimizer(strategy=strategy)
            logger.info(f"Decision optimizer enabled (strategy: {strategy.value})")
            
        # 初始化文件内容管理器
        self.file_content_manager = None
        self.enable_file_content_management = enable_file_content_management
        if self.enable_file_content_management:
            merge_strategy_map = {
                "overwrite": MergeStrategy.OVERWRITE,
                "append": MergeStrategy.APPEND,
                "merge_smart": MergeStrategy.MERGE_SMART,
                "warn_skip": MergeStrategy.WARN_SKIP
            }
            merge_strategy = merge_strategy_map.get(file_merge_strategy, MergeStrategy.MERGE_SMART)
            self.file_content_manager = FileContentManager(default_strategy=merge_strategy)
            logger.info(f"File content manager enabled (strategy: {merge_strategy.value})")
        
        # 初始化压缩器
        self.context_compressor = None
        if self.enable_context_compression:
            self.context_compressor = ThreeLayerContextCompressor(
                llm_client=self.llm_client,
                context_size_limit=context_size_limit,
                recent_file_window=recent_file_window
            )
            logger.info(f"Context compression enabled (limit: {context_size_limit} bytes)")
        
        # 初始化诊断日志器
        self.diagnostic_logger = None
        if enable_diagnostic_logging and DIAGNOSTIC_LOGGING_AVAILABLE:
            self.diagnostic_logger = init_diagnostic_logger(diagnostic_log_file)
            logger.info(f"Diagnostic logging enabled: {diagnostic_log_file}")
            
        self.steps: List[Step] = []
        self.current_step_index: int = 0
        
    def _action_decider(self, step: Step) -> Optional[Dict]:
        """动作决策器 - 改进版，集成文件缓存和依赖分析"""
        # 依赖分析（如果启用）
        dependency_info = ""
        suggested_next_file = None
        
        if self.enable_dependency_analysis and self.dependency_analyzer and hasattr(step, 'deliverables'):
            # 分析待创建文件的依赖关系
            pending_files = self._extract_pending_files(step)
            created_files = self.context.get('created_files', [])
            
            if pending_files:
                # 获取推荐的创建顺序
                ordered_files = self.dependency_analyzer.get_creation_order(pending_files)
                
                # 找到下一个应该创建的文件
                for file_path in ordered_files:
                    if not any(file_path in created for created in created_files):
                        suggested_next_file = file_path
                        dependency_info = f"\n\n依赖分析建议：\n下一个应该创建的文件是 {file_path}（基于依赖关系）"
                        break
                        
        # 基础提示词
        base_system_prompt = """你是一个动作决策专家。根据当前步骤和已执行的动作，决定下一个需要执行的动作。

可用工具：
- read_file: 读取文件内容
- write_file: 写入文件内容
- list_files: 列出目录文件
- python_repl: 执行Python代码
- bash: 执行系统命令

决策原则：
1. 分析步骤目标和已完成的动作
2. 如果步骤目标已达成，返回 null
3. 否则返回下一个必要的动作
4. 优先使用已缓存的文件内容，避免重复读取
5. 遵循依赖关系，先创建被依赖的模块

返回格式：
{
    "tool_name": "工具名称",
    "description": "这个动作要做什么",
    "params": {"参数名": "参数值"}
}

或者如果不需要更多动作：
null"""

        # 如果启用了文件缓存，增强提示词
        if self.enable_file_cache and self.file_cache:
            # 提取步骤中可能需要的文件
            potential_files = self._extract_file_references(step, self.context.get('task', ''))
            
            # 增强提示词，包含缓存信息
            system_prompt = integrate_cache_with_action_decider(
                base_system_prompt,
                self.file_cache,
                potential_files
            )
        else:
            system_prompt = base_system_prompt
        
        # 构建已执行动作的摘要
        actions_summary = ""
        if step.actions:
            actions_summary = "\n已执行的动作：\n"
            for i, action in enumerate(step.actions, 1):
                actions_summary += f"{i}. {action.tool_name}: {action.description}"
                if action.success:
                    actions_summary += " ✓"
                else:
                    actions_summary += " ✗"
                actions_summary += "\n"
                
        # 如果有缓存的文件内容，添加到上下文
        cached_files_info = ""
        if self.enable_file_cache and self.file_cache:
            cached_files = self.file_cache.get_cache_summary()
            if cached_files != "当前没有缓存的文件。":
                cached_files_info = f"\n\n{cached_files}"
                
        human_prompt = f"""当前步骤：{step.name}
步骤描述：{step.description}
期望输出：{step.expected_output}

{actions_summary}

任务上下文：{self.context.get('task', '未知')}
{cached_files_info}
{dependency_info}

请决定下一个动作，如果步骤已完成则返回 null。
特别注意：
1. 如果需要的文件已经在缓存中，不要重复读取
2. 遵循依赖关系建议，确保被依赖的模块先创建"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            response = self.llm_client.invoke(messages)
            response = response.content if hasattr(response, 'content') else str(response)
            
            content = response.strip()
            if content.lower() == "null" or content == "None":
                return None
                
            # 解析 JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            decision = json.loads(content)
            
            # 验证必需字段
            required = ["tool_name", "description", "params"]
            for field in required:
                if field not in decision:
                    raise ValueError(f"Missing required field: {field}")
                    
            # 如果是 read_file 操作，检查缓存
            if decision["tool_name"] == "read_file" and self.enable_file_cache:
                file_path = decision["params"].get("path", decision["params"].get("file_path", ""))
                if file_path and self.file_cache.has_file(file_path):
                    logger.info(f"Intercepting read_file for cached file: {file_path}")
                    # 可以选择直接返回 None 或修改为其他操作
                    cache_stats = self.file_cache.get_cache_stats()
                    if file_path in cache_stats["access_stats"] and cache_stats["access_stats"][file_path] >= 3:
                        logger.warning(f"File {file_path} has been read {cache_stats['access_stats'][file_path]} times. Skipping redundant read.")
                        return None
                    
            return decision
            
        except Exception as e:
            logger.error(f"Action decision failed: {e}")
            return None
            
    def _extract_file_references(self, step: Step, task: str) -> set:
        """从步骤和任务中提取可能的文件引用"""
        import re
        
        references = set()
        
        # 查找常见的文件模式
        patterns = [
            r'([a-zA-Z0-9_\-/]+\.(?:py|md|yaml|yml|json|txt|csv))',  # 文件扩展名
            r'`([^`]+)`',  # 反引号中的内容
            r'"([^"]+)"',  # 双引号中的内容
            r"'([^']+)'",  # 单引号中的内容
        ]
        
        text = f"{step.description} {step.expected_output} {task}"
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 过滤掉明显不是文件路径的内容
                if '/' in match or '.' in match:
                    if not match.startswith('http') and len(match) < 100:
                        references.add(match)
                        
        return references
        
    def _update_context_from_action(self, action: Action):
        """根据动作结果更新上下文 - 改进版，集成文件缓存"""
        import time
        
        # 如果是读取文件，保存到缓存
        if action.tool_name == "read_file" and action.success:
            file_path = action.params.get("path", action.params.get("file_path", ""))
            if file_path and action.result:
                # 更新文件缓存
                if self.enable_file_cache and self.file_cache:
                    self.file_cache.add_file(file_path, action.result)
                    
                # 仍然保存到上下文（为了兼容性）
                if "file_contents" not in self.context:
                    self.context["file_contents"] = {}
                    
                self.context["file_contents"][file_path] = {
                    "content": action.result,
                    "timestamp": time.time(),
                    "size": len(action.result) if action.result else 0
                }
                
                self.context["last_file_content"] = action.result
                self.context["last_file_path"] = file_path
                
                logger.debug(f"Stored file content: {file_path} ({len(action.result)} bytes)")
                
                # 记录缓存统计
                if self.enable_file_cache and self.diagnostic_logger:
                    cache_stats = self.file_cache.get_cache_stats()
                    self.diagnostic_logger.logger.info(
                        f"File cache stats: {cache_stats['total_files']} files, "
                        f"{cache_stats['total_size']} bytes, "
                        f"frequent files: {cache_stats['frequent_files']}"
                    )
            
        # 如果是写入文件，记录已创建的文件
        elif action.tool_name == "write_file" and action.success:
            if "created_files" not in self.context:
                self.context["created_files"] = []
            file_path = action.params.get("path", action.params.get("file_path", ""))
            if file_path:
                self.context["created_files"].append(file_path)
                
                # 记录到文件内容管理器（如果启用）
                if self.enable_file_content_management and self.file_content_manager:
                    import time
                    content = action.params.get("content", "")
                    self.file_content_manager.record_file_write(
                        file_path, content, action.description, 
                        len(self.context.get("created_files", [])) - 1,  # action index
                        time.time()
                    )
                    
                    # 记录统计
                    stats = self.file_content_manager.get_stats()
                    logger.debug(f"File content manager stats: {stats}")
                
                # 分析新创建文件的依赖关系（如果启用）
                if self.enable_dependency_analysis and self.dependency_analyzer and action.params.get("content"):
                    content = action.params["content"]
                    dependencies = self.dependency_analyzer.analyze_code_dependencies(content, file_path)
                    
                    # 记录依赖关系
                    for dep in dependencies:
                        self.dependency_analyzer.dependencies.append(dep)
                        logger.debug(f"Found dependency: {dep.source} -> {dep.target} ({dep.type.value})")
                        
                    # 检查是否有缺失的依赖
                    suggestions = self.dependency_analyzer.suggest_missing_dependencies(content, file_path)
                    if suggestions:
                        logger.warning(f"Missing dependencies detected for {file_path}:")
                        for suggested_file, _ in suggestions:
                            logger.warning(f"  - Should create: {suggested_file}")
                
    def execute_task(self, task: str) -> Tuple[bool, str]:
        """执行任务 - 从原版复制主要逻辑"""
        logger.info(f"Starting task: {task}")
        self.context["task"] = task
        
        # 尝试从任务中提取输出目录
        if self.enable_path_validation and self.path_validator:
            import re
            # 查找常见的输出目录模式
            output_dir_patterns = [
                r'output[^/\\]*[/\\](\S+)',
                r'生成.*?到\s*(\S+)',
                r'创建.*?在\s*(\S+)',
                r'(\w+_output\w*)'
            ]
            
            for pattern in output_dir_patterns:
                match = re.search(pattern, task)
                if match:
                    output_dir = match.group(1).strip()
                    self.path_validator.set_output_directory(output_dir)
                    logger.info(f"Detected output directory from task: {output_dir}")
                    break
        
        # 记录诊断日志
        if self.diagnostic_logger:
            self.diagnostic_logger.log_task(task)
        
        try:
            # 1. 创建初始计划
            self._create_plan(task)
            
            # 2. 执行步骤
            while self.current_step_index < len(self.steps):
                step = self.steps[self.current_step_index]
                
                # 执行单个步骤（支持多动作）
                success = self._execute_step(step)
                
                if not success:
                    return False, f"Step failed: {step.name}"
                    
                # 动态调整计划（如果启用）
                if self.enable_dynamic_planning and self.current_step_index < len(self.steps) - 1:
                    self._adjust_plan_if_needed()
                    
                self.current_step_index += 1
                
            # 诊断日志 - 生成总结
            if self.diagnostic_logger:
                # 添加文件缓存统计
                if self.enable_file_cache:
                    cache_stats = self.file_cache.get_cache_stats()
                    self.diagnostic_logger.logger.info(f"Final file cache stats: {json.dumps(cache_stats, ensure_ascii=False)}")
                    
                self.diagnostic_logger.log_summary()
                
            return True, "Task completed successfully"
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            
            # 诊断日志 - 错误
            if self.diagnostic_logger:
                self.diagnostic_logger.log_error("Task execution failed", e)
                self.diagnostic_logger.log_summary()
                
            return False, str(e)
            
    # 复制其他必要的方法（从 core_v2_new.py）
    def _execute_step(self, step: Step) -> bool:
        """执行单个步骤 - 支持多个动作"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Executing step: {step.name}")
        logger.info(f"Description: {step.description}")
        logger.info(f"Expected output: {step.expected_output}")
        logger.info(f"{'='*60}")
        
        # 诊断日志 - 步骤开始
        if self.diagnostic_logger:
            self.diagnostic_logger.log_step_start(
                step.name, step.description, step.expected_output
            )
        
        step.status = StepStatus.IN_PROGRESS
        action_count = 0
        
        # 初始化决策上下文（如果启用优化）
        decision_context = None
        quick_checker = None
        if self.enable_decision_optimization and self.decision_optimizer:
            decision_context = DecisionContext(
                action_count=0,
                success_count=0,
                files_created=0,
                expected_deliverables=len(getattr(step, 'deliverables', [])),
                last_decision_at=0,
                step_type=getattr(step, 'type', 'unknown')
            )
            quick_checker = create_quick_checker(step)
        
        while action_count < self.max_actions_per_step:
            # 1. 使用动作决策器决定下一个动作
            action_decision = self._action_decider(step)
            
            if not action_decision:
                logger.info("No more actions needed for this step")
                break
                
            # 2. 执行动作
            action = Action(
                tool_name=action_decision["tool_name"],
                description=action_decision["description"],
                params=action_decision["params"]
            )
            
            logger.info(f"\nAction {action_count + 1}: {action.tool_name} - {action.description}")
            
            # 诊断日志 - 动作
            if self.diagnostic_logger:
                self.diagnostic_logger.log_action(
                    action_count + 1, action.tool_name, 
                    action.description, action.params
                )
            
            try:
                # 如果是写文件操作，先检查文件内容管理
                if action.tool_name == "write_file" and self.enable_file_content_management and self.file_content_manager:
                    file_path = action.params.get("path", action.params.get("file_path", ""))
                    content = action.params.get("content", "")
                    
                    if file_path:
                        # 检查是否应该写入
                        should_write, reason, merged_content = self.file_content_manager.check_file_write(
                            file_path, content, action.description, action_count
                        )
                        
                        if not should_write:
                            logger.warning(f"Skipping file write: {reason}")
                            action.result = f"Skipped: {reason}"
                            action.success = False
                            
                            # 诊断日志
                            if self.diagnostic_logger:
                                self.diagnostic_logger.log_warning(
                                    f"File write skipped for {file_path}: {reason}"
                                )
                            
                            # 跳过执行，但不中断流程
                            continue
                        
                        # 如果需要使用合并后的内容
                        if merged_content and merged_content != content:
                            logger.info(f"Using merged content: {reason}")
                            action.params = action.params.copy()
                            action.params["content"] = merged_content
                
                # 执行动作
                if self.use_langchain_tools:
                    # LangChain 执行器使用工具名称
                    result = self.executor.execute(
                        tool_name=action.tool_name,
                        parameters=action.params
                    )
                    if hasattr(result, 'output'):
                        action.result = result.output
                    else:
                        action.result = str(result)
                else:
                    # 传统执行器使用动作类型
                    result = self.executor.execute(
                        action_type=self._get_action_type(action.tool_name),
                        params=action.params
                    )
                    action.result = str(result)
                action.success = True
                logger.info(f"✓ Action completed successfully")
                
                # 诊断日志 - 动作结果
                if self.diagnostic_logger:
                    self.diagnostic_logger.log_action_result(
                        True, action.result
                    )
                
                # 更新上下文
                self._update_context_from_action(action)
                
                # 检查并压缩上下文（如果需要）
                if self.enable_context_compression and self.context_compressor:
                    if self.context_compressor.should_compress(self.context):
                        logger.info("Context size exceeded limit, compressing...")
                        original_context = self.context.copy()
                        self.context = self.context_compressor.compress_with_attention(
                            self.context,
                            task=self.context.get("task", ""),
                            step_plan=self.steps,
                            current_step=step,
                            current_action=action.description
                        )
                        # 保存压缩统计
                        stats = self.context_compressor.get_compression_stats(
                            original_context, self.context
                        )
                        self.context["_compression_stats"] = stats
                        logger.info(f"Compression completed: {stats['space_saved_percentage']:.1f}% saved")
                        
                        # 诊断日志 - 压缩
                        if self.diagnostic_logger:
                            self.diagnostic_logger.log_context_compression(
                                stats['original_size'],
                                stats['compressed_size'],
                                stats['space_saved_percentage']
                            )
                
            except Exception as e:
                logger.error(f"✗ Action failed: {e}")
                action.result = str(e)
                action.success = False
                
                # 诊断日志 - 动作失败
                if self.diagnostic_logger:
                    self.diagnostic_logger.log_action_result(
                        False, None, str(e)
                    )
                
                step.status = StepStatus.FAILED
                return False
                
            # 3. 记录动作
            step.actions.append(action)
            action_count += 1
            
            # 更新决策上下文（如果启用优化）
            if decision_context:
                decision_context.action_count = action_count
                if action.success:
                    decision_context.success_count += 1
                    if action.tool_name == "write_file":
                        decision_context.files_created += 1
            
            # 4. 决定是否检查步骤完成状态
            should_check = True
            check_reason = "默认检查"
            
            if self.enable_decision_optimization and self.decision_optimizer and decision_context:
                # 先进行快速检查
                if quick_checker:
                    quick_result = quick_checker(step.actions)
                    if quick_result is False:
                        should_check = False
                        check_reason = "快速检查：明显未完成"
                        logger.debug(f"Skipping step completion check: {check_reason}")
                
                # 如果快速检查没有明确结果，使用决策优化器
                if should_check:
                    should_check, check_reason = self.decision_optimizer.should_check_completion(decision_context)
                    
                    if not should_check:
                        logger.debug(f"Skipping step completion check: {check_reason}")
            
            # 执行步骤完成检查（如果需要）
            if should_check:
                logger.debug(f"Checking step completion: {check_reason}")
                
                # 记录决策（如果使用优化器）
                if self.decision_optimizer and decision_context:
                    self.decision_optimizer.record_decision(decision_context)
                
                if self._step_decider(step):
                    logger.info(f"\n✓ Step completed: {step.name}")
                    
                    # 记录决策优化统计
                    if self.decision_optimizer:
                        stats = self.decision_optimizer.get_stats()
                        logger.info(f"Decision optimization stats: "
                                  f"Saved {stats['skipped_checks']} checks "
                                  f"({stats['efficiency_rate']:.1%} efficiency)")
                    break
                
        # 检查是否因为达到最大动作数而退出
        if action_count >= self.max_actions_per_step:
            logger.warning(f"Reached maximum actions ({self.max_actions_per_step}) for step")
            if self.diagnostic_logger:
                self.diagnostic_logger.log_warning(
                    f"Step '{step.name}' reached maximum actions limit ({self.max_actions_per_step})"
                )
            
        step.status = StepStatus.COMPLETED
        
        # 诊断日志 - 步骤结束
        if self.diagnostic_logger:
            self.diagnostic_logger.log_step_end(step.name, step.status.value)
            
        return True
        
    def _step_decider(self, step: Step) -> bool:
        """步骤决策器 - 基于里程碑交付物判断步骤是否完成"""
        if not step.actions:
            return False
            
        # 快速判断：如果步骤明显未完成（基于交付物数量）
        if hasattr(step, 'deliverables') and len(step.deliverables) > 0:
            # 统计已创建的文件数
            created_files = sum(1 for action in step.actions 
                              if action.tool_name == "write_file" and action.success)
            
            # 如果创建的文件数远少于交付物数量，明显未完成
            if created_files < len(step.deliverables) * 0.5:
                logger.info(f"Quick decision: Step not completed (created {created_files} files, "
                          f"expected at least {len(step.deliverables)} deliverables)")
                return False
        
        # 构建步骤决策提示词 - 强调里程碑验收
        system_prompt = """你是一个软件工程里程碑验收专家。根据步骤的交付物、验收标准和已执行的动作，判断里程碑是否达成。

评估原则：
1. **交付物完整性**：所有承诺的交付物必须完成
2. **验收标准满足**：每个验收标准都要达到
3. **原子性判断**：里程碑要么完全完成，要么未完成，不存在部分完成

返回格式：
{
    "completed": true/false,
    "reason": "判断理由",
    "missing_deliverables": ["缺失的交付物1", "缺失的交付物2"],
    "unmet_criteria": ["未满足的验收标准1", "未满足的验收标准2"]
}"""

        # 构建动作执行详情
        actions_detail = "已执行的动作及结果：\n"
        for i, action in enumerate(step.actions, 1):
            actions_detail += f"\n{i}. {action.tool_name}: {action.description}\n"
            actions_detail += f"   参数: {json.dumps(action.params, ensure_ascii=False)}\n"
            actions_detail += f"   结果: {'成功' if action.success else '失败'}\n"
            if action.result:
                # 限制结果长度
                result_preview = action.result[:200] + "..." if len(action.result) > 200 else action.result
                actions_detail += f"   输出: {result_preview}\n"

        # 构建包含里程碑信息的提示
        deliverables_info = ""
        if hasattr(step, 'deliverables') and step.deliverables:
            deliverables_info = "\n具体交付物：\n"
            deliverables_info += "\n".join(f"- {d}" for d in step.deliverables)
            
        criteria_info = ""
        if hasattr(step, 'acceptance_criteria') and step.acceptance_criteria:
            criteria_info = "\n\n验收标准：\n"
            criteria_info += "\n".join(f"- {c}" for c in step.acceptance_criteria)
            
        human_prompt = f"""里程碑步骤：{step.name}
类型：{getattr(step, 'type', '未知')}
描述：{step.description}
{deliverables_info}{criteria_info}

{actions_detail}

请基于交付物完整性和验收标准满足情况，判断此里程碑是否完成。
记住：里程碑必须完全达成才算完成，部分完成也视为未完成。"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            response = self.llm_client.invoke(messages)
            response = response.content if hasattr(response, 'content') else str(response)
            
            # 解析 JSON
            content = response.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            decision = json.loads(content)
            
            logger.info(f"Step completion decision: {decision}")
            
            # 诊断日志 - 步骤决策
            if self.diagnostic_logger:
                self.diagnostic_logger.log_step_decision(
                    decision.get("completed", False),
                    decision.get("reason", ""),
                    decision.get("missing")
                )
            
            return decision.get("completed", False)
            
        except Exception as e:
            logger.error(f"Step decision failed: {e}")
            # 默认认为未完成，继续执行
            return False
            
    def _extract_pending_files(self, step: Step) -> List[str]:
        """从步骤中提取待创建的文件列表"""
        import re
        
        pending_files = []
        
        # 从交付物中提取文件
        if hasattr(step, 'deliverables'):
            for deliverable in step.deliverables:
                # 查找文件路径模式
                file_patterns = [
                    r'([a-zA-Z0-9_\-/]+\.py)',     # Python文件
                    r'([a-zA-Z0-9_\-/]+\.json)',   # JSON文件
                    r'([a-zA-Z0-9_\-/]+\.yaml)',   # YAML文件
                    r'([a-zA-Z0-9_\-/]+\.yml)',    # YML文件
                    r'([a-zA-Z0-9_\-/]+\.txt)',    # 文本文件
                ]
                
                for pattern in file_patterns:
                    matches = re.findall(pattern, deliverable)
                    pending_files.extend(matches)
                    
        # 从步骤描述中提取
        search_text = f"{step.description} {step.expected_output}"
        for pattern in [r'`([^`]+\.py)`', r'"([^"]+\.py)"', r'创建\s*(\S+\.py)']:
            matches = re.findall(pattern, search_text)
            pending_files.extend(matches)
            
        # 去重并返回
        return list(set(pending_files))
            
    def _create_plan(self, task: str):
        """创建执行计划 - 使用改进的里程碑式规划"""
        logger.info("Creating milestone-based execution plan...")
        
        # 初始化里程碑规划器
        self.milestone_planner = MilestoneBasedPlanner()
        
        try:
            # 使用改进的规划提示词
            messages = [
                SystemMessage(content=IMPROVED_PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=IMPROVED_PLANNER_HUMAN_PROMPT.format(task=task))
            ]
            response = self.llm_client.invoke(messages)
            response = response.content if hasattr(response, 'content') else str(response)
            
            # 解析计划
            plan_text = response.strip()
            if plan_text.startswith("```json"):
                plan_text = plan_text[7:]
            if plan_text.endswith("```"):
                plan_text = plan_text[:-3]
                
            plan_data = json.loads(plan_text)
            
            # 验证计划质量
            is_valid, issues = self.milestone_planner.validate_plan(plan_data)
            if not is_valid:
                logger.warning(f"Plan validation issues: {issues}")
                # 可以选择让LLM重新规划或者继续执行
                
            # 创建步骤对象
            self.steps = []
            for step_data in plan_data.get("steps", []):
                # 构建期望输出，结合交付物和验收标准
                deliverables = step_data.get("deliverables", [])
                criteria = step_data.get("acceptance_criteria", [])
                
                expected_output = "交付物：\n"
                expected_output += "\n".join(f"- {d}" for d in deliverables)
                expected_output += "\n\n验收标准：\n"
                expected_output += "\n".join(f"- {c}" for c in criteria)
                
                step = Step(
                    name=step_data["name"],
                    description=step_data.get("description", ""),
                    expected_output=expected_output
                )
                
                # 存储额外信息供后续使用
                step.type = step_data.get("type", "feature")
                step.deliverables = deliverables
                step.acceptance_criteria = criteria
                step.dependencies = step_data.get("dependencies", [])
                
                self.steps.append(step)
                
            logger.info(f"Created milestone-based plan with {len(self.steps)} steps:")
            for i, step in enumerate(self.steps, 1):
                logger.info(f"  Step {i}: {step.name} (类型: {getattr(step, 'type', 'unknown')})")
                if hasattr(step, 'deliverables'):
                    logger.info(f"    交付物: {len(step.deliverables)}个")
                    
            # 诊断日志
            if self.diagnostic_logger:
                self.diagnostic_logger.logger.info(
                    f"Milestone plan created: {len(self.steps)} steps, "
                    f"types: {[getattr(s, 'type', 'unknown') for s in self.steps]}"
                )
                
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            raise
            
    def _adjust_plan_if_needed(self):
        """动态调整计划（从原版复制主要逻辑）"""
        # 暂时跳过实现，专注于文件缓存优化
        pass
        
    def _get_action_type(self, tool_name: str) -> ActionType:
        """将工具名称转换为动作类型"""
        mapping = {
            "read_file": ActionType.READ_FILE,
            "write_file": ActionType.WRITE_FILE,
            "list_files": ActionType.LIST_FILES,
            "python_repl": ActionType.PYTHON,
            "bash": ActionType.BASH
        }
        return mapping.get(tool_name, ActionType.READ_FILE)