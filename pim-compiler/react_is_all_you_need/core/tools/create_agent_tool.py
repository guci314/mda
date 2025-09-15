#!/usr/bin/env python3
"""
创建Agent工具 - 创建Agent并将其作为工具添加到主Agent
Agent本身就是Function，可以直接调用
"""

import os
import sys
import time
from typing import List, Optional, Dict, Any
import json

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool_base import Function
from react_agent_minimal import ReactAgentMinimal


class CreateAgentTool(Function):
    """创建Agent工具 - 创建Agent并注册为可调用的工具"""
    
    def __init__(self, work_dir=".", parent_agent=None):
        super().__init__(
            name="create_agent",
            description="创建一个新的Agent作为工具，可以像普通工具一样调用",
            parameters={
                "model": {
                    "type": "string", 
                    "description": "使用的模型名称",
                    "default": "x-ai/grok-code-fast-1"
                },
                "knowledge_files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "知识文件列表",
                    "default": []
                },
                "max_iterations": {
                    "type": "number",
                    "description": "最大迭代次数",
                    "default": 100
                },
                "agent_type": {
                    "type": "string",
                    "description": "Agent类型标识（用于生成名称）",
                    "default": "worker"
                },
                "description": {
                    "type": "string",
                    "description": "Agent的功能描述",
                    "default": ""
                },
                "knowledge_str": {
                    "type": "string",
                    "description": "动态知识内容（直接传入的知识字符串）",
                    "default": ""
                },
                "inherit_tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要继承的工具名称列表（其他Agent的名称）",
                    "default": []
                }
            }
        )
        self.work_dir = work_dir
        self.parent_agent = parent_agent  # 父Agent引用
    
    def execute(self, **kwargs) -> str:
        """
        创建一个新的Agent并注册为工具
        
        返回:
            创建结果信息
        """
        # 提取参数
        model = kwargs.get('model', 'x-ai/grok-code-fast-1')  # 默认使用Grok
        knowledge_files = kwargs.get('knowledge_files', [])
        max_iterations = kwargs.get('max_iterations', 100)
        agent_type = kwargs.get('agent_type', 'worker')
        description = kwargs.get('description', '')
        knowledge_str = kwargs.get('knowledge_str', '')
        inherit_tools = kwargs.get('inherit_tools', [])
        
        try:
            # 根据模型获取API配置
            api_key, base_url = self._get_api_config(model)
            
            # 处理知识文件路径
            processed_knowledge_files = []
            for kf in knowledge_files:
                if '/' not in kf:
                    processed_knowledge_files.append(f'knowledge/{kf}')
                else:
                    processed_knowledge_files.append(kf)
            
            # 生成唯一的agent名称
            model_short = model.split('/')[-1].replace('-', '_')[:15]
            timestamp = int(time.time() * 1000) % 100000
            agent_name = f"{agent_type}_{model_short}_{timestamp}"
            
            # 设置描述
            if not description:
                model_display = model.split('/')[-1] if '/' in model else model
                description = f"{agent_type} Agent使用{model_display}模型"
            
            # 创建Agent实例（Agent本身就是Function）
            agent = ReactAgentMinimal(
                work_dir=self.work_dir,
                model=model,
                base_url=base_url,
                api_key=api_key,
                knowledge_files=processed_knowledge_files,
                max_rounds=max_iterations,
                name=agent_name,  # 使用name参数，会创建.notes/{agent_name}/目录
                description=description,  # Function的description
                parameters={
                    "task": {
                        "type": "string",
                        "description": "要执行的任务"
                    }
                }
            )
            
            # 如果提供了知识字符串，动态加载
            if knowledge_str:
                agent.load_knowledge_str(knowledge_str, f"{agent_type}_dynamic_knowledge")
            
            # 继承指定的工具（其他Agent）
            inherited_count = 0
            if inherit_tools and self.parent_agent:
                for tool_name in inherit_tools:
                    # 从父Agent的function_instances列表中查找
                    for tool in self.parent_agent.function_instances:
                        # 直接匹配工具名称
                        if tool.name == tool_name:
                            # 将找到的工具添加到新Agent
                            agent.add_function(tool)
                            inherited_count += 1
                            break
            
            # 如果有父Agent，直接将新Agent添加到父Agent的工具列表
            if self.parent_agent:
                self.parent_agent.append_tool(agent)
                
                inherit_msg = f"\n- 继承工具：{inherited_count}个" if inherited_count > 0 else ""
                return f"""Agent创建成功并已添加到工具列表！
- 名称：{agent_name}
- 模型：{model}
- 描述：{description}{inherit_msg}
- 用法：直接调用 {agent_name}(task="你的任务")
"""
            else:
                return f"""Agent创建成功！
- 名称：{agent_name}
- 模型：{model}
- 描述：{description}
- 注意：需要手动添加到工具列表才能使用
"""
            
        except Exception as e:
            return f"创建Agent失败: {str(e)}"
    
    def _get_api_config(self, model: str) -> tuple:
        """根据模型获取API配置"""
        # 如果模型包含/，说明是OpenRouter上的模型
        if "/" in model:
            api_key = os.getenv("OPENROUTER_API_KEY")
            base_url = "https://openrouter.ai/api/v1"
        else:
            # 直接连接到各个API
            if model.startswith("deepseek"):
                api_key = os.getenv("DEEPSEEK_API_KEY")
                base_url = "https://api.deepseek.com"
            elif model.startswith("kimi"):
                api_key = os.getenv("MOONSHOT_API_KEY")
                base_url = "https://api.moonshot.cn/v1"
            else:
                # 默认使用OpenRouter
                api_key = os.getenv("OPENROUTER_API_KEY")
                base_url = "https://openrouter.ai/api/v1"
        
        return api_key, base_url