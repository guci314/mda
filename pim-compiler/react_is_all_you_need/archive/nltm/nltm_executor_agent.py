#!/usr/bin/env python3
"""
NLTM执行Agent实现 - 作为工具
负责严格执行NLPL程序
"""

import json
import time
import copy
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class StepStatus(Enum):
    """步骤执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionMode(Enum):
    """执行模式"""
    STRICT = "strict"      # 严格模式：遇错即停
    ADAPTIVE = "adaptive"  # 适应模式：尝试恢复


class NLPLExecutor:
    """NLTM执行Agent - 作为工具被调用"""
    
    # 工具接口定义
    tool_interface = {
        "name": "nlpl_executor",
        "description": "执行NLPL程序并返回结果",
        "parameters": {
            "nlpl": "NLPL程序文本",
            "initial_state": "初始状态字典",
            "options": "执行选项（可选）"
        },
        "returns": {
            "success": "是否成功",
            "final_state": "最终状态",
            "execution_trace": "执行轨迹",
            "errors": "错误列表",
            "statistics": "执行统计"
        }
    }
    
    def __init__(self):
        """初始化执行器"""
        self.reset()
    
    def reset(self):
        """重置执行器状态"""
        self.context = None
        self.start_time = None
        self.checkpoints = []
    
    def execute(self, nlpl: str, initial_state: Dict[str, Any], 
                options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行NLPL程序（工具接口）
        
        Args:
            nlpl: NLPL程序文本
            initial_state: 初始状态
            options: 执行选项
            
        Returns:
            执行结果
        """
        try:
            # 重置状态
            self.reset()
            self.start_time = time.time()
            
            # 解析选项
            options = options or {}
            mode = ExecutionMode(options.get("mode", "strict"))
            timeout = options.get("timeout", 30000)
            checkpoint = options.get("checkpoint", False)
            continue_from = options.get("continue_from", None)
            
            # 解析NLPL程序
            program = self._parse_nlpl(nlpl)
            
            # 初始化执行上下文
            self.context = {
                "program": program,
                "state": copy.deepcopy(initial_state),
                "current_step": continue_from or self._get_first_step(program),
                "trace": [],
                "errors": [],
                "mode": mode,
                "timeout": timeout,
                "checkpoint": checkpoint
            }
            
            # 执行主循环
            self._execute_loop()
            
            # 构建返回结果
            result = self._build_result()
            
            return result
            
        except Exception as e:
            # 处理意外错误
            return {
                "success": False,
                "final_state": initial_state,
                "execution_trace": [],
                "errors": [{
                    "type": "SYSTEM_ERROR",
                    "message": str(e),
                    "step": "initialization"
                }],
                "statistics": {
                    "total_steps": 0,
                    "executed_steps": 0,
                    "success_steps": 0,
                    "failed_steps": 0,
                    "duration": 0
                }
            }
    
    def _parse_nlpl(self, nlpl: str) -> Dict[str, Any]:
        """解析NLPL程序"""
        # 简化的YAML风格解析
        lines = nlpl.strip().split('\n')
        program = {
            "name": "",
            "goal": "",
            "state": {},
            "steps": []
        }
        
        current_section = None
        current_step = None
        
        for line in lines:
            stripped = line.strip()
            
            # 识别程序名称
            if stripped.startswith("程序:"):
                program["name"] = stripped[3:].strip()
            
            # 识别目标
            elif stripped.startswith("目标:"):
                program["goal"] = stripped[3:].strip()
            
            # 识别状态section
            elif stripped == "状态:":
                current_section = "state"
            
            # 识别主流程section
            elif stripped.startswith("主流程:"):
                current_section = "steps"
            
            # 识别步骤
            elif current_section == "steps" and stripped.startswith("步骤"):
                if ":" in stripped:
                    step_name = stripped.split(":")[0].strip()
                    current_step = {
                        "name": step_name,
                        "actions": [],
                        "conditions": []
                    }
                    program["steps"].append(current_step)
            
            # 识别动作
            elif current_step and stripped.startswith("动作:"):
                action = stripped[3:].strip()
                current_step["actions"].append(action)
            
            # 识别条件
            elif current_step and stripped.startswith("条件:"):
                condition = stripped[3:].strip()
                current_step["conditions"].append(condition)
        
        return program
    
    def _get_first_step(self, program: Dict[str, Any]) -> Optional[str]:
        """获取第一个步骤"""
        if program["steps"]:
            return program["steps"][0]["name"]
        return None
    
    def _execute_loop(self):
        """执行主循环"""
        max_iterations = 1000  # 防止无限循环
        iteration = 0
        
        while not self._is_complete() and iteration < max_iterations:
            iteration += 1
            
            # 检查超时
            if self._is_timeout():
                self._handle_timeout()
                break
            
            # 获取当前步骤
            current_step = self._get_current_step()
            if not current_step:
                break
            
            # 执行步骤
            self._execute_step(current_step)
            
            # 创建检查点
            if self.context["checkpoint"]:
                self._create_checkpoint()
            
            # 移动到下一步
            self._move_to_next_step()
    
    def _is_complete(self) -> bool:
        """检查是否完成"""
        # 检查状态中的完成标志
        state = self.context["state"]
        if isinstance(state, dict) and state.get("完成", False):
            return True
        
        # 检查是否还有步骤
        return self.context["current_step"] is None
    
    def _is_timeout(self) -> bool:
        """检查是否超时"""
        if not self.start_time:
            return False
        
        elapsed = (time.time() - self.start_time) * 1000  # 转换为毫秒
        return elapsed > self.context["timeout"]
    
    def _handle_timeout(self):
        """处理超时"""
        self.context["errors"].append({
            "type": "TIMEOUT_ERROR",
            "message": f"执行超时（>{self.context['timeout']}ms）",
            "step": self.context["current_step"]
        })
    
    def _get_current_step(self) -> Optional[Dict[str, Any]]:
        """获取当前步骤"""
        step_name = self.context["current_step"]
        if not step_name:
            return None
        
        for step in self.context["program"]["steps"]:
            if step["name"] == step_name:
                return step
        
        return None
    
    def _execute_step(self, step: Dict[str, Any]):
        """执行单个步骤"""
        step_name = step["name"]
        
        # 记录开始
        trace_entry = {
            "step": step_name,
            "status": StepStatus.RUNNING.value,
            "start_time": datetime.now().isoformat(),
            "state_before": copy.deepcopy(self.context["state"])
        }
        
        try:
            # 检查前置条件
            if not self._check_conditions(step):
                trace_entry["status"] = StepStatus.SKIPPED.value
                trace_entry["reason"] = "条件不满足"
            else:
                # 执行动作
                for action in step.get("actions", []):
                    self._execute_action(action)
                
                trace_entry["status"] = StepStatus.SUCCESS.value
            
        except Exception as e:
            # 处理执行错误
            trace_entry["status"] = StepStatus.FAILED.value
            trace_entry["error"] = str(e)
            
            self.context["errors"].append({
                "type": "STEP_ERROR",
                "message": str(e),
                "step": step_name
            })
            
            # 严格模式下停止执行
            if self.context["mode"] == ExecutionMode.STRICT:
                self.context["current_step"] = None
        
        finally:
            # 记录结束
            trace_entry["end_time"] = datetime.now().isoformat()
            trace_entry["state_after"] = copy.deepcopy(self.context["state"])
            self.context["trace"].append(trace_entry)
    
    def _check_conditions(self, step: Dict[str, Any]) -> bool:
        """检查步骤的前置条件"""
        conditions = step.get("conditions", [])
        if not conditions:
            return True
        
        # 简化实现：所有条件都满足才返回True
        for condition in conditions:
            if not self._evaluate_condition(condition):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: str) -> bool:
        """评估条件"""
        # 简化实现：检查状态中的某些值
        state = self.context["state"]
        
        # 处理简单的条件
        if "存在" in condition:
            # 检查某个字段是否存在
            return True
        elif ">" in condition or "<" in condition:
            # 数值比较
            return True
        else:
            # 默认为真
            return True
    
    def _execute_action(self, action: str):
        """执行动作"""
        # 简化实现：模拟不同类型的动作
        state = self.context["state"]
        
        if "计算" in action:
            # 模拟计算
            if isinstance(state, dict):
                if "处理" not in state:
                    state["处理"] = {}
                state["处理"]["计算结果"] = "已计算"
        
        elif "保存" in action:
            # 模拟保存
            if isinstance(state, dict):
                if "输出" not in state:
                    state["输出"] = {}
                state["输出"]["已保存"] = True
        
        elif "设置" in action:
            # 设置状态值
            if "完成" in action and isinstance(state, dict):
                state["完成"] = True
        
        else:
            # 通用动作
            pass
    
    def _move_to_next_step(self):
        """移动到下一个步骤"""
        current_step_name = self.context["current_step"]
        steps = self.context["program"]["steps"]
        
        # 找到当前步骤的索引
        current_index = -1
        for i, step in enumerate(steps):
            if step["name"] == current_step_name:
                current_index = i
                break
        
        # 移动到下一个步骤
        if current_index >= 0 and current_index < len(steps) - 1:
            self.context["current_step"] = steps[current_index + 1]["name"]
        else:
            self.context["current_step"] = None
    
    def _create_checkpoint(self):
        """创建检查点"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "step": self.context["current_step"],
            "state": copy.deepcopy(self.context["state"]),
            "trace_length": len(self.context["trace"])
        }
        
        self.checkpoints.append(checkpoint)
        
        # 限制检查点数量
        if len(self.checkpoints) > 10:
            self.checkpoints = self.checkpoints[-10:]
    
    def _build_result(self) -> Dict[str, Any]:
        """构建执行结果"""
        # 计算统计信息
        total_steps = len(self.context["program"]["steps"])
        executed_steps = len(self.context["trace"])
        success_steps = sum(1 for t in self.context["trace"] 
                          if t["status"] == StepStatus.SUCCESS.value)
        failed_steps = sum(1 for t in self.context["trace"]
                         if t["status"] == StepStatus.FAILED.value)
        
        duration = 0
        if self.start_time:
            duration = int((time.time() - self.start_time) * 1000)
        
        return {
            "success": len(self.context["errors"]) == 0,
            "final_state": self.context["state"],
            "execution_trace": self.context["trace"],
            "errors": self.context["errors"],
            "statistics": {
                "total_steps": total_steps,
                "executed_steps": executed_steps,
                "success_steps": success_steps,
                "failed_steps": failed_steps,
                "duration": duration,
                "state_changes": executed_steps  # 简化：每步都改变状态
            }
        }
    
    def restore_from_checkpoint(self, checkpoint_index: int = -1) -> bool:
        """从检查点恢复"""
        if not self.checkpoints:
            return False
        
        checkpoint = self.checkpoints[checkpoint_index]
        self.context["state"] = copy.deepcopy(checkpoint["state"])
        self.context["current_step"] = checkpoint["step"]
        
        # 截断执行轨迹
        self.context["trace"] = self.context["trace"][:checkpoint["trace_length"]]
        
        return True


# 创建全局执行器实例（作为工具）
executor_tool = NLPLExecutor()


def get_executor_tool() -> NLPLExecutor:
    """获取执行器工具实例"""
    return executor_tool


if __name__ == "__main__":
    # 测试执行器
    executor = NLPLExecutor()
    
    # 测试NLPL程序
    test_nlpl = """程序: 测试程序
  目标: 测试执行器功能
  
  状态:
    输入: 测试数据
    处理: {}
    输出: null
    完成: false
    
  主流程:
    步骤1_初始化:
      动作: 初始化环境
      
    步骤2_处理:
      动作: 执行计算
      条件: 输入存在
      
    步骤3_保存:
      动作: 保存结果
      
    步骤4_完成:
      动作: 设置完成标志
      设置: 状态.完成 = true
"""
    
    # 测试状态
    test_state = {
        "输入": "测试数据",
        "处理": {},
        "输出": None,
        "完成": False
    }
    
    # 执行测试
    print("执行NLPL程序...")
    result = executor.execute(
        nlpl=test_nlpl,
        initial_state=test_state,
        options={
            "mode": "strict",
            "timeout": 5000,
            "checkpoint": True
        }
    )
    
    # 打印结果
    print(f"\n执行{'成功' if result['success'] else '失败'}")
    print(f"\n统计信息:")
    for key, value in result["statistics"].items():
        print(f"  {key}: {value}")
    
    print(f"\n最终状态:")
    print(json.dumps(result["final_state"], ensure_ascii=False, indent=2))
    
    if result["errors"]:
        print(f"\n错误列表:")
        for error in result["errors"]:
            print(f"  - {error['type']}: {error['message']}")