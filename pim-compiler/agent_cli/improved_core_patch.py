"""
核心改进补丁 - 为 core_v2_improved.py 添加任务分类支持
"""

from typing import Tuple
from .task_classifier import TaskClassifier, TaskType
from .query_handler import QueryHandler
import logging

logger = logging.getLogger(__name__)


def patch_agent_cli_v2_improved(agent_class):
    """
    为 AgentCLI_V2_Improved 类添加任务分类支持
    使用猴子补丁方式，避免修改原始文件
    """
    
    # 保存原始的 execute_task 方法
    original_execute_task = agent_class.execute_task
    
    # 创建新的 execute_task 方法
    def enhanced_execute_task(self, task: str) -> Tuple[bool, str]:
        """增强的任务执行 - 添加任务分类"""
        
        # 初始化分类器（如果还没有）
        if not hasattr(self, '_task_classifier'):
            self._task_classifier = TaskClassifier()
            self._query_handler = QueryHandler(self.tool_executor)
        
        # 对任务进行分类
        task_type, confidence = self._task_classifier.classify(task)
        logger.info(f"任务分类: {task_type.value} (置信度: {confidence:.2f})")
        
        # 如果是查询类任务，使用简化处理器
        if task_type == TaskType.QUERY and confidence > 0.6:
            logger.info("使用查询处理器处理任务")
            
            # 尝试识别具体的查询类型
            if "执行流程" in task or "流程是什么" in task:
                # 提取项目路径和名称
                import re
                path_match = re.search(r'([/\w\-_]+)', task)
                if path_match:
                    project_path = path_match.group(1)
                    project_name = project_path.split('/')[-1]
                    return self._query_handler.handle_execution_flow_query(project_name, project_path)
            
            elif "项目结构" in task or "目录结构" in task:
                # 处理项目结构查询
                import re
                path_match = re.search(r'([/\w\-_]+)', task)
                if path_match:
                    project_path = path_match.group(1)
                    return self._query_handler.handle_project_structure_query(project_path)
        
        # 获取执行策略
        strategy = self._task_classifier.get_execution_strategy(task_type)
        
        # 临时修改配置
        original_max_steps = getattr(self, 'max_steps', 10)
        self.max_steps = strategy['max_steps']
        
        # 在规划时注入策略提示
        if hasattr(self, '_create_plan'):
            original_create_plan = self._create_plan
            
            def enhanced_create_plan(task_desc: str):
                # 添加策略提示到任务描述
                enhanced_task = f"{task_desc}\n\n执行提示：{strategy['planning_hint']}"
                return original_create_plan(enhanced_task)
            
            self._create_plan = enhanced_create_plan
        
        try:
            # 调用原始方法
            result = original_execute_task(self, task)
        finally:
            # 恢复原始配置
            self.max_steps = original_max_steps
            if hasattr(self, '_create_plan'):
                self._create_plan = original_create_plan
        
        return result
    
    # 替换方法
    agent_class.execute_task = enhanced_execute_task
    
    logger.info("Successfully patched AgentCLI_V2_Improved with task classification support")
    
    return agent_class


# 使用示例
def apply_patch():
    """应用补丁到 AgentCLI_V2_Improved"""
    try:
        from .core_v2_improved import AgentCLI_V2_Improved
        patch_agent_cli_v2_improved(AgentCLI_V2_Improved)
        return True
    except Exception as e:
        logger.error(f"Failed to apply patch: {e}")
        return False