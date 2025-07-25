"""
决策优化器 - 减少重复决策开销
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DecisionStrategy(Enum):
    """决策策略"""
    ALWAYS = "always"           # 每次动作后都决策（原始行为）
    BATCH = "batch"            # 批量动作后决策
    SMART = "smart"            # 智能决策（基于启发式规则）
    MILESTONE = "milestone"    # 里程碑决策（基于交付物）


@dataclass
class DecisionContext:
    """决策上下文"""
    action_count: int              # 已执行的动作数
    success_count: int             # 成功的动作数
    files_created: int             # 创建的文件数
    expected_deliverables: int     # 期望的交付物数量
    last_decision_at: int          # 上次决策时的动作数
    step_type: str                 # 步骤类型


class DecisionOptimizer:
    """决策优化器
    
    减少不必要的步骤完成判断，提高执行效率
    """
    
    def __init__(
        self,
        strategy: DecisionStrategy = DecisionStrategy.SMART,
        batch_size: int = 3,
        min_progress_threshold: float = 0.3
    ):
        self.strategy = strategy
        self.batch_size = batch_size
        self.min_progress_threshold = min_progress_threshold
        self.decision_count = 0
        self.skipped_count = 0
        
    def should_check_completion(self, context: DecisionContext) -> Tuple[bool, str]:
        """判断是否应该检查步骤完成状态
        
        Returns:
            (should_check, reason): 是否检查和原因
        """
        if self.strategy == DecisionStrategy.ALWAYS:
            return True, "策略：每次都检查"
            
        elif self.strategy == DecisionStrategy.BATCH:
            # 批量策略：每N个动作检查一次
            actions_since_last = context.action_count - context.last_decision_at
            if actions_since_last >= self.batch_size:
                return True, f"批量策略：已执行 {actions_since_last} 个动作"
            else:
                self.skipped_count += 1
                return False, f"批量策略：等待更多动作 ({actions_since_last}/{self.batch_size})"
                
        elif self.strategy == DecisionStrategy.SMART:
            return self._smart_decision(context)
            
        elif self.strategy == DecisionStrategy.MILESTONE:
            return self._milestone_decision(context)
            
        return True, "默认：检查完成状态"
        
    def _smart_decision(self, context: DecisionContext) -> Tuple[bool, str]:
        """智能决策：基于启发式规则"""
        
        # 规则1：如果没有成功的动作，明显未完成
        if context.success_count == 0:
            self.skipped_count += 1
            return False, "智能决策：还没有成功的动作"
            
        # 规则2：如果步骤类型是基础设施，且已创建目录，可能需要检查
        if context.step_type == "infrastructure" and context.action_count >= 2:
            return True, "智能决策：基础设施步骤可能已完成"
            
        # 规则3：如果有期望的交付物数量，检查进度
        if context.expected_deliverables > 0:
            progress = context.files_created / context.expected_deliverables
            
            # 进度太低，明显未完成
            if progress < self.min_progress_threshold:
                self.skipped_count += 1
                return False, f"智能决策：进度过低 ({progress:.1%})"
                
            # 进度接近完成，应该检查
            if progress >= 0.8:
                return True, f"智能决策：进度接近完成 ({progress:.1%})"
                
        # 规则4：执行了足够多的动作，应该检查一次
        if context.action_count - context.last_decision_at >= self.batch_size:
            return True, "智能决策：达到批量阈值"
            
        # 规则5：如果最近的动作是关键动作（如写入主文件），应该检查
        # 这需要额外的上下文信息，暂时跳过
        
        # 默认：跳过检查
        self.skipped_count += 1
        return False, "智能决策：继续执行更多动作"
        
    def _milestone_decision(self, context: DecisionContext) -> Tuple[bool, str]:
        """里程碑决策：基于交付物完成情况"""
        
        # 如果没有定义交付物，退回到批量策略
        if context.expected_deliverables == 0:
            actions_since_last = context.action_count - context.last_decision_at
            if actions_since_last >= self.batch_size:
                return True, "里程碑决策：无交付物定义，使用批量策略"
            else:
                self.skipped_count += 1
                return False, "里程碑决策：等待更多动作"
                
        # 计算交付物完成率
        completion_rate = context.files_created / context.expected_deliverables
        
        # 如果所有交付物都完成了，必须检查
        if completion_rate >= 1.0:
            return True, "里程碑决策：所有交付物已创建"
            
        # 如果完成率很低，且动作数不多，跳过
        if completion_rate < 0.5 and context.action_count < 5:
            self.skipped_count += 1
            return False, f"里程碑决策：交付物完成率低 ({completion_rate:.1%})"
            
        # 如果执行了很多动作但交付物完成率仍然很低，可能有问题，应该检查
        if context.action_count > 8 and completion_rate < 0.3:
            return True, "里程碑决策：动作多但交付物少，需要检查"
            
        # 默认：基于批量大小
        if context.action_count - context.last_decision_at >= self.batch_size * 2:
            return True, "里程碑决策：达到扩展批量阈值"
            
        self.skipped_count += 1
        return False, "里程碑决策：继续执行"
        
    def record_decision(self, context: DecisionContext):
        """记录决策"""
        self.decision_count += 1
        context.last_decision_at = context.action_count
        
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "total_decisions": self.decision_count,
            "skipped_checks": self.skipped_count,
            "efficiency_rate": self.skipped_count / (self.decision_count + self.skipped_count) 
                              if (self.decision_count + self.skipped_count) > 0 else 0
        }


def create_quick_checker(step) -> callable:
    """创建快速检查函数，用于明显未完成的情况"""
    
    def quick_check(actions: List) -> Optional[bool]:
        """快速检查步骤是否明显未完成
        
        Returns:
            True: 明显已完成
            False: 明显未完成
            None: 需要详细检查
        """
        # 如果没有动作，明显未完成
        if not actions:
            return False
            
        # 如果步骤有交付物定义
        if hasattr(step, 'deliverables') and step.deliverables:
            # 统计创建的文件
            files_created = sum(1 for a in actions 
                              if a.tool_name == "write_file" and a.success)
            
            # 如果文件数远少于交付物数，明显未完成
            if files_created < len(step.deliverables) * 0.3:
                logger.debug(f"Quick check: Only {files_created}/{len(step.deliverables)} "
                           f"deliverables created, obviously incomplete")
                return False
                
            # 如果所有预期文件都创建了，可能已完成（但仍需详细检查）
            if files_created >= len(step.deliverables):
                return None
                
        # 对于基础设施步骤，如果只执行了1-2个动作，可能未完成
        if hasattr(step, 'type') and step.type == 'infrastructure':
            if len(actions) <= 2:
                return False
                
        # 其他情况需要详细检查
        return None
        
    return quick_check