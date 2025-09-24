#!/usr/bin/env python3
"""
JSON条件反射拦截器
在interceptor层实现条件反射，无需LLM
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Optional

class JSONReflexInterceptor:
    """JSON输入的条件反射处理"""

    def __init__(self, agent):
        """
        初始化拦截器
        agent: ReactAgentMinimal实例
        """
        self.agent = agent
        self.work_dir = agent.work_dir

    def __call__(self, task: str) -> Optional[str]:
        """
        拦截器主函数
        返回None表示继续正常流程，返回字符串表示直接返回结果
        """

        task = task.strip()

        # 1. 尝试JSON解析
        if not task.startswith('{'):
            return None  # 不是JSON，走正常流程

        try:
            data = json.loads(task)
        except:
            return None  # 解析失败，走正常流程

        # 2. 库存管理反射
        if 'action' in data and 'inventory' in data.get('action', ''):
            return self._handle_inventory(data)

        # 3. 数据查询反射
        if 'query' in data and 'table' in data:
            return self._handle_query(data)

        # 4. 计算反射
        if 'calc' in data:
            return self._handle_calc(data)

        # 5. 工具调用反射
        if 'tool' in data and 'params' in data:
            return self._handle_tool_call(data)

        # 没有匹配的模式，走正常流程
        return None

    def _handle_inventory(self, data: dict) -> str:
        """处理库存相关的JSON命令"""

        # 查找inventory_tool.py
        tool_paths = [
            Path(self.work_dir) / "external_tools" / "inventory_tool.py",
            Path.home() / f".agent/{self.agent.name}" / "external_tools" / "inventory_tool.py",
            Path("/tmp") / "agent_creator_v2" / "inventory_tool.py"
        ]

        tool_path = None
        for path in tool_paths:
            if path.exists():
                tool_path = path
                break

        if not tool_path:
            return "❌ [条件反射] 未找到inventory_tool.py"

        # 构建命令
        cmd = ['python', str(tool_path)]

        action = data.get('action', '')
        if action == 'inventory_check':
            cmd.extend(['check', data.get('product_id', '')])
        elif action == 'inventory_list':
            cmd.append('list')
        elif action == 'inventory_update':
            cmd.extend(['update', data.get('product_id', ''), str(data.get('quantity', 0))])
        elif action == 'inventory_add':
            cmd.extend(['add', data.get('product_id', ''), data.get('name', ''),
                       str(data.get('quantity', 0)), str(data.get('threshold', 10))])
        else:
            return f"❌ [条件反射] 未知的inventory动作: {action}"

        # 执行命令
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            output = result.stdout or result.stderr
            return f"⚡ [条件反射-库存管理]\n{output}"
        except subprocess.TimeoutExpired:
            return "❌ [条件反射] 命令执行超时"
        except Exception as e:
            return f"❌ [条件反射] 执行失败: {e}"

    def _handle_query(self, data: dict) -> str:
        """处理数据查询"""
        table = data.get('table')
        conditions = data.get('where', {})

        # 这里可以直接查询数据库或文件
        # 示例实现
        return f"⚡ [条件反射-查询]\n查询表: {table}\n条件: {conditions}\n（需要实现具体查询逻辑）"

    def _handle_calc(self, data: dict) -> str:
        """处理计算请求"""
        expr = data.get('calc', '')

        try:
            # 安全计算 - 只允许基本数学运算
            allowed_names = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'len': len, 'pow': pow
            }
            result = eval(expr, {"__builtins__": {}}, allowed_names)
            return f"⚡ [条件反射-计算]\n{expr} = {result}"
        except Exception as e:
            return f"❌ [条件反射] 计算失败: {e}"

    def _handle_tool_call(self, data: dict) -> str:
        """直接调用工具"""
        tool_name = data.get('tool')
        params = data.get('params', {})

        # 查找对应的工具
        for tool in self.agent.tools:
            if tool.name == tool_name:
                try:
                    result = tool.execute(**params)
                    return f"⚡ [条件反射-工具调用]\n工具: {tool_name}\n结果: {result}"
                except Exception as e:
                    return f"❌ [条件反射] 工具调用失败: {e}"

        return f"❌ [条件反射] 未找到工具: {tool_name}"


def create_reflex_interceptor(agent):
    """工厂函数，创建条件反射拦截器"""
    return JSONReflexInterceptor(agent)


# 使用示例
"""
from core.react_agent_minimal import ReactAgentMinimal
from core.interceptors.json_reflex_interceptor import create_reflex_interceptor

# 创建agent
agent = ReactAgentMinimal(
    work_dir="my_project",
    model="x-ai/grok-code-fast-1",
    knowledge_files=["knowledge/my_knowledge.md"]
)

# 安装条件反射拦截器
agent.interceptor = create_reflex_interceptor(agent)

# 现在JSON输入会被条件反射处理
result = agent.run('{"action": "inventory_list"}')  # 直接执行，不经过LLM
result = agent.run('{"calc": "2+2*3"}')  # 直接计算，不经过LLM
result = agent.run('普通文本输入')  # 正常走LLM流程
"""