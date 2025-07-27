"""
改进的任务规划器 v2 - 支持任务类型感知的规划
"""

from typing import Dict, List, Any
from .task_classifier import TaskType

# 针对不同任务类型的规划模板
QUERY_PLANNER_PROMPT = """你是一个代码分析专家，负责理解和分析现有代码。

对于查询/分析类任务，请遵循以下原则：
1. **最小化步骤**：通常 2-3 个步骤就足够
2. **只读操作**：只使用读取和搜索工具，不创建或修改文件
3. **快速定位**：直接找到关键信息，不要过度探索

返回格式：
{
    "steps": [
        {
            "name": "步骤名称",
            "actions": ["read_file:README.md", "search:main function"],
            "expected_outcome": "预期结果"
        }
    ]
}
"""

CREATE_PLANNER_PROMPT = """你是一个软件架构师，负责规划新功能的实现。

对于创建/实现类任务，请遵循里程碑方式：
1. **模块化设计**：每个步骤是一个完整的功能模块
2. **渐进式构建**：从基础到复杂，逐步构建
3. **可验证性**：每步都有明确的验收标准

返回格式：
{
    "steps": [
        {
            "name": "里程碑名称",
            "type": "infrastructure|feature|integration|validation",
            "deliverables": ["交付物1", "交付物2"],
            "acceptance_criteria": ["验收标准1", "验收标准2"]
        }
    ]
}
"""

class AdaptivePlanner:
    """自适应任务规划器 - 根据任务类型选择合适的规划策略"""
    
    def __init__(self):
        self.planners = {
            TaskType.QUERY: self._plan_query_task,
            TaskType.CREATE: self._plan_create_task,
            TaskType.MODIFY: self._plan_modify_task,
            TaskType.DEBUG: self._plan_debug_task,
            TaskType.EXPLAIN: self._plan_explain_task,
        }
        
    def create_plan(self, task: str, task_type: TaskType, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        根据任务类型创建适应性计划
        
        Args:
            task: 任务描述
            task_type: 任务类型
            context: 上下文信息
            
        Returns:
            计划字典
        """
        planner = self.planners.get(task_type, self._plan_default)
        return planner(task, context)
    
    def _plan_query_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """规划查询类任务"""
        # 分析查询意图
        if "执行流程" in task or "流程" in task:
            return {
                "steps": [
                    {
                        "name": "查找项目文档",
                        "actions": ["read_file:README.md", "read_file:docs/architecture.md"],
                        "expected_outcome": "理解项目概述和架构"
                    },
                    {
                        "name": "定位入口点",
                        "actions": ["search:if __name__", "search:main(", "list_files:./"],
                        "expected_outcome": "找到程序入口"
                    },
                    {
                        "name": "分析执行流程",
                        "actions": ["read_file:<入口文件>"],
                        "expected_outcome": "理解完整执行流程"
                    }
                ]
            }
        elif "结构" in task:
            return {
                "steps": [
                    {
                        "name": "扫描项目结构",
                        "actions": ["list_files:./", "read_file:README.md"],
                        "expected_outcome": "获取项目布局"
                    },
                    {
                        "name": "分析核心模块",
                        "actions": ["list_files:src/", "list_files:lib/"],
                        "expected_outcome": "理解模块组织"
                    }
                ]
            }
        else:
            # 通用查询计划
            return {
                "steps": [
                    {
                        "name": "搜索相关信息",
                        "actions": ["search:<关键词>", "read_file:<相关文件>"],
                        "expected_outcome": "找到相关信息"
                    }
                ]
            }
    
    def _plan_create_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """规划创建类任务"""
        # 保持原有的里程碑式规划
        return {
            "steps": [
                {
                    "name": "初始化项目结构",
                    "type": "infrastructure",
                    "deliverables": ["项目目录", "配置文件"],
                    "acceptance_criteria": ["目录结构创建完成", "配置文件就绪"]
                },
                {
                    "name": "实现核心功能",
                    "type": "feature",
                    "deliverables": ["主要功能代码", "辅助模块"],
                    "acceptance_criteria": ["功能可运行", "无语法错误"]
                },
                {
                    "name": "添加错误处理和优化",
                    "type": "integration",
                    "deliverables": ["错误处理代码", "性能优化"],
                    "acceptance_criteria": ["异常被正确捕获", "代码结构清晰"]
                }
            ]
        }
    
    def _plan_modify_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """规划修改类任务"""
        return {
            "steps": [
                {
                    "name": "分析现有代码",
                    "actions": ["read_file:<目标文件>", "search:<相关功能>"],
                    "expected_outcome": "理解当前实现"
                },
                {
                    "name": "实施修改",
                    "actions": ["modify_file:<目标文件>"],
                    "expected_outcome": "完成代码修改"
                },
                {
                    "name": "验证修改",
                    "actions": ["python_repl:<测试代码>"],
                    "expected_outcome": "确认修改正确"
                }
            ]
        }
    
    def _plan_debug_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """规划调试类任务"""
        return {
            "steps": [
                {
                    "name": "重现问题",
                    "actions": ["read_file:<问题文件>", "python_repl:<测试代码>"],
                    "expected_outcome": "确认问题存在"
                },
                {
                    "name": "定位根因",
                    "actions": ["search:error", "search:exception", "read_file:<相关模块>"],
                    "expected_outcome": "找到问题原因"
                },
                {
                    "name": "修复问题",
                    "actions": ["modify_file:<问题文件>"],
                    "expected_outcome": "问题已修复"
                },
                {
                    "name": "验证修复",
                    "actions": ["python_repl:<验证代码>"],
                    "expected_outcome": "确认问题解决"
                }
            ]
        }
    
    def _plan_explain_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """规划解释类任务"""
        return {
            "steps": [
                {
                    "name": "读取目标代码",
                    "actions": ["read_file:<目标文件>"],
                    "expected_outcome": "获取完整代码"
                },
                {
                    "name": "分析并添加注释",
                    "actions": ["write_file:<带注释的文件>"],
                    "expected_outcome": "生成解释文档"
                }
            ]
        }
    
    def _plan_default(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """默认规划策略"""
        return {
            "steps": [
                {
                    "name": "分析任务需求",
                    "actions": ["think"],
                    "expected_outcome": "明确任务目标"
                },
                {
                    "name": "执行任务",
                    "actions": ["execute"],
                    "expected_outcome": "完成任务"
                }
            ]
        }
    
    def optimize_plan(self, plan: Dict[str, Any], execution_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        基于执行历史优化计划
        
        Args:
            plan: 当前计划
            execution_history: 执行历史
            
        Returns:
            优化后的计划
        """
        # 分析执行历史中的失败模式
        failures = [h for h in execution_history if not h.get('success', True)]
        
        if failures:
            # 基于失败原因调整计划
            for failure in failures:
                if "file not found" in str(failure.get('error', '')):
                    # 添加文件搜索步骤
                    plan['steps'].insert(0, {
                        "name": "搜索必要文件",
                        "actions": ["search:<文件名>", "list_files:./"],
                        "expected_outcome": "找到所需文件"
                    })
                elif "permission" in str(failure.get('error', '')):
                    # 添加权限检查步骤
                    plan['steps'].insert(0, {
                        "name": "检查权限",
                        "actions": ["check_permissions"],
                        "expected_outcome": "确认有必要权限"
                    })
        
        return plan