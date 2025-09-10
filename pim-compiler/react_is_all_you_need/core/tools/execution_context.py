#!/usr/bin/env python3
"""
ExecutionContext - 简化的任务记录本

提供任务列表、状态管理和数据存储功能。
执行顺序和控制流由Agent决定，工具只负责记录。
"""

import os
import sys
import json
from typing import List, Optional, Dict, Any

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool_base import Function


class ExecutionContext(Function):
    """ExecutionContext - 任务记录本
    
    核心功能：
    - 任务记录：记录任务列表和执行状态
    - 状态管理：当前状态的语义化描述
    - 数据存储：通用KV存储提供灵活空间
    
    注意：这只是记录工具，不负责调度。执行顺序和依赖关系由Agent自主决定。
    """
    
    def __init__(self):
        super().__init__(
            name="context",
            description="内存中的任务记录本：记录项目目标、任务列表、当前状态和数据（不持久化）",
            parameters={
                "action": {
                    "type": "string",
                    "enum": [
                        # 项目管理（极简）
                        "init_project",      # 初始化项目
                        "add_tasks",         # 批量添加任务
                        "remove_tasks",      # 批量删除任务
                        "start_task",        # 开始任务
                        "complete_task",     # 完成任务
                        "fail_task",         # 任务失败
                        
                        # 状态管理（语义化）
                        "set_state",         # 设置当前状态
                        "get_state",         # 获取当前状态
                        
                        # 通用KV存储（自由空间）
                        "set_data",          # 存储任意数据
                        "get_data",          # 读取数据
                        "delete_data",       # 删除数据
                        
                        # 全局查询
                        "get_context",       # 获取完整上下文
                    ],
                    "description": "操作类型。init_project:初始化新项目；add_tasks:添加任务列表；start_task:标记任务开始；complete_task:标记任务完成；fail_task:标记任务失败；set_state:设置语义化状态描述；set_data:存储数据(key-value)；get_context:查看全部上下文"
                },
                
                # 项目管理参数
                "goal": {
                    "type": "string",
                    "description": "项目的总体目标描述，如'生成完整的博客系统'、'修复所有测试错误'等。应该是一句话的概括"
                },
                "tasks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "任务名称列表，每个任务用动词开头，如['清空工作目录', '生成PSM文档', '创建数据模型']"
                },
                "task": {
                    "type": "string",
                    "description": "具体任务名称，应与tasks列表中的名称一致，如'生成PSM文档'"
                },
                "result": {
                    "type": "string",
                    "description": "任务执行结果的描述，如'成功生成10个文件'、'发现3个错误需要修复'等"
                },
                
                # 状态管理参数
                "state": {
                    "type": "string",
                    "description": "语义化的状态描述，如'正在生成PSM文档'、'等待用户确认'、'调试测试失败问题'等。避免使用数字或代码"
                },
                
                # KV存储参数
                "key": {
                    "type": "string",
                    "description": "数据键名，使用有意义的名称如'pim_content'、'test_results'、'error_log'等"
                },
                "value": {
                    "type": ["string", "object", "array", "number", "boolean"],
                    "description": "存储的数据值。当key为'当前状态'时，必须使用描述性字符串如'正在处理第3个文件'，而不是数字'3'"
                }
            }
        )
        
        # 只在内存中维护状态，不需要文件持久化
        self.project = {
            "goal": None,
            "tasks": {},  # {task_name: {status, result}}
            "current_state": None,
            "data": {}  # 自由KV存储
        }
    
    def execute(self, **kwargs) -> str:
        """执行操作"""
        action = kwargs.get('action')
        
        # 项目管理操作
        if action == 'init_project':
            return self._init_project(kwargs.get('goal'))
        elif action == 'add_tasks':
            return self._add_tasks(kwargs.get('tasks', []))
        elif action == 'remove_tasks':
            return self._remove_tasks(kwargs.get('tasks', []))
        elif action == 'start_task':
            return self._start_task(kwargs.get('task'))
        elif action == 'complete_task':
            return self._complete_task(kwargs.get('task'), kwargs.get('result'))
        elif action == 'fail_task':
            return self._fail_task(kwargs.get('task'), kwargs.get('result'))
        
        # 状态管理操作
        elif action == 'set_state':
            return self._set_state(kwargs.get('state'))
        elif action == 'get_state':
            return self._get_state()
        
        # KV存储操作
        elif action == 'set_data':
            return self._set_data(kwargs.get('key'), kwargs.get('value'))
        elif action == 'get_data':
            return self._get_data(kwargs.get('key'))
        elif action == 'delete_data':
            return self._delete_data(kwargs.get('key'))
        
        # 全局查询
        elif action == 'get_context':
            return self._get_context()
        else:
            return f"未知操作: {action}"
    
    # ========== 项目管理方法 ==========
    
    def _init_project(self, goal: str) -> str:
        """初始化项目"""
        self.project["goal"] = goal
        self.project["tasks"] = {}
        self.project["current_state"] = "项目已初始化"
        self.project["data"] = {}
        return f"✅ 项目已初始化: {goal}"
    
    def _add_tasks(self, tasks: List[str]) -> str:
        """批量添加任务"""
        added = 0
        for task in tasks:
            if task and task not in self.project["tasks"]:
                self.project["tasks"][task] = {
                    "status": "pending",
                    "result": None
                }
                added += 1
        
        return f"✅ 添加了 {added} 个任务"
    
    def _remove_tasks(self, tasks: List[str]) -> str:
        """批量删除任务"""
        removed = 0
        for task in tasks:
            if task in self.project["tasks"]:
                del self.project["tasks"][task]
                removed += 1
        
        return f"✅ 删除了 {removed} 个任务"
    
    def _start_task(self, task: str) -> str:
        """开始执行任务"""
        if task not in self.project["tasks"]:
            return f"❌ 任务不存在: {task}"
        
        self.project["tasks"][task]["status"] = "in_progress"
        return f"✅ 任务 {task} 标记为执行中"
    
    def _complete_task(self, task: str, result: str = None) -> str:
        """完成任务"""
        if task not in self.project["tasks"]:
            return f"❌ 任务不存在: {task}"
        
        self.project["tasks"][task]["status"] = "completed"
        if result:
            self.project["tasks"][task]["result"] = result
        
        return f"✅ 任务 {task} 已完成"
    
    def _fail_task(self, task: str, result: str = None) -> str:
        """标记任务失败"""
        if task not in self.project["tasks"]:
            return f"❌ 任务不存在: {task}"
        
        self.project["tasks"][task]["status"] = "failed"
        if result:
            self.project["tasks"][task]["result"] = result
        
        return f"✅ 任务 {task} 标记为失败"
    
    # ========== 状态管理方法 ==========
    
    def _set_state(self, state: str) -> str:
        """设置当前状态"""
        self.project["current_state"] = state
        return f"✅ 已设置 当前状态 = {state}"
    
    def _get_state(self) -> str:
        """获取当前状态"""
        state = self.project.get("current_state", "未设置状态")
        return f"当前状态: {state}"
    
    # ========== KV存储方法 ==========
    
    def _set_data(self, key: str, value: Any) -> str:
        """存储数据"""
        if not key:
            return "❌ 需要提供key"
        
        self.project["data"][key] = value
        return f"✅ 已设置 {key} = {value}"
    
    def _get_data(self, key: str) -> str:
        """读取数据"""
        if not key:
            return "❌ 需要提供key"
        
        if key in self.project["data"]:
            value = self.project["data"][key]
            return f"{key}: {value}"
        else:
            return f"❌ 未找到key: {key}"
    
    def _delete_data(self, key: str) -> str:
        """删除数据"""
        if key in self.project["data"]:
            del self.project["data"][key]
            return f"✅ 已删除 {key}"
        else:
            return f"❌ 未找到key: {key}"
    
    # ========== 全局查询 ==========
    
    def _get_context(self) -> str:
        """获取完整执行上下文"""
        context = {
            "目标": self.project.get("goal", "未设置"),
            "当前状态": self.project.get("current_state", "未设置"),
            "任务统计": self._get_task_stats(),
            "任务详情": self._format_tasks(),
            "数据存储": self.project.get("data", {})
        }
        
        return json.dumps(context, ensure_ascii=False, indent=2)
    
    def _get_task_stats(self) -> Dict[str, int]:
        """获取任务统计"""
        stats = {
            "总计": len(self.project["tasks"]),
            "待办": 0,
            "进行中": 0,
            "已完成": 0,
            "失败": 0
        }
        
        for task_info in self.project["tasks"].values():
            status = task_info["status"]
            if status == "pending":
                stats["待办"] += 1
            elif status == "in_progress":
                stats["进行中"] += 1
            elif status == "completed":
                stats["已完成"] += 1
            elif status == "failed":
                stats["失败"] += 1
        
        return stats
    
    def _format_tasks(self) -> List[str]:
        """格式化任务列表"""
        formatted = []
        for task_name, task_info in self.project["tasks"].items():
            status_icon = {
                "pending": "⏸",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌"
            }.get(task_info["status"], "❓")
            
            task_str = f"{status_icon} {task_name}"
            
            if task_info["result"]:
                task_str += f" → {task_info['result']}"
            
            formatted.append(task_str)
        
        return formatted
    
    # ========== 辅助方法 ==========
    
    # 不再需要文件I/O操作
    # ExecutionContext只在内存中维护状态