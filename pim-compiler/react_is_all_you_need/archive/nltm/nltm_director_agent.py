#!/usr/bin/env python3
"""
NLTM编导Agent实现
负责理解用户意图、生成NLPL程序、调用执行Agent
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.base_agent import BaseAgent, AgentConfig


class NLTMDirectorAgent(BaseAgent):
    """NLTM编导Agent - 负责生成和优化NLPL程序"""
    
    def __init__(self, config: AgentConfig):
        """初始化编导Agent"""
        super().__init__(config)
        self.name = "NLTM-Director"
        
        # 加载NLTM知识文件
        self.knowledge_base = self._load_knowledge_files()
        
        # 执行Agent作为工具
        self.executor_tool = None  # 将被注入
        
        # 执行历史
        self.execution_history = []
        
    def _load_knowledge_files(self) -> Dict[str, str]:
        """加载NLTM知识文件"""
        knowledge_dir = Path(__file__).parent / "knowledge" / "nltm"
        knowledge_files = {
            "engine": "nltm_engine.md",
            "director": "director_agent.md", 
            "executor": "executor_agent.md",
            "templates": "nlpl_templates.md"
        }
        
        knowledge = {}
        for key, filename in knowledge_files.items():
            file_path = knowledge_dir / filename
            if file_path.exists():
                knowledge[key] = file_path.read_text(encoding='utf-8')
        
        return knowledge
    
    def set_executor_tool(self, executor):
        """设置执行Agent工具"""
        self.executor_tool = executor
    
    def execute_task(self, user_request: str) -> Dict[str, Any]:
        """
        执行用户任务
        
        Args:
            user_request: 用户的自然语言请求
            
        Returns:
            执行结果
        """
        try:
            # 1. 理解用户意图
            intent = self._analyze_intent(user_request)
            
            # 2. 生成NLPL程序
            nlpl_program = self._generate_nlpl(intent)
            
            # 3. 创建初始状态
            initial_state = self._create_initial_state(intent)
            
            # 4. 调用执行Agent
            execution_result = self._execute_nlpl(nlpl_program, initial_state)
            
            # 5. 处理执行结果
            if not execution_result["success"]:
                # 动态调整
                nlpl_program, initial_state = self._adjust_nlpl(
                    nlpl_program, 
                    initial_state,
                    execution_result
                )
                # 重新执行
                execution_result = self._execute_nlpl(nlpl_program, initial_state)
            
            # 6. 生成用户响应
            response = self._generate_response(execution_result, intent)
            
            # 7. 记录执行历史
            self._record_execution(user_request, nlpl_program, execution_result)
            
            return {
                "success": True,
                "response": response,
                "nlpl": nlpl_program,
                "execution": execution_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"抱歉，执行过程中出现错误：{str(e)}"
            }
    
    def _analyze_intent(self, user_request: str) -> Dict[str, Any]:
        """分析用户意图"""
        # 这里应该调用LLM来分析
        # 简化实现：基于关键词识别
        
        intent = {
            "request": user_request,
            "type": self._identify_task_type(user_request),
            "parameters": self._extract_parameters(user_request),
            "complexity": self._estimate_complexity(user_request)
        }
        
        return intent
    
    def _identify_task_type(self, request: str) -> str:
        """识别任务类型"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["分析", "统计", "计算"]):
            return "analysis"
        elif any(word in request_lower for word in ["查找", "搜索", "查询"]):
            return "query"
        elif any(word in request_lower for word in ["决策", "选择", "推荐"]):
            return "decision"
        elif any(word in request_lower for word in ["处理", "转换", "格式化"]):
            return "processing"
        else:
            return "general"
    
    def _extract_parameters(self, request: str) -> Dict[str, Any]:
        """提取请求参数"""
        # 简化实现
        return {
            "raw_request": request,
            "timestamp": datetime.now().isoformat()
        }
    
    def _estimate_complexity(self, request: str) -> str:
        """估计任务复杂度"""
        words = len(request.split())
        if words < 10:
            return "simple"
        elif words < 30:
            return "medium"
        else:
            return "complex"
    
    def _generate_nlpl(self, intent: Dict[str, Any]) -> str:
        """生成NLPL程序"""
        task_type = intent["type"]
        
        # 根据任务类型选择模板
        if task_type == "analysis":
            template = self._get_analysis_template()
        elif task_type == "query":
            template = self._get_query_template()
        else:
            template = self._get_general_template()
        
        # 填充模板
        nlpl = template.format(
            goal=intent["request"],
            timestamp=intent["parameters"]["timestamp"]
        )
        
        return nlpl
    
    def _get_analysis_template(self) -> str:
        """获取分析任务模板"""
        return """程序: 数据分析任务
  目标: {goal}
  
  状态:
    输入:
      数据: []
      参数: {{}}
    处理:
      当前步骤: null
      中间结果: {{}}
    输出:
      结果: null
      统计: {{}}
      报告: null
    完成: false
    
  主流程:
    步骤1_准备:
      动作: 准备数据和环境
      验证: 数据可用性
      
    步骤2_分析:
      动作: 执行分析计算
      保存到: 状态.处理.中间结果
      
    步骤3_汇总:
      动作: 生成结果报告
      保存到: 状态.输出.报告
      
    步骤4_完成:
      设置: 状态.完成 = true
      返回: 状态.输出"""
    
    def _get_query_template(self) -> str:
        """获取查询任务模板"""
        return """程序: 查询任务
  目标: {goal}
  
  状态:
    查询:
      条件: null
      结果: []
    完成: false
    
  主流程:
    步骤1_解析:
      动作: 解析查询条件
      
    步骤2_搜索:
      动作: 执行搜索
      保存到: 状态.查询.结果
      
    步骤3_完成:
      设置: 状态.完成 = true
      返回: 状态.查询.结果"""
    
    def _get_general_template(self) -> str:
        """获取通用任务模板"""
        return """程序: 通用任务
  目标: {goal}
  
  状态:
    输入: null
    输出: null
    完成: false
    
  主流程:
    步骤1_执行:
      动作: 执行任务
      
    步骤2_完成:
      设置: 状态.完成 = true
      返回: 状态.输出"""
    
    def _create_initial_state(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """创建初始状态"""
        return {
            "输入": {
                "请求": intent["request"],
                "参数": intent["parameters"]
            },
            "处理": {
                "开始时间": datetime.now().isoformat()
            },
            "输出": None,
            "完成": False
        }
    
    def _execute_nlpl(self, nlpl: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """调用执行Agent执行NLPL程序"""
        if not self.executor_tool:
            # 如果没有真实的执行Agent，返回模拟结果
            return self._simulate_execution(nlpl, state)
        
        # 调用执行Agent工具
        result = self.executor_tool.execute(
            nlpl=nlpl,
            initial_state=state,
            options={
                "mode": "strict",
                "timeout": 30000,
                "checkpoint": True
            }
        )
        
        return result
    
    def _simulate_execution(self, nlpl: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """模拟执行（用于测试）"""
        return {
            "success": True,
            "final_state": {
                **state,
                "输出": {
                    "结果": "模拟执行结果",
                    "统计": {
                        "处理项": 10,
                        "成功": 10,
                        "失败": 0
                    }
                },
                "完成": True
            },
            "execution_trace": [
                {"step": "步骤1_准备", "status": "success"},
                {"step": "步骤2_分析", "status": "success"},
                {"step": "步骤3_汇总", "status": "success"},
                {"step": "步骤4_完成", "status": "success"}
            ],
            "errors": [],
            "statistics": {
                "total_steps": 4,
                "executed_steps": 4,
                "success_steps": 4,
                "failed_steps": 0,
                "duration": 1234
            }
        }
    
    def _adjust_nlpl(self, nlpl: str, state: Dict[str, Any], 
                     execution_result: Dict[str, Any]) -> tuple:
        """动态调整NLPL程序"""
        # 分析错误
        errors = execution_result.get("errors", [])
        if not errors:
            return nlpl, state
        
        # 根据错误类型调整
        error_type = errors[0].get("type", "unknown")
        
        if error_type == "timeout":
            # 添加批处理
            nlpl = self._add_batch_processing(nlpl)
        elif error_type == "data_error":
            # 添加数据验证
            nlpl = self._add_data_validation(nlpl)
        else:
            # 添加错误处理
            nlpl = self._add_error_handling(nlpl)
        
        # 使用最后的状态作为新的初始状态
        new_state = execution_result.get("final_state", state)
        
        return nlpl, new_state
    
    def _add_batch_processing(self, nlpl: str) -> str:
        """添加批处理逻辑"""
        # 简化实现：在处理步骤中添加批处理说明
        return nlpl.replace(
            "步骤2_分析:",
            "步骤2_分析:\n      批处理: 每次处理100项"
        )
    
    def _add_data_validation(self, nlpl: str) -> str:
        """添加数据验证"""
        # 简化实现：添加验证步骤
        return nlpl.replace(
            "步骤1_准备:",
            "步骤1_准备:\n      验证: 数据格式和完整性"
        )
    
    def _add_error_handling(self, nlpl: str) -> str:
        """添加错误处理"""
        # 简化实现：为每个步骤添加失败处理
        return nlpl.replace(
            "动作:",
            "动作:\n      失败时: 记录错误并继续"
        )
    
    def _generate_response(self, execution_result: Dict[str, Any], 
                          intent: Dict[str, Any]) -> str:
        """生成用户友好的响应"""
        if execution_result["success"]:
            stats = execution_result.get("statistics", {})
            output = execution_result.get("final_state", {}).get("输出", {})
            
            response = f"""✅ 任务执行成功！

执行统计：
- 总步骤数：{stats.get('total_steps', 0)}
- 成功步骤：{stats.get('success_steps', 0)}
- 执行时间：{stats.get('duration', 0)}ms

结果摘要：
{json.dumps(output, ensure_ascii=False, indent=2)}
"""
        else:
            errors = execution_result.get("errors", [])
            response = f"""❌ 任务执行失败

错误信息：
{json.dumps(errors, ensure_ascii=False, indent=2)}

请检查输入或稍后重试。
"""
        
        return response
    
    def _record_execution(self, request: str, nlpl: str, 
                         result: Dict[str, Any]):
        """记录执行历史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "nlpl": nlpl,
            "success": result["success"],
            "statistics": result.get("statistics", {})
        }
        
        self.execution_history.append(record)
        
        # 保持历史记录在合理范围内
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history


def create_director_agent(work_dir: str = "./nltm_workspace") -> NLTMDirectorAgent:
    """创建编导Agent实例"""
    config = AgentConfig(
        work_dir=work_dir,
        name="NLTM-Director",
        description="NLTM编导Agent，负责生成和优化NLPL程序"
    )
    
    return NLTMDirectorAgent(config)


if __name__ == "__main__":
    # 测试编导Agent
    director = create_director_agent()
    
    # 测试请求
    test_requests = [
        "帮我分析这组数据的统计信息",
        "查找所有包含Python的文件",
        "帮我决定哪个方案更好"
    ]
    
    for request in test_requests:
        print(f"\n{'='*60}")
        print(f"用户请求: {request}")
        print('='*60)
        
        result = director.execute_task(request)
        
        if result["success"]:
            print(f"响应:\n{result['response']}")
            print(f"\n生成的NLPL:\n{result['nlpl']}")
        else:
            print(f"错误: {result['error']}")