#!/usr/bin/env python3
"""
删除Agent工具 - 从工具列表中移除Agent
"""

import os
import sys
from typing import Optional

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool_base import Function


class DeleteAgentTool(Function):
    """删除Agent工具 - 从工具列表中移除指定的Agent"""

    def __init__(self, parent_agent=None):
        super().__init__(
            name="delete_agent",
            description="删除一个已创建的Agent，从工具列表中移除",
            parameters={
                "agent_name": {
                    "type": "string",
                    "description": "要删除的Agent名称"
                }
            }
        )
        self.parent_agent = parent_agent  # 父Agent引用

    def execute(self, **kwargs) -> str:
        """
        删除指定的Agent

        返回:
            删除结果信息
        """
        agent_name = kwargs.get('agent_name')

        if not agent_name:
            return "错误：必须提供agent_name参数"

        if not self.parent_agent:
            return "错误：没有父Agent引用，无法删除工具"

        try:
            # 检查Agent是否存在
            if agent_name not in self.parent_agent.function_instances:
                return f"Agent '{agent_name}' 不存在于工具列表中"

            # 从工具列表中移除
            del self.parent_agent.function_instances[agent_name]

            # 清理相关资源（如果有）
            # 注意：这里只是从工具列表移除引用，Python的垃圾回收会处理实际的内存释放

            return f"""Agent删除成功！
- 已删除：{agent_name}
- 剩余工具数：{len(self.parent_agent.function_instances)}"""

        except Exception as e:
            return f"删除Agent失败: {str(e)}"