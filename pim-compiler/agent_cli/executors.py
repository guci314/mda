"""
LangChain Tool Executor
负责执行 LangChain 工具的执行器
"""
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
import json

from langchain.tools import StructuredTool
from agent_cli.tools import get_tool_by_name, get_all_tools, get_tools_description


logger = logging.getLogger(__name__)


@dataclass
class ToolExecutionResult:
    """工具执行结果"""
    success: bool
    output: str
    error: Optional[str] = None
    tool_name: Optional[str] = None


class LangChainToolExecutor:
    """
    LangChain 工具执行器
    负责管理和执行 LangChain 工具
    """
    
    def __init__(self):
        """初始化执行器"""
        self.tools = {tool.name: tool for tool in get_all_tools()}
        logger.info(f"Initialized LangChainToolExecutor with {len(self.tools)} tools")
    
    def _map_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        映射参数名称以匹配 LangChain 工具的期望
        
        Args:
            tool_name: 工具名称
            parameters: 原始参数
            
        Returns:
            映射后的参数
        """
        # 复制参数以避免修改原始数据
        mapped_params = parameters.copy()
        
        # 文件路径参数映射
        if tool_name in ["read_file", "write_file"]:
            if "file_path" in mapped_params:
                mapped_params["path"] = mapped_params.pop("file_path")
        
        # 目录路径参数映射
        if tool_name == "list_files":
            if "dir_path" in mapped_params:
                mapped_params["path"] = mapped_params.pop("dir_path")
        
        # Python REPL 参数映射
        if tool_name == "python_repl":
            # python_repl 工具期望 'code' 参数，但有时会传入 'input'
            if "input" in mapped_params and "code" not in mapped_params:
                mapped_params["code"] = mapped_params.pop("input")
            # 保持向后兼容性 - 如果传入的就是 'code'，不做修改
        
        logger.debug(f"Parameter mapping for {tool_name}: {parameters} -> {mapped_params}")
        return mapped_params
    
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> ToolExecutionResult:
        """
        执行指定的工具
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            ToolExecutionResult: 执行结果
        """
        try:
            # 获取工具
            tool = self.tools.get(tool_name)
            if not tool:
                return ToolExecutionResult(
                    success=False,
                    output="",
                    error=f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}",
                    tool_name=tool_name
                )
            
            # 映射参数
            mapped_parameters = self._map_parameters(tool_name, parameters)
            
            # 执行工具
            logger.info(f"Executing tool '{tool_name}' with parameters: {mapped_parameters}")
            result = tool.run(mapped_parameters)
            
            return ToolExecutionResult(
                success=True,
                output=result,
                error=None,
                tool_name=tool_name
            )
            
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            return ToolExecutionResult(
                success=False,
                output="",
                error=str(e),
                tool_name=tool_name
            )
    
    def get_available_tools(self) -> List[str]:
        """获取所有可用的工具名称"""
        return list(self.tools.keys())
    
    def get_tool_description(self, tool_name: str) -> Optional[str]:
        """获取工具的描述"""
        tool = self.tools.get(tool_name)
        return tool.description if tool else None
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具的参数 schema"""
        tool = self.tools.get(tool_name)
        if not tool or not hasattr(tool, 'args_schema'):
            return None
        
        # 转换 Pydantic schema 为字典
        schema = tool.args_schema.schema()
        return schema
    
    def get_all_tools_info(self) -> List[Dict[str, Any]]:
        """获取所有工具的详细信息"""
        tools_info = []
        for name, tool in self.tools.items():
            info = {
                "name": name,
                "description": tool.description,
            }
            
            # 添加参数 schema
            if hasattr(tool, 'args_schema'):
                info["parameters"] = tool.args_schema.schema()
            
            tools_info.append(info)
        
        return tools_info
    
    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[str]:
        """
        验证工具参数
        
        Returns:
            None if valid, error message if invalid
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Tool '{tool_name}' not found"
        
        if not hasattr(tool, 'args_schema'):
            return None  # 如果没有 schema，不验证
        
        try:
            # 使用 Pydantic 验证参数
            tool.args_schema(**parameters)
            return None
        except Exception as e:
            return f"Invalid parameters: {str(e)}"
    
    def format_tools_for_prompt(self) -> str:
        """格式化工具信息用于 LLM 提示"""
        lines = ["Available tools:"]
        
        for name, tool in self.tools.items():
            lines.append(f"\n{name}:")
            lines.append(f"  Description: {tool.description}")
            
            if hasattr(tool, 'args_schema'):
                schema = tool.args_schema.schema()
                properties = schema.get('properties', {})
                required = schema.get('required', [])
                
                lines.append("  Parameters:")
                for param_name, param_info in properties.items():
                    param_type = param_info.get('type', 'any')
                    param_desc = param_info.get('description', 'No description')
                    is_required = param_name in required
                    req_str = " (required)" if is_required else " (optional)"
                    
                    lines.append(f"    - {param_name}: {param_type}{req_str} - {param_desc}")
        
        return "\n".join(lines)