"""
Context栈实现 - 支持函数调用树的图灵完备性
解决ExecutionContext只能单层的问题，实现真正的函数调用栈
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ExecutionContext:
    """单个执行上下文"""
    context_id: str
    goal: str
    parent_id: Optional[str] = None
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def add_tasks(self, tasks: List[str]) -> None:
        """添加任务列表"""
        for task in tasks:
            self.tasks.append({
                'name': task,
                'status': 'pending',
                'started_at': None,
                'completed_at': None,
                'result': None
            })

    def start_task(self, task_name: str) -> bool:
        """开始执行任务"""
        for task in self.tasks:
            if task['name'] == task_name and task['status'] == 'pending':
                task['status'] = 'in_progress'
                task['started_at'] = datetime.now().isoformat()
                return True
        return False

    def complete_task(self, task_name: str, result: str = None) -> bool:
        """完成任务"""
        for task in self.tasks:
            if task['name'] == task_name and task['status'] == 'in_progress':
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                task['result'] = result
                return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """获取Context状态"""
        pending = sum(1 for t in self.tasks if t['status'] == 'pending')
        in_progress = sum(1 for t in self.tasks if t['status'] == 'in_progress')
        completed = sum(1 for t in self.tasks if t['status'] == 'completed')

        return {
            'context_id': self.context_id,
            'goal': self.goal,
            'parent_id': self.parent_id,
            'total_tasks': len(self.tasks),
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'is_complete': pending == 0 and in_progress == 0,
            'data': self.data
        }


class ContextStack:
    """
    Context栈 - 管理函数调用树

    核心功能：
    1. push() - 进入新函数，创建子Context
    2. pop() - 函数返回，恢复父Context
    3. current - 当前活跃的Context

    这是实现图灵完备的关键组件
    """

    def __init__(self):
        self.stack: List[ExecutionContext] = []
        self.all_contexts: Dict[str, ExecutionContext] = {}  # 保存所有Context历史
        self._context_counter = 0

    def _generate_id(self) -> str:
        """生成唯一的Context ID"""
        self._context_counter += 1
        return f"ctx_{self._context_counter:04d}"

    @property
    def current(self) -> Optional[ExecutionContext]:
        """获取当前Context"""
        return self.stack[-1] if self.stack else None

    @property
    def depth(self) -> int:
        """获取栈深度"""
        return len(self.stack)

    def push(self, goal: str) -> ExecutionContext:
        """
        进入新函数调用，压入新Context

        Args:
            goal: 新函数的目标

        Returns:
            新创建的Context
        """
        context_id = self._generate_id()
        parent_id = self.current.context_id if self.current else None

        new_context = ExecutionContext(
            context_id=context_id,
            goal=goal,
            parent_id=parent_id
        )

        self.stack.append(new_context)
        self.all_contexts[context_id] = new_context

        return new_context

    def pop(self) -> Optional[ExecutionContext]:
        """
        函数返回，弹出当前Context

        Returns:
            被弹出的Context（已完成）
        """
        if not self.stack:
            return None

        completed_context = self.stack.pop()
        completed_context.completed_at = datetime.now().isoformat()

        return completed_context

    def peek(self, offset: int = 0) -> Optional[ExecutionContext]:
        """
        查看栈中的Context（不弹出）

        Args:
            offset: 0表示当前，-1表示父级，-2表示祖父级...

        Returns:
            指定位置的Context
        """
        if not self.stack:
            return None

        index = -(offset + 1) if offset >= 0 else offset

        if abs(index) > len(self.stack):
            return None

        return self.stack[index]

    def get_context_by_id(self, context_id: str) -> Optional[ExecutionContext]:
        """通过ID获取Context（历史记录）"""
        return self.all_contexts.get(context_id)

    def get_call_stack(self) -> List[str]:
        """
        获取当前调用栈（用于调试）

        Returns:
            从根到当前的函数调用链
        """
        return [ctx.goal for ctx in self.stack]

    def get_tree(self) -> Dict[str, Any]:
        """
        获取完整的调用树

        Returns:
            树形结构的调用历史
        """
        def build_tree(context_id: Optional[str]) -> Dict[str, Any]:
            if not context_id:
                # 找到所有根节点
                roots = [ctx for ctx in self.all_contexts.values() if ctx.parent_id is None]
                return {
                    'children': [build_tree(root.context_id) for root in roots]
                }

            context = self.all_contexts[context_id]
            children = [ctx for ctx in self.all_contexts.values() if ctx.parent_id == context_id]

            return {
                'context_id': context.context_id,
                'goal': context.goal,
                'status': context.get_status(),
                'children': [build_tree(child.context_id) for child in children]
            }

        return build_tree(None)

    def save_state(self) -> str:
        """
        保存栈状态（用于持久化）

        Returns:
            JSON格式的状态字符串
        """
        state = {
            'stack': [ctx.context_id for ctx in self.stack],
            'contexts': {
                cid: {
                    'context_id': ctx.context_id,
                    'goal': ctx.goal,
                    'parent_id': ctx.parent_id,
                    'tasks': ctx.tasks,
                    'data': ctx.data,
                    'created_at': ctx.created_at,
                    'completed_at': ctx.completed_at
                }
                for cid, ctx in self.all_contexts.items()
            },
            'counter': self._context_counter
        }
        return json.dumps(state, indent=2, ensure_ascii=False)

    def load_state(self, state_json: str) -> None:
        """
        恢复栈状态

        Args:
            state_json: save_state()保存的JSON字符串
        """
        state = json.loads(state_json)

        # 重建所有Context
        self.all_contexts = {}
        for cid, ctx_data in state['contexts'].items():
            ctx = ExecutionContext(
                context_id=ctx_data['context_id'],
                goal=ctx_data['goal'],
                parent_id=ctx_data['parent_id']
            )
            ctx.tasks = ctx_data['tasks']
            ctx.data = ctx_data['data']
            ctx.created_at = ctx_data['created_at']
            ctx.completed_at = ctx_data['completed_at']
            self.all_contexts[cid] = ctx

        # 重建栈
        self.stack = [self.all_contexts[cid] for cid in state['stack']]
        self._context_counter = state['counter']

    def clear(self) -> None:
        """清空栈"""
        self.stack.clear()
        self.all_contexts.clear()
        self._context_counter = 0


# 全局Context栈实例（单例模式）
_global_stack = None

def get_context_stack() -> ContextStack:
    """获取全局Context栈实例"""
    global _global_stack
    if _global_stack is None:
        _global_stack = ContextStack()
    return _global_stack


def reset_context_stack() -> None:
    """重置全局Context栈"""
    global _global_stack
    _global_stack = ContextStack()


# 便捷函数（供Agent直接调用）
def push_context(goal: str) -> Dict[str, Any]:
    """进入新函数"""
    stack = get_context_stack()
    ctx = stack.push(goal)
    return {
        'status': 'success',
        'context_id': ctx.context_id,
        'depth': stack.depth,
        'message': f'进入Context: {goal}'
    }


def pop_context() -> Dict[str, Any]:
    """退出当前函数"""
    stack = get_context_stack()
    ctx = stack.pop()
    if ctx:
        return {
            'status': 'success',
            'context_id': ctx.context_id,
            'goal': ctx.goal,
            'message': f'退出Context: {ctx.goal}'
        }
    else:
        return {
            'status': 'error',
            'message': '栈为空，无法弹出'
        }


def current_context() -> Dict[str, Any]:
    """获取当前Context信息"""
    stack = get_context_stack()
    ctx = stack.current
    if ctx:
        return {
            'status': 'success',
            'context': ctx.get_status(),
            'call_stack': stack.get_call_stack()
        }
    else:
        return {
            'status': 'error',
            'message': '栈为空'
        }